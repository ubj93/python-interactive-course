"""Session scoring and reload regressions, with no learner-answer writes."""
import contextlib
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

from course.catalog import Exercise, Part
from course.cli import App
from course.progress import Progress
from course.sessions import finish_session, new_session, normalize_session, record_attempt, session_summary
from course.timestamps import UTC, timestamp

ROOT = Path(__file__).resolve().parent.parent
START = dt.datetime(2026, 9, 5, 12, 0, tzinfo=UTC)


class TestSessions(unittest.TestCase):
    def test_attempt_scope_and_first_pass_are_independent_of_reporting_time(self):
        session = new_session(["9.1", "9.2"], 1, now=START)
        self.assertFalse(record_attempt(session, "9.1", True, START - dt.timedelta(seconds=1)))
        self.assertFalse(record_attempt(session, "9.3", True, START))
        self.assertEqual(session_summary(session)["passed"], 0)
        record_attempt(session, "9.1", False, START)
        record_attempt(session, "9.1", True, START + dt.timedelta(seconds=60))
        record_attempt(session, "9.1", True, START + dt.timedelta(seconds=80))
        record_attempt(session, "9.2", True, START + dt.timedelta(seconds=61))
        result = session_summary(session)
        self.assertEqual((result["passed"], result["on_time"]), (2, 1))
        self.assertEqual(result["results"][0]["attempts"], 3)
        self.assertEqual(result["results"][0]["passed_at"], "2026-09-05T12:01:00.000Z")
        finished = finish_session(session, START + dt.timedelta(minutes=10))
        self.assertEqual(finished["summary"], result)
        before = copy.deepcopy(finished)
        self.assertFalse(record_attempt(finished, "9.2", True, START + dt.timedelta(minutes=11)))
        self.assertEqual(finish_session(finished, START + dt.timedelta(days=1)), before)
        record_attempt(session, "9.2", False, START + dt.timedelta(minutes=11))
        self.assertEqual(finished, before)

    def test_invalid_metadata_never_creates_a_scoring_session(self):
        good = new_session(["9.1"], 1, now=START)
        variants = [None, [], 17, {}, {**good, "ids": []}, {**good, "ids": ["9.1", "9.1"]}, {**good, "ids": [None]}, {**good, "started": "bad"}, {**good, "deadline": good["started"]}, {**good, "attempts": None}, {**good, "status": []}, {**good, "kind": 7}, {**good, "status": "finished", "finished_at": None}, {**good, "version": 999}]
        for value in variants:
            with self.subTest(value=value):
                self.assertIsNone(normalize_session(value))
                self.assertIsNone(session_summary(value))
                self.assertIsNone(finish_session(value))
        for ids, minutes in (([], 1), (["9.1"], 0), (["9.1"], -1), (["9.1"], float("inf")), (["9.1"], 10 ** 50), (["9.1"], 10 ** 1000)):
            with self.subTest(ids=ids, minutes=minutes), self.assertRaises(ValueError):
                new_session(ids, minutes, now=START)

    def test_finish_refuses_clock_rollback_before_any_recorded_attempt(self):
        session = new_session(["9.1"], 1, now=START)
        record_attempt(session, "9.1", True, START + dt.timedelta(seconds=10))
        record_attempt(session, "9.1", False, START + dt.timedelta(seconds=12))
        before = copy.deepcopy(session)
        for seconds in (-1, 5, 11):
            with self.subTest(seconds=seconds):
                self.assertIsNone(finish_session(session, START + dt.timedelta(seconds=seconds)))
                self.assertEqual(session, before)
        finished = finish_session(session, START + dt.timedelta(seconds=12))
        self.assertEqual(finished["summary"]["passed"], 1)
        self.assertEqual(finished["summary"]["results"][0]["attempts"], 2)

    def test_malformed_events_cannot_supply_session_credit(self):
        session = new_session(["9.1"], 1, now=START)
        session["attempts"] = [None, {"exercise_id": "9.2", "passed": True, "at": timestamp(START)}, {"exercise_id": "9.1", "passed": "true", "at": timestamp(START)}, {"exercise_id": "9.1", "passed": True, "at": "bad"}, {"exercise_id": "9.1", "passed": True, "at": timestamp(START - dt.timedelta(seconds=1))}]
        self.assertEqual(session_summary(session)["passed"], 0)
        self.assertEqual(session_summary(session)["results"][0]["attempts"], 0)

    def test_legacy_cli_and_browser_sessions_keep_metadata_without_inventing_passes(self):
        for started, deadline in ((timestamp(START), timestamp(START + dt.timedelta(minutes=1))), (START.timestamp() * 1000, (START + dt.timedelta(minutes=1)).timestamp() * 1000)):
            legacy = {"ids": ["9.1"], "started": started, "deadline": deadline, "before": ["9.1"], "solved_before": ["9.1"], "custom": "preserve"}
            migrated = normalize_session(legacy)
            self.assertTrue(migrated["legacy"])
            self.assertEqual(migrated["custom"], "preserve")
            self.assertEqual(migrated["started"], timestamp(START))
            self.assertEqual(session_summary(migrated)["passed"], 0)
            record_attempt(migrated, "9.1", True, START + dt.timedelta(seconds=1))
            self.assertEqual(session_summary(migrated)["passed"], 1)


class TestInterviewProgress(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "progress.json"
        self.ex = Exercise(9, 1, "repeat", Path(self.temp.name), {"kyu": 5, "time_limit_min": 1})
        self.p = Progress(self.path)
        self.app = App.__new__(App)
        self.app.progress = self.p
        self.app.catalog = [Part(9, "practice", Path(self.temp.name), [self.ex])]
        self.args = SimpleNamespace(new=False, finish=False, count=1, minutes=1, min_part=9)
        self.clock = contextlib.ExitStack()
        self.addCleanup(self.clock.close)
        self.now = START
        self.clock.enter_context(patch("course.progress.utc_now", side_effect=lambda: self.now))
        self.clock.enter_context(patch("course.timestamps.utc_now", side_effect=lambda: self.now))
        self.clock.enter_context(patch("course.cli.utc_now", side_effect=lambda: self.now))

    def command(self, **kwargs):
        args = SimpleNamespace(**{**vars(self.args), **kwargs})
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = self.app.cmd_interview(args)
        return code, output.getvalue()

    def test_previously_solved_exercise_needs_fresh_pass_and_never_duplicates_xp(self):
        self.p.record_run(self.ex, True)
        old_solved, xp = copy.deepcopy(self.p.data["solved"]), self.p.xp
        code, output = self.command()
        self.assertEqual(code, 0)
        self.assertIn("awaiting a fresh passing attempt", output)
        self.assertEqual(session_summary(self.p.active_interview())["passed"], 0)
        self.now += dt.timedelta(seconds=10)
        self.assertEqual(self.p.record_run(self.ex, True)["xp"], 0)
        self.assertEqual(self.p.xp, xp)
        self.assertEqual(self.p.data["solved"], old_solved)
        self.assertEqual(session_summary(self.p.active_interview())["passed"], 1)

    def test_late_report_and_finish_keep_on_time_credit_across_reload(self):
        self.command()
        self.now += dt.timedelta(seconds=60)
        self.p.record_run(self.ex, True)
        self.now += dt.timedelta(minutes=5)
        self.app.progress = self.p = Progress(self.path)
        code, output = self.command()
        self.assertEqual(code, 0)
        self.assertIn("Time is up", output)
        self.assertIn("1/1 on time", output)
        code, output = self.command(finish=True)
        self.assertEqual(code, 0)
        self.assertIn("results", output)
        self.assertIn("interviewer", self.p.data["badges"])
        frozen = copy.deepcopy(self.p.data["last_interview"])
        self.assertIsNone(self.p.data["interview"])
        self.p.record_run(self.ex, False)
        self.p.record_run(self.ex, True)
        self.app.progress = self.p = Progress(self.path)
        code, output = self.command(finish=True)
        self.assertEqual(code, 0)
        self.assertIn("1/1 on time", output)
        self.assertEqual(self.p.data["last_interview"], frozen)
        self.command(new=True)
        self.assertEqual(self.p.data["last_interview"], frozen)
        self.assertEqual(session_summary(self.p.active_interview())["passed"], 0)
        code, output = self.command(last=True)
        self.assertEqual(code, 0)
        self.assertIn("1/1 on time", output)
        self.assertEqual(session_summary(self.p.active_interview())["passed"], 0)

    def test_late_pass_does_not_award_badge_and_starting_new_preserves_result(self):
        self.command()
        self.now += dt.timedelta(seconds=61)
        self.p.record_run(self.ex, True)
        code, output = self.command(new=True)
        self.assertEqual(code, 0)
        summary = self.p.data["last_interview"]["summary"]
        self.assertEqual((summary["passed"], summary["on_time"]), (1, 0))
        self.assertNotIn("interviewer", self.p.data["badges"])
        self.assertEqual(session_summary(self.p.active_interview())["passed"], 0)

    def test_rollback_finish_and_restart_preserve_memory_disk_and_prior_result(self):
        self.command()
        self.now = START + dt.timedelta(seconds=10)
        self.p.record_run(self.ex, True)
        self.p.data["last_interview"] = {"custom": "previous result stays untouched"}
        self.p.save()
        before = copy.deepcopy(self.p.data)
        saved = self.path.read_bytes()
        for seconds in (-1, 5):
            self.now = START + dt.timedelta(seconds=seconds)
            with self.subTest(seconds=seconds):
                self.assertIsNone(self.p.finish_interview())
                with self.assertRaisesRegex(ValueError, "device clock"):
                    self.p.start_interview([self.ex.id], 1)
                code, output = self.command(new=True)
                self.assertEqual(code, 2)
                self.assertIn("device clock", output)
                self.assertEqual(self.p.data, before)
                self.assertEqual(self.path.read_bytes(), saved)
        self.now = START + dt.timedelta(seconds=10)
        self.assertEqual(self.command(new=True)[0], 0)
        self.assertEqual(self.p.data["last_interview"]["summary"]["passed"], 1)
        self.assertEqual(session_summary(self.p.active_interview())["passed"], 0)

    def test_oversized_duration_reports_validation_error_without_changing_round(self):
        self.command()
        before = copy.deepcopy(self.p.data)
        saved = self.path.read_bytes()
        code, output = self.command(new=True, minutes=10 ** 1000)
        self.assertEqual(code, 2)
        self.assertIn("duration", output)
        self.assertEqual(self.p.data, before)
        self.assertEqual(self.path.read_bytes(), saved)

    def test_invalid_and_empty_rounds_preserve_progress_and_allow_recovery(self):
        invalid = {"ids": [], "started": "bad", "deadline": "bad"}
        self.p.data["interview"] = copy.deepcopy(invalid)
        self.p.record_run(self.ex, True)
        self.assertEqual(self.p.data["interview"], invalid)
        self.assertEqual(self.command()[0], 1)
        self.assertEqual(self.command(new=True, min_part=99)[0], 2)
        self.assertEqual(self.command(new=True, count=0)[0], 2)
        self.assertEqual(self.command(new=True, minutes=0)[0], 2)
        self.assertEqual(self.p.data["interview"], invalid)
        self.assertEqual(self.command(new=True)[0], 0)
        self.assertIsNotNone(self.p.active_interview())

    def test_legacy_reload_requires_new_attempts_even_when_lifetime_pass_exists(self):
        self.p.record_run(self.ex, True)
        self.p.data["interview"] = {"ids": [self.ex.id], "started": timestamp(START), "deadline": timestamp(START + dt.timedelta(minutes=1)), "solved_before": []}
        self.p.save()
        self.app.progress = self.p = Progress(self.path)
        code, output = self.command()
        self.assertEqual(code, 0)
        self.assertIn("Only fresh runs", output)
        self.assertIn("0/1 passed", output)
        self.p.record_run(self.ex, True)
        self.assertEqual(session_summary(self.p.active_interview())["passed"], 1)


@unittest.skipUnless(shutil.which("node"), "browser regressions require Node.js")
class TestBrowserSessions(unittest.TestCase):
    def test_browser_rounds_migration_and_cross_client_format(self):
        session = new_session(["9.1", "9.2"], 1, now=START)
        record_attempt(session, "9.1", True, START + dt.timedelta(seconds=60))
        record_attempt(session, "9.2", True, START + dt.timedelta(seconds=61))
        finished = finish_session(session, START + dt.timedelta(minutes=2))
        result = subprocess.run([shutil.which("node"), str(ROOT / "tests" / "web_sessions.js")], input=json.dumps(finished), cwd=ROOT, env={**os.environ, "TZ": "America/New_York"}, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        browser = json.loads(result.stdout)
        self.assertEqual(session_summary(browser), browser["summary"])
