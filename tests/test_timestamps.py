"""Cross-client timestamp regressions; all progress writes use temporary files."""
import contextlib
import datetime as dt
import io
import json
import os
import shutil
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from course.catalog import Exercise
from course.cli import App
from course.progress import Progress
from course.timestamps import UTC, elapsed_seconds, local_day, parse_timestamp, timestamp, timestamp_day

ROOT = Path(__file__).resolve().parent.parent
NOW = dt.datetime(2026, 9, 5, 0, 30, tzinfo=UTC)


@contextlib.contextmanager
def timezone(name):
    previous = os.environ.get("TZ")
    os.environ["TZ"] = name
    time.tzset()
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = previous
        time.tzset()


@unittest.skipUnless(hasattr(time, "tzset"), "requires timezone switching")
class TestTimestamps(unittest.TestCase):
    def test_browser_offsets_and_legacy_local_times_represent_same_instant(self):
        with timezone("America/New_York"):
            for value in ("2026-09-05T00:30:00Z", "2026-09-05T02:30:00+02:00", "2026-09-04T20:30:00-04:00", "2026-09-04T20:30:00", "2026-09-04 20:30:00"):
                with self.subTest(value=value):
                    self.assertEqual(parse_timestamp(value), NOW)
                    self.assertEqual(timestamp(parse_timestamp(value)), "2026-09-05T00:30:00.000Z")
            self.assertEqual(parse_timestamp("2026-01-04T20:30:00"), dt.datetime(2026, 1, 5, 1, 30, tzinfo=UTC))
            self.assertIsNone(parse_timestamp("2026-03-08T02:30:00"))
            self.assertEqual(parse_timestamp("2026-11-01T01:30:00"), dt.datetime(2026, 11, 1, 5, 30, tzinfo=UTC))

    def test_invalid_values_and_future_starts_have_no_elapsed_time(self):
        for value in (None, 0, [], {}, "", "garbage", "2026-09-05", "2026-02-30T00:00:00Z", "2026-09-05T24:00:00Z", "2026-09-05T00:00:00+24:00", "2026-09-05T00:00:00+01:99"):
            with self.subTest(value=value):
                self.assertIsNone(parse_timestamp(value))
                self.assertIsNone(elapsed_seconds(value, NOW))
        self.assertIsNone(elapsed_seconds("2026-09-05T00:31:00Z", NOW))
        self.assertEqual(elapsed_seconds("2026-09-05T00:29:00.125Z", NOW), 59.875)

    def test_local_days_follow_device_timezone_at_midnight_and_dst_boundaries(self):
        for zone, expected, spring_day in (("America/New_York", "2026-09-04", "2026-03-07"), ("Asia/Tokyo", "2026-09-05", "2026-03-08")):
            with self.subTest(zone=zone), timezone(zone):
                self.assertEqual(local_day(NOW), expected)
                self.assertEqual(timestamp_day("2026-09-05T00:30:00Z"), expected)
                self.assertEqual(timestamp_day("2026-03-08T04:30:00Z"), spring_day)

    def test_local_calendar_overflow_is_ignored(self):
        for zone, value in (("Asia/Tokyo", "9999-12-31T23:30:00Z"), ("America/New_York", "0001-01-01T00:30:00Z")):
            with self.subTest(zone=zone), timezone(zone):
                self.assertIsNone(timestamp_day(value))


@unittest.skipUnless(hasattr(time, "tzset"), "requires timezone switching")
class TestProgressTimestamps(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "progress.json"
        self.ex = Exercise(1, 1, "timed", Path(self.temp.name), {"kyu": 5, "time_limit_min": 5})
        self.contexts = contextlib.ExitStack()
        self.addCleanup(self.contexts.close)
        self.contexts.enter_context(timezone("America/New_York"))
        self.contexts.enter_context(patch("course.timestamps.utc_now", return_value=NOW))
        self.contexts.enter_context(patch("course.progress.utc_now", return_value=NOW))

    def test_imported_progress_can_pass_without_losing_existing_data(self):
        for opened in ("2026-09-05T00:29:00.000Z", "2026-09-04T20:29:00-04:00", "2026-09-04T20:29:00"):
            with self.subTest(opened=opened):
                old = {"xp": 42, "solved": {"old": {"passed_at": "2026-09-04T18:00:00", "xp": 42}}, "opened": {self.ex.id: opened}, "days": ["2026-09-03"], "custom": {"keep": True}}
                self.path.write_text(json.dumps(old))
                p = Progress(self.path)
                result = p.record_run(self.ex, True)
                reloaded = Progress(self.path)
                self.assertEqual(reloaded.data["solved"]["old"], old["solved"]["old"])
                self.assertEqual(reloaded.data["opened"][self.ex.id], opened)
                self.assertEqual(reloaded.data["custom"], old["custom"])
                self.assertEqual(reloaded.xp, 42 + result["xp"])
                self.assertEqual(reloaded.data["solved"][self.ex.id]["passed_at"], "2026-09-05T00:30:00.000Z")
                self.assertEqual(reloaded.data["solved"][self.ex.id]["seconds"], 60)
                self.assertEqual(reloaded.solved_today(), 2)
                self.assertEqual(reloaded.streak(), 2)
                self.assertEqual(reloaded.record_run(self.ex, True)["xp"], 0)

    def test_invalid_and_future_imported_times_preserve_completion_without_speed_bonus(self):
        for opened in (None, "", 17, {}, "bad", "2026-09-05T00:31:00Z"):
            with self.subTest(opened=opened):
                self.path.write_text(json.dumps({"opened": {self.ex.id: opened}}))
                p = Progress(self.path)
                result = p.record_run(self.ex, True)
                self.assertTrue(p.is_solved(self.ex.id))
                self.assertIsNone(p.data["solved"][self.ex.id]["seconds"])
                self.assertNotIn("inside time limit ×1.1", result["notes"])
                self.assertNotIn("speed_demon", p.data["badges"])
                self.assertEqual(result["xp"], round(self.ex.xp * 1.25))

    def test_daily_cards_and_solved_count_use_local_day(self):
        p = Progress(self.path)
        p.data["solved"] = {"utc": {"passed_at": "2026-09-05T00:20:00Z"}, "offset": {"passed_at": "2026-09-05T02:20:00+02:00"}, "legacy": {"passed_at": "2026-09-04T20:20:00"}, "invalid": {"passed_at": 17}, "tomorrow": {"passed_at": "2026-09-05T05:00:00Z"}}
        self.assertEqual(p.solved_today(), 3)
        p.set_daily(self.ex.id)
        p.record_card("1.1", "timestamp-card", checkable=False)
        self.assertEqual(p.data["days"], ["2026-09-04"])
        self.assertEqual(p.data["daily"], {"2026-09-04": {"id": self.ex.id, "done": False}})
        p.record_run(self.ex, True)
        self.assertTrue(p.today_daily()["done"])
        self.assertEqual(p.data["badges"]["first_blood"], "2026-09-04")

    def test_cli_interview_accepts_new_and_legacy_deadlines_without_mutating_progress(self):
        app = App.__new__(App)
        app.progress = Progress(self.path)
        app.catalog = []
        before = json.dumps(app.progress.data, sort_keys=True)
        for deadline in ("2026-09-05T01:00:00Z", "2026-09-04T21:00:00-04:00", "2026-09-04T21:00:00"):
            with self.subTest(deadline=deadline), contextlib.redirect_stdout(io.StringIO()), patch("course.cli.utc_now", return_value=NOW):
                self.assertEqual(app.report_interview({"ids": ["9.1"], "started": "2026-09-05T00:00:00Z", "deadline": deadline}, final=False), 0)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(app.report_interview({"ids": [], "deadline": None}, final=False), 1)
        self.assertEqual(json.dumps(app.progress.data, sort_keys=True), before)


@unittest.skipUnless(shutil.which("node"), "browser regressions require Node.js")
class TestBrowserTimestamps(unittest.TestCase):
    def test_browser_timestamp_progress_regressions(self):
        for zone in ("America/New_York", "Asia/Tokyo"):
            with self.subTest(zone=zone):
                result = subprocess.run([shutil.which("node"), str(ROOT / "tests" / "web_timestamps.js")], cwd=ROOT, env={**os.environ, "TZ": zone}, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
