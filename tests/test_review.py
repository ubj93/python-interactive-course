"""Review scheduling and scratch sessions use isolated progress and curriculum."""
import copy
import datetime as dt
import io
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from course.catalog import load_catalog
from course.cli import build_parser
from course.practice import practice_summary
from course.progress import Progress
from course.review import queue_rows, queue_state, reflect_queue
from course.review_cli import command, reflection
from course.workspace import Workspace
from test_engine import TESTS, make_exercise

ROOT = Path(__file__).resolve().parent.parent
NOW = dt.datetime(2026, 3, 7, 17, tzinfo=dt.timezone.utc)


class TestReview(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "progress.json"
        self.p = Progress(self.path)

    def test_intervals_priority_and_manual_future_items(self):
        queue = reflect_queue(None, "1.1", "confident", "check bounds", now=NOW)
        self.assertEqual(queue["items"]["1.1"]["next_review"], "2026-03-10")
        queue = reflect_queue(queue, "1.2", "needs_review", "empty input", now=NOW)
        queue = reflect_queue(queue, "1.3", "needs_review", "later", interval=7, now=NOW)
        queue = reflect_queue(queue, "1.4", "confident", "month", interval=30, now=NOW)
        self.assertEqual(queue["items"]["1.2"]["next_review"], "2026-03-08")
        self.assertEqual(queue["items"]["1.3"]["next_review"], "2026-03-14")
        self.assertEqual(queue["items"]["1.4"]["next_review"], "2026-04-06")
        self.assertEqual([r["id"] for r in queue_rows(queue, "2026-03-11", due_only=True)], ["1.2", "1.1"])
        self.assertEqual(len(queue_rows(queue, "2026-03-07")), 4)
        self.assertEqual(queue_rows(queue, "2026-03-11", due_only=True, available={"1.1"})[0]["id"], "1.1")

    def test_invalid_fields_are_rejected_without_mutation_and_unknown_data_survives(self):
        queue = reflect_queue(None, "99.1", "needs_review", "unavailable exercise", now=NOW)
        queue["custom"] = ["preserve"]
        queue["items"]["99.1"]["custom"] = {"keep": True}
        before = copy.deepcopy(queue)
        for interval in [True, 0, 2, 365, "7"]:
            with self.assertRaises(ValueError):
                reflect_queue(queue, "1.1", "confident", "", interval=interval, now=NOW)
        for date in ["2026-02-30", "0000-01-01", "2026-3-7", None]:
            bad = copy.deepcopy(queue); bad["items"]["99.1"]["next_review"] = date
            with self.assertRaises(ValueError):
                queue_state(bad)
        self.assertEqual(queue, before)
        self.assertEqual(queue_state(queue), before)
        updated = reflect_queue(queue, "99.1", "confident", "new note", source="diagnostic", now=NOW)
        self.assertEqual(updated["items"]["99.1"]["sources"], ["exercise", "diagnostic"])
        self.assertEqual(updated["items"]["99.1"]["custom"], {"keep": True})

    def test_diagnostic_and_exercise_share_one_row_with_atomic_failure(self):
        self.p.data.update(xp=71, solved={"1.2": {"xp": 9}}, hints={"1.2": 2})
        self.p.reflect_exercise("1.2", "confident", "ordinary", now=NOW)
        state = self.p.start_diagnostic()
        self.p.reflect_diagnostic("1.2", "needs_review", "diagnostic edge case", state["id"])
        self.assertEqual(len(self.p.data["review_queue"]["items"]), 1)
        self.assertEqual(self.p.data["review_queue"]["items"]["1.2"]["sources"], ["exercise", "diagnostic"])
        self.assertEqual(self.p.data["diagnostic"]["reflections"]["1.2"]["confidence"], "needs_review")
        self.assertEqual((self.p.xp, self.p.data["solved"], self.p.data["hints"]), (71, {"1.2": {"xp": 9}}, {"1.2": 2}))
        before, disk = copy.deepcopy(self.p.data), self.path.read_bytes()
        with patch.object(self.p, "save", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self.p.reflect_diagnostic("1.2", "confident", "must not persist", state["id"])
        self.assertEqual(self.p.data, before)
        self.assertEqual(self.path.read_bytes(), disk)
        self.assertEqual(Progress(self.path).data, before)

    def test_new_resume_stale_results_and_archived_drafts(self):
        original = self.p.start_review(["1.1"])
        self.p.update_review("1.1", "draft", original["id"], code="first round")
        self.p.update_review("1.1", "attempt", original["id"], passed=True)
        self.assertEqual(self.p.start_review(["1.2"])["id"], original["id"])
        fresh = self.p.start_review(["1.1"], new=True)
        self.assertNotEqual(fresh["id"], original["id"])
        self.assertEqual(fresh["drafts"], {})
        before = copy.deepcopy(self.p.data)
        with self.assertRaises(ValueError):
            self.p.update_review("1.1", "attempt", original["id"], passed=True)
        self.assertEqual(self.p.data, before)
        self.assertEqual(self.p.data["review_history"][0]["drafts"]["1.1"], "first round")
        self.assertEqual(practice_summary(fresh)[0]["outcome"], "not_attempted")
        self.p.finish_review()
        self.assertIsNone(self.p.review_state())
        self.assertEqual(len(self.p.data["review_history"]), 2)

    def test_malformed_round_and_save_failure_keep_recoverable_work(self):
        self.p.data["review_session"] = {"unrecognized": "keep my data"}
        self.p.save()
        before = copy.deepcopy(self.p.data)
        with self.assertRaises(ValueError):
            self.p.start_review(["1.1"])
        with patch.object(self.p, "save", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self.p.start_review(["1.1"], new=True)
        self.assertEqual(self.p.data, before)
        state = self.p.start_review(["1.1"], new=True)
        self.assertEqual(self.p.data["review_history"][0], before["review_session"])
        before = copy.deepcopy(self.p.data)
        with patch.object(self.p, "save", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self.p.update_review("1.1", "reflect", state["id"], confidence="needs_review", note="note")
        self.assertEqual(self.p.data, before)

    def test_cli_real_grading_fresh_files_and_separate_outcomes(self):
        repo = self.root / "repo"
        ex = make_exercise(repo / "curriculum", "def f(x):\n    raise NotImplementedError\n", TESTS)
        workspace = Workspace(self.root / "answers", repository_root=repo)
        saved_answer = workspace.ensure(ex)
        saved_answer.write_text("def f(x):\n    return x + 1\n# my saved solution\n")
        self.p.record_run(ex, True)
        original_progress = copy.deepcopy(self.p.data)
        source = ex.exercise_file.read_bytes()
        app = SimpleNamespace(progress=self.p, workspace=workspace, catalog=load_catalog(repo / "curriculum"), lessons={}, print_result=lambda *a, **k: None)
        parser = build_parser()
        def invoke(*args):
            with patch("sys.stdout", new=io.StringIO()) as out:
                result = command(app, parser.parse_args(["review", *args]))
            return result, out.getvalue()
        invoke("new", "1.1")
        _, path = invoke("path")
        answer = Path(path.strip())
        self.assertEqual(answer.read_bytes(), source)
        self.assertNotEqual(answer, saved_answer)
        self.assertEqual(invoke("run")[0], 1)
        answer.write_text("def f(x):\n    return x + 1\n")
        self.assertEqual(invoke("run")[0], 0)
        sid = app.progress.review_state()["id"]
        app.progress = Progress(self.path)
        self.assertEqual(invoke("path")[1].strip(), str(answer))
        self.assertEqual(practice_summary(app.progress.review_state())[0]["outcome"], "passed")
        invoke("reflect", "--confidence", "needs-review", "--note", "empty input", "--interval", "7")
        self.assertEqual(app.progress.data["review_queue"]["items"]["1.1"]["interval_days"], 7)
        invoke("help")
        for field, value in original_progress.items():
            self.assertEqual(app.progress.data[field], value, field)
        invoke("new", "1.1")
        self.assertNotEqual(app.progress.review_state()["id"], sid)
        _, fresh = invoke("path")
        self.assertEqual(Path(fresh.strip()).read_bytes(), source)
        self.assertEqual(answer.read_text(), "def f(x):\n    return x + 1\n")
        self.assertIn("my saved solution", saved_answer.read_text())
        self.assertEqual(ex.exercise_file.read_bytes(), source)

    def test_queue_read_does_not_create_progress_or_hide_unavailable_entries(self):
        app = SimpleNamespace(progress=self.p, catalog=[], lessons={})
        args = build_parser().parse_args(["review"])
        with patch("sys.stdout", new=io.StringIO()):
            command(app, args)
        self.assertFalse(self.path.exists())
        self.p.reflect_exercise("99.1", "needs_review", "preserve")
        with patch("sys.stdout", new=io.StringIO()) as out:
            command(app, args)
        self.assertIn("unavailable exercise", out.getvalue())
        self.assertIn("99.1", self.p.data["review_queue"]["items"])

    def test_manual_interval_survives_resume_and_diagnostic_note_edits_keep_date(self):
        state = self.p.start_review(["1.2"])
        self.p.update_review("1.2", "reflect", state["id"], confidence="confident", note="first", interval=30)
        self.p = Progress(self.path)
        self.assertEqual(self.p.review_state()["reflections"]["1.2"]["interval_days"], 30)
        self.p.update_review("1.2", "reflect", state["id"], confidence="confident", note="edited")
        self.assertEqual(self.p.data["review_queue"]["items"]["1.2"]["interval_days"], 30)
        diagnostic = self.p.start_diagnostic()
        self.p.reflect_diagnostic("1.2", "confident", "diagnostic", diagnostic["id"])
        row = self.p.data["review_queue"]["items"]["1.2"]
        row["next_review"] = "2026-12-01"
        self.p.save()
        self.p.reflect_diagnostic("1.2", "confident", "edit only the note", diagnostic["id"])
        row = self.p.data["review_queue"]["items"]["1.2"]
        self.assertEqual((row["interval_days"], row["next_review"]), (30, "2026-12-01"))
        self.p.reflect_diagnostic("1.2", "needs_review", "confidence changed", diagnostic["id"])
        self.assertEqual(self.p.data["review_queue"]["items"]["1.2"]["interval_days"], 1)


@unittest.skipUnless(shutil.which("node"), "actual browser review checks require Node.js")
class TestBrowserReview(unittest.TestCase):
    def test_browser_queue_cross_client_dates_storage_failures_and_independent_attempts(self):
        payload = reflect_queue(None, "1.2", "needs_review", "cross-client note", now=NOW)
        for timezone in ("America/New_York", "Asia/Tokyo"):
            env = dict(os.environ, TZ=timezone)
            run = subprocess.run([shutil.which("node"), str(ROOT / "tests/web_review.js")], input=json.dumps(payload), text=True, capture_output=True, env=env)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            returned = json.loads(run.stdout)
            self.assertEqual(queue_state(returned), returned)
            self.assertEqual(returned["items"]["1.2"]["mistake_note"], "cross-client note")
