"""Saved path navigation is explicit, portable and independent of lifetime scores."""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from course import refresher
from course.catalog import all_exercises, load_catalog
from course.lessons import load_all_lessons
from course.progress import Progress
from course.refresher_cli import command
from course.practice import DIAGNOSTIC_IDS, new_practice, update_practice

ROOT = Path(__file__).resolve().parent.parent


class TestRefresherPlan(unittest.TestCase):
    def test_curated_sessions_have_real_links_manageable_budgets_and_practised_mocks(self):
        plan = refresher.catalog()
        curriculum = load_catalog()
        lessons = {lesson.id for group in load_all_lessons(curriculum).values() for lesson in group}
        exercises = {exercise.id for exercise in all_exercises(curriculum)}
        self.assertEqual(len(plan["sessions"]), 14)
        ids = [item["id"] for item in refresher.activities()]
        self.assertEqual(len(ids), len(set(ids)))
        practised = set()
        for session in plan["sessions"]:
            self.assertTrue(session["prerequisite"])
            self.assertTrue(75 <= sum(item["minutes"] for item in session["activities"]) <= 90)
            for activity in session["activities"]:
                self.assertLessEqual(set(activity["lessons"]), lessons)
                self.assertLessEqual(set(activity["exercises"]), exercises)
                if activity["kind"] == "practice":
                    practised.update(activity["exercises"])
                elif activity["kind"] == "mock":
                    self.assertLessEqual(set(activity["exercises"]), practised)
                    self.assertFalse(set(activity["exercises"]) & {"12.9", "12.10", "10.6"})
        self.assertEqual(sum(item["kind"] == "mock" for item in refresher.activities()), 2)
        for optional in plan["optional"]:
            self.assertLessEqual(set(optional["lessons"]), lessons)

    def test_done_skip_revisit_and_notes_survive_reload_without_inferred_mastery(self):
        original = {"xp": 200, "solved": {"2.1": {"xp": 3}}, "cards": {"anything": {"done": True}}}
        progress = copy.deepcopy(original)
        saved = refresher.update(None, "done")
        self.assertEqual(saved["next_activity"], "baseline-review")
        saved = refresher.update(saved, "skip")
        self.assertEqual(saved["next_activity"], "baseline-plan")
        saved = refresher.update(saved, "note", "baseline-diagnostic", "Explain the loop boundary")
        saved = refresher.update(saved, "revisit", "baseline-diagnostic")
        progress["refresher"] = json.loads(json.dumps(saved))
        self.assertEqual(refresher.state(progress["refresher"])["next_activity"], "baseline-diagnostic")
        self.assertEqual(refresher.status(saved, "baseline-diagnostic"), "pending")
        self.assertEqual(refresher.status(saved, "baseline-review"), "skipped")
        self.assertEqual(saved["activities"]["baseline-diagnostic"]["note"], "Explain the loop boundary")
        self.assertEqual({key: progress[key] for key in original}, original)
        for activity in refresher.activities():
            saved = refresher.update(saved, "done", activity["id"])
        self.assertIsNone(refresher.state(saved)["next_activity"])
        self.assertEqual(refresher.update(saved, "revisit", "mocks-a")["next_activity"], "mocks-a")

    def test_malformed_and_unknown_records_are_not_silently_destroyed(self):
        for invalid in ({"version": True}, {"version": 99}, [], "oops"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                refresher.state(invalid)
        saved = refresher.state()
        saved["custom"] = {"keep": 1}
        saved["activities"]["future-activity"] = {"status": "done", "note": "keep"}
        before = copy.deepcopy(saved)
        result = refresher.update(saved, "skip")
        self.assertEqual(saved, before)
        self.assertEqual(result["custom"], saved["custom"])
        self.assertEqual(result["activities"]["future-activity"], saved["activities"]["future-activity"])

    def test_review_suggestions_use_self_reports_and_fresh_diagnostic_evidence(self):
        diagnostic = {**new_practice(DIAGNOSTIC_IDS, "diagnostic"), "attempts": [{"exercise_id": "1.2", "passed": True}, {"exercise_id": "1.3", "passed": False}], "reflections": {"1.2": {"confidence": "needs_review", "mistake_note": "forgot strip", "help_at": "2026-09-05T12:00:00Z"}, "2.1": {"confidence": "confident"}}}
        diagnostic["reflections"]["1.2"]["help_at"] = diagnostic["started"]
        for event in diagnostic["attempts"]:
            event["at"] = diagnostic["started"]
        before = copy.deepcopy(diagnostic)
        rows = refresher.weak_areas(diagnostic)
        self.assertEqual([row["id"] for row in rows], ["1.2", "1.3"])
        self.assertEqual(rows[0]["lessons"], ["1.2"])
        self.assertEqual(rows[0]["note"], "forgot strip")
        self.assertEqual(diagnostic, before)

    def test_failed_retry_is_suggested_and_invalid_diagnostic_does_not_invent_signals(self):
        diagnostic = new_practice(DIAGNOSTIC_IDS, "diagnostic")
        diagnostic = update_practice(diagnostic, "1.2", "attempt", passed=True)
        diagnostic = update_practice(diagnostic, "1.2", "attempt", passed=False)
        rows = refresher.weak_areas(diagnostic)
        self.assertEqual(rows[0]["id"], "1.2")
        self.assertEqual(rows[0]["reasons"], ["Latest diagnostic run did not pass"])
        diagnostic = update_practice(diagnostic, "1.2", "attempt", passed=True)
        self.assertEqual(refresher.weak_areas(diagnostic), [])
        diagnostic["attempts"].append({"exercise_id": "1.3", "passed": False, "at": "invalid"})
        self.assertEqual(refresher.weak_areas(diagnostic), [])
        self.assertEqual(refresher.weak_areas({"attempts": [], "reflections": {"1.2": {"confidence": "needs_review"}}}), [])

    @unittest.skipUnless(shutil.which("node"), "Node is needed for browser-format parity")
    def test_javascript_navigation_and_reflection_parity(self):
        saved = refresher.update(None, "done")
        saved = refresher.update(saved, "skip")
        result = subprocess.run([shutil.which("node"), str(ROOT / "tests/web_refresher.js")], input=json.dumps({"plan": refresher.catalog(), "saved": saved, "diagnostic": new_practice(DIAGNOSTIC_IDS, "diagnostic")}), text=True, capture_output=True, check=True)
        imported = json.loads(result.stdout)
        self.assertEqual(refresher.state(imported)["next_activity"], "baseline-diagnostic")
        self.assertEqual(imported["activities"]["baseline-diagnostic"]["note"], "A saved takeaway")


class TestRefresherCLI(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.progress = Path(self.temp.name) / "progress.json"
        self.env = dict(os.environ, COURSE_PROGRESS=str(self.progress), COURSE_WORKSPACE=str(Path(self.temp.name) / "workspace"), PYTHONDONTWRITEBYTECODE="1")

    def command(self, *args):
        import sys
        return subprocess.run([sys.executable, str(ROOT / "course.py"), "--no-color", "refresher", *args], cwd=ROOT, env=self.env, text=True, capture_output=True)

    def test_real_cli_resume_skip_revisit_and_curated_mock_preserve_course_progress(self):
        original = {"xp": 123, "solved": {"5.4": {"xp": 23}}, "cards": {"old": {"done": True}}}
        self.progress.write_text(json.dumps(original))
        self.assertEqual(self.command("open").returncode, 0)
        self.assertIn("baseline-review", self.command("done").stdout)
        self.assertIn("baseline-plan", self.command("skip").stdout)
        self.assertIn("baseline-diagnostic", self.command("revisit", "baseline-diagnostic").stdout)
        self.assertIn("baseline-diagnostic", self.command().stdout)
        self.assertEqual(self.command("mock", "mocks-a").returncode, 0)
        saved = json.loads(self.progress.read_text())
        self.assertEqual(saved["interview"]["ids"], ["5.4", "10.1"])
        self.assertEqual(saved["interview"]["attempts"], [])
        first_id = saved["interview"]["id"]
        self.assertEqual(self.command("mock", "mocks-a").returncode, 0)
        self.assertEqual(json.loads(self.progress.read_text())["interview"]["id"], first_id)
        self.assertEqual(self.command("mock", "mocks-b").returncode, 2)
        self.assertEqual(json.loads(self.progress.read_text())["interview"]["id"], first_id)
        for key, value in original.items():
            self.assertEqual(saved[key], value)

    def test_status_is_read_only_and_invalid_activity_cannot_create_progress(self):
        self.assertIn("baseline-diagnostic", self.command().stdout)
        self.assertFalse(self.progress.exists())
        self.assertEqual(self.command("done", "unknown").returncode, 2)
        self.assertFalse(self.progress.exists())

    def test_completed_path_reopens_as_a_completed_summary(self):
        saved = refresher.state()
        for activity in refresher.activities():
            saved = refresher.update(saved, "done", activity["id"])
        self.progress.write_text(json.dumps({"refresher": saved}))
        before = self.progress.read_bytes()
        result = self.command("open")
        self.assertEqual(result.returncode, 0)
        self.assertIn("All path activities are done or skipped", result.stdout)
        self.assertEqual(self.progress.read_bytes(), before)

    def test_mock_and_path_link_are_saved_together_or_both_rolled_back(self):
        progress = Progress(self.progress)
        app = SimpleNamespace(progress=progress, report_interview=lambda session, final: 0)
        args = SimpleNamespace(action="mock", activity="mocks-a", text=None)
        before = copy.deepcopy(progress.data)
        with patch.object(progress, "save", side_effect=OSError("disk full")) as save:
            with self.assertRaises(OSError):
                command(app, args)
            save.assert_called_once()
        self.assertEqual(progress.data, before)
        self.assertEqual(command(app, args), 0)
        reloaded = Progress(self.progress)
        self.assertEqual(reloaded.data["refresher"]["mock_sessions"]["mocks-a"], reloaded.active_interview()["id"])

    def test_diagnostic_reflection_returns_to_same_saved_path_activity(self):
        import sys
        self.assertEqual(self.command("open").returncode, 0)
        result = subprocess.run([sys.executable, str(ROOT / "course.py"), "--no-color", "diagnostic", "reflect", "1.2", "--confidence", "needs-review", "--note", "Strip before splitting"], cwd=ROOT, env=self.env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        resumed = self.command("open")
        self.assertEqual(resumed.returncode, 0)
        self.assertIn("baseline-diagnostic", resumed.stdout)
        self.assertIn("course learn 1.2", resumed.stdout)
        self.assertIn("Strip before splitting", resumed.stdout)
        saved = json.loads(self.progress.read_text())
        self.assertEqual(saved["refresher"]["next_activity"], "baseline-diagnostic")
        self.assertEqual(saved["xp"], 0)
        self.assertEqual(saved["solved"], {})
