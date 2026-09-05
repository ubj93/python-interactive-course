"""Extreme imported timestamps remain reportable without mutating saved results."""
import contextlib
import datetime as dt
import io
import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from course.catalog import Exercise, Part
from course.cli import App
from course.progress import Progress
from course.sessions import normalize_session
from course.timestamps import UTC


@contextlib.contextmanager
def timezone(zone):
    try:
        with patch.dict(os.environ, {"TZ": zone}):
            time.tzset()
            yield
    finally:
        time.tzset()


@unittest.skipUnless(hasattr(time, "tzset"), "timezone switching requires tzset")
class TestInterviewTimestampBoundaries(unittest.TestCase):
    def test_extreme_finished_times_fall_back_to_utc_without_changing_saved_data(self):
        cases = [
            ("Asia/Tokyo", "9999-12-31T22:00:00Z", "9999-12-31T23:00:00Z", "9999-12-31T23:30:00Z"),
            ("America/New_York", "0001-01-01T00:00:00Z", "0001-01-01T00:15:00Z", "0001-01-01T00:30:00Z"),
        ]
        for zone, started, deadline, finished in cases:
            with self.subTest(zone=zone), tempfile.TemporaryDirectory() as directory, timezone(zone):
                app = App.__new__(App)
                app.progress = Progress(Path(directory) / "progress.json")
                app.catalog = []
                session = normalize_session({"version": 1, "id": "boundary", "kind": "interview", "ids": ["9.1"], "started": started, "deadline": deadline, "finished_at": finished, "status": "finished", "attempts": []})
                app.progress.data["last_interview"] = session
                before = json.dumps(app.progress.data, sort_keys=True)
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(app.report_interview(session, final=False), 0)
                self.assertIn(finished, output.getvalue())
                self.assertEqual(json.dumps(app.progress.data, sort_keys=True), before)
                self.assertFalse(app.progress.path.exists())

    def test_starting_a_round_with_an_extreme_valid_deadline_remains_reportable(self):
        with tempfile.TemporaryDirectory() as directory, timezone("Asia/Tokyo"):
            app = App.__new__(App)
            app.progress = Progress(Path(directory) / "progress.json")
            exercise = Exercise(9, 1, "boundary", Path(directory), {})
            app.catalog = [Part(9, "practice", Path(directory), [exercise])]
            now = dt.datetime(9999, 12, 31, 22, 40, tzinfo=UTC)
            args = SimpleNamespace(new=True, finish=False, last=False, count=1, minutes=30, min_part=9)
            output = io.StringIO()
            with patch("course.progress.utc_now", return_value=now), contextlib.redirect_stdout(output):
                self.assertEqual(app.cmd_interview(args), 0)
            self.assertIn("9999-12-31T23:10:00Z", output.getvalue())
            self.assertIsNotNone(app.progress.active_interview())
