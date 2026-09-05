"""Independent diagnostic attempts, resumable work, and portable practice state."""
import copy
import datetime as dt
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from course.backup import backup, restore
from course.catalog import find_exercise, load_catalog
from course.cli import App, build_parser
from course.practice import DIAGNOSTIC_IDS, diagnostic_summary, new_practice, normalize_diagnostic, normalize_practice, update_practice
from course.progress import Progress
from course.timestamps import UTC
from course.workspace import Workspace

ROOT = Path(__file__).resolve().parent.parent
START = dt.datetime(2026, 9, 5, 12, tzinfo=UTC)


class PracticeStateTests(unittest.TestCase):
    def test_latest_attempt_and_reflection_are_separate_and_unknown_fields_roundtrip(self):
        state = new_practice(DIAGNOSTIC_IDS, "diagnostic", START)
        state["future_metadata"] = {"keep": [1, 2]}
        state = update_practice(state, "1.2", "attempt", passed=True, now=START)
        state = update_practice(state, "1.2", "reflect", confidence="needs_review", note="String methods", now=START)
        state = update_practice(state, "1.2", "attempt", passed=False, now=START + dt.timedelta(minutes=2))
        # An out-of-order imported attempt doesn't replace a later outcome.
        state = update_practice(state, "1.2", "attempt", passed=True, now=START + dt.timedelta(minutes=1))
        state = update_practice(state, "1.2", "help", now=START + dt.timedelta(minutes=3))
        state = update_practice(state, "1.2", "draft", code="draft\n", now=START)
        normalized = normalize_diagnostic(json.loads(json.dumps(state)))
        self.assertEqual(normalized, state)
        row = diagnostic_summary(state)[0]
        self.assertEqual((row["outcome"], row["attempts"], row["confidence"], row["help_used"]), ("not_passed", 3, "needs_review", True))
        self.assertEqual(diagnostic_summary(state)[1]["outcome"], "not_attempted")
        self.assertEqual(state["future_metadata"], {"keep": [1, 2]})
        self.assertEqual(normalize_practice(new_practice(["1.2"], "review", START))["kind"], "review")

    def test_invalid_known_metadata_is_rejected_without_mutation(self):
        state = new_practice(DIAGNOSTIC_IDS, "diagnostic", START)
        bad = [None, [], True, {}, {**state, "version": True}, {**state, "kind": []}, {**state, "id": "../outside"}, {**state, "id": "valid\n"},
               {**state, "ids": []}, {**state, "ids": [None]}, {**state, "ids": ["1.2"]},
               {**state, "started": "invalid"}, {**state, "started": "0001-01-01T00:00:00+23:59"}, {**state, "last_exercise": []},
               {**state, "attempts": [True]}, {**state, "attempts": [{"exercise_id": "1.2", "passed": 1, "at": state["started"]}]},
               {**state, "attempts": [{"exercise_id": "1.2", "passed": True, "at": "2026-01-01T12:00:00Z"}]},
               {**state, "reflections": {"1.2": {"confidence": [], "mistake_note": ""}}},
               {**state, "reflections": {"1.2": {"mistake_note": "x" * 501}}},
               {**state, "reflections": {"1.2": {"help_at": "bad"}}}, {**state, "drafts": {"1.2": 6}}]
        for value in bad:
            snapshot = copy.deepcopy(value)
            with self.subTest(value=value):
                self.assertIsNone(normalize_diagnostic(value))
                self.assertIsNone(diagnostic_summary(value))
                self.assertEqual(value, snapshot)
        with self.assertRaises(ValueError):
            update_practice(state, "1.2", "attempt", passed=True, now=START - dt.timedelta(seconds=1))
        self.assertEqual(state["attempts"], [])

    def test_utc_and_legacy_timestamps_are_normalized(self):
        state = new_practice(DIAGNOSTIC_IDS, "diagnostic", START)
        del state["last_exercise"]
        self.assertIsNone(normalize_diagnostic(state)["last_exercise"])
        state["started"] = "2026-09-05T08:00:00-04:00"
        state["attempts"] = [{"exercise_id": "1.2", "passed": False, "at": "2026-09-05T14:00:00+02:00"}]
        normalized = normalize_diagnostic(state)
        self.assertEqual(normalized["started"], "2026-09-05T12:00:00.000Z")
        self.assertEqual(normalized["attempts"][0]["at"], normalized["started"])

    @unittest.skipUnless(shutil.which("node"), "Node is only needed for browser regression tests")
    def test_python_browser_state_roundtrip_and_browser_guards(self):
        state = new_practice(DIAGNOSTIC_IDS, "diagnostic", START)
        state = update_practice(state, "1.2", "attempt", passed=True, now=START)
        state = update_practice(state, "1.2", "reflect", confidence="needs_review", note="Bash habits", now=START)
        state["unknown"] = {"keep": True}
        process = subprocess.run([shutil.which("node"), str(ROOT / "tests/web_practice.js")], input=json.dumps(state), capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        exported = json.loads(process.stdout)
        self.assertEqual(normalize_diagnostic(exported), exported)
        self.assertEqual(diagnostic_summary(exported)[1]["confidence"], "confident")
        self.assertEqual(exported["unknown"], state["unknown"])


class DiagnosticFlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.env = patch.dict(os.environ, {"COURSE_WORKSPACE": str(self.root / "workspace"), "COURSE_PROGRESS": str(self.root / "progress.json")})
        self.env.start(); self.addCleanup(self.env.stop)
        self.app = App()
        self.p = self.app.progress
        self.p.data.update(xp=123, solved={"1.2": {"xp": 12, "passed_at": "2026-01-01T00:00:00Z"}}, hints={"1.2": 2}, cards={"1.2:1": {"done": True}})
        self.p.save()
        self.lifetime = copy.deepcopy(self.p.data)

    def command(self, *args):
        output = io.StringIO()
        with patch("sys.stdout", output):
            code = self.app.cmd_diagnostic(build_parser().parse_args(["diagnostic", *args]))
        return code, output.getvalue()

    def assert_lifetime_preserved(self):
        current = Progress(self.p.path).data
        self.assertEqual({key: value for key, value in current.items() if not key.startswith("diagnostic")}, self.lifetime)

    def test_cli_fresh_work_multiple_attempts_help_reflections_reload_and_new(self):
        ex = find_exercise(self.app.catalog, "1.2")
        answer = self.app.workspace.ensure(ex)
        answer.write_text("# ordinary saved answer\n")
        curriculum = ex.exercise_file.read_bytes()
        self.command()
        state = self.p.diagnostic_state()
        self.assertEqual(diagnostic_summary(state)[0]["outcome"], "not_attempted")
        _, output = self.command("path", "1.2")
        work = Path(output.strip())
        self.assertEqual(work.read_bytes(), self.app.workspace.starter(ex))
        self.assertNotEqual(work, answer)
        self.assertEqual(self.command("run", "1.2")[0], 1)
        work.write_bytes(ex.solution_file.read_bytes())
        self.assertEqual(self.command("run", "1.2")[0], 0)
        self.assertEqual(self.command("run", "1.2")[0], 0)
        self.command("help", "1.2")
        self.command("reflect", "1.2", "--confidence", "needs-review", "--note", "Remember to strip first")
        self.app = App()
        _, output = self.command()
        self.assertIn("1.2 Normalize a hostname · passed · 3 attempt(s)", output)
        self.assertIn("needs review", output)
        self.assertIn("course learn 1.2", output)
        self.assertIn("Remember to strip first", output)
        state = self.app.progress.diagnostic_state()
        self.assertEqual(state["drafts"]["1.2"], work.read_text())
        self.command("new")
        self.assertEqual(self.app.progress.data["diagnostic_history"][-1], state)
        self.assertEqual(diagnostic_summary(self.app.progress.diagnostic_state())[0]["outcome"], "not_attempted")
        _, output = self.command("path", "1.2")
        self.assertNotEqual(Path(output.strip()), work)
        self.assertEqual(work.read_bytes(), ex.solution_file.read_bytes())
        self.assertEqual(answer.read_text(), "# ordinary saved answer\n")
        self.assertEqual(ex.exercise_file.read_bytes(), curriculum)
        self.assert_lifetime_preserved()

    def test_imported_draft_is_initialized_once_and_backed_up_with_earlier_round(self):
        state = self.p.start_diagnostic()
        self.p.update_diagnostic("1.2", "draft", state["id"], code="# imported browser draft\n")
        _, output = self.command("path", "1.2")
        work = Path(output.strip()); self.assertEqual(work.read_text(), "# imported browser draft\n")
        work.write_text("# newer unsent CLI work\n")
        self.command("path", "1.2")
        self.assertEqual(work.read_text(), "# newer unsent CLI work\n")
        self.command("new"); self.command("path", "1.2")
        archive, count, has_progress = backup(self.app.catalog, self.p.path, self.root / "copy.zip", workspace=self.app.workspace)
        self.assertEqual(count, 2); self.assertTrue(has_progress)
        restored = Workspace(self.root / "restored")
        progress = self.root / "restored.json"
        result = restore(archive, progress, catalog=self.app.catalog, workspace=restored)
        self.assertEqual(len(result["exercises"]), 2)
        self.assertEqual(restored.practice_path(find_exercise(self.app.catalog, "1.2"), state["id"]).read_text(), "# newer unsent CLI work\n")
        self.assertEqual(Progress(progress).data, self.p.data)

    def test_invalid_import_and_failed_save_and_stale_result_preserve_original(self):
        self.p.data["diagnostic"] = {"id": "../../escape", "drafts": {"1.2": "keep"}}
        self.p.save(); before = copy.deepcopy(self.p.data)
        with self.assertRaises(ValueError):
            self.command()
        self.assertEqual(self.p.data, before)
        state = self.p.start_diagnostic(new=True)
        self.assertEqual(self.p.data["diagnostic_history"], [before["diagnostic"]])
        before = copy.deepcopy(self.p.data)
        with patch.object(self.p, "save", side_effect=OSError("full")), self.assertRaises(OSError):
            self.p.record_diagnostic_attempt("1.2", True, state["id"])
        self.assertEqual(self.p.data, before)
        self.p.start_diagnostic(new=True)
        newer = copy.deepcopy(self.p.data)
        with self.assertRaises(ValueError):
            self.p.record_diagnostic_attempt("1.2", True, state["id"])
        self.assertEqual(self.p.data, newer)
        self.assert_lifetime_preserved()

    def test_run_rechecks_disk_session_and_empty_catalog_never_creates_a_round(self):
        self.command()
        sid = self.p.diagnostic_state()["id"]
        def concurrent_round(*args):
            other = Progress(self.p.path); other.start_diagnostic(new=True)
            from course.runner import RunResult, TestCase
            return RunResult(tests=[TestCase("ok", "", "pass")])
        with patch("course.diagnostic.run_learner", side_effect=concurrent_round), self.assertRaises(ValueError):
            self.command("run", "1.2")
        state = Progress(self.p.path).diagnostic_state()
        self.assertNotEqual(state["id"], sid); self.assertEqual(state["attempts"], [])
        before = self.p.path.read_bytes()
        self.app.catalog = []
        with self.assertRaises(ValueError):
            self.command("new")
        self.assertEqual(self.p.path.read_bytes(), before)

    def test_practice_path_traversal_and_symlink_escape_fail(self):
        ex = find_exercise(self.app.catalog, "1.2")
        for sid in ("../escape", "", "a/b", [], "x" * 81):
            with self.assertRaises(ValueError):
                self.app.workspace.ensure_practice(ex, sid)
        outside = self.root / "outside"; outside.mkdir()
        link = self.app.workspace.root / "practice"
        link.parent.mkdir(parents=True, exist_ok=True); link.symlink_to(outside)
        with self.assertRaises(ValueError):
            self.app.workspace.ensure_practice(ex, "valid")
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
