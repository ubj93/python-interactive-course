"""Replay and watch regressions using only disposable learner state."""
import contextlib
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
from unittest.mock import Mock, patch

from course.catalog import Exercise
from course.cli import App
from course.progress import Progress
from course.workspace import Workspace


class TestRewardHistory(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'progress.json'
        self.p = Progress(self.path)
        self.lesson = SimpleNamespace(id='1.1', cards=[None])

    def test_restart_and_reload_do_not_repeat_card_xp(self):
        self.assertEqual(self.p.record_card('1.1', 0, True, True), 1)
        self.p.restart_lesson(self.lesson)
        self.p = Progress(self.path)
        self.assertFalse(self.p.card_state('1.1', 0)['done'])
        self.assertEqual(self.p.record_card('1.1', 0, True, True), 0)
        self.assertTrue(self.p.card_state('1.1', 0)['done'])
        self.assertEqual(self.p.xp, 1)

    def test_restart_after_a_miss_does_not_create_another_first_attempt(self):
        self.p.record_card('1.1', 0, True, False)
        self.p.restart_lesson(self.lesson)
        self.assertEqual(self.p.record_card('1.1', 0, True, True), 0)
        self.assertEqual(self.p.xp, 0)

    def test_legacy_attempts_are_migrated_without_recalculating_xp(self):
        for correct, tries in ((True, 1), (True, 5), (False, 1), (False, 2)):
            with self.subTest(correct=correct, tries=tries):
                self.path.write_text(json.dumps({'xp': 71, 'cards': {'1.1:0': {'done': tries > 1 or correct, 'correct': correct, 'tries': tries}}}))
                p = Progress(self.path)
                p.restart_lesson(self.lesson)
                self.assertEqual(p.record_card('1.1', 0, True, True), 0)
                self.assertEqual(p.xp, 71)
                self.assertTrue(p.data['card_reward_history']['1.1:0'])

    def test_browser_reward_history_survives_cli_import(self):
        self.path.write_text(json.dumps({'xp': 14, 'cards': {}, 'card_reward_history': {'1.1:0': True}}))
        p = Progress(self.path)
        self.assertEqual(p.record_card('1.1', 0, True, True), 0)
        self.assertEqual(p.xp, 14)
        self.assertEqual(p.record_card('1.1', 1, True, True), 1)

    def test_lesson_activity_earns_week_and_month_badges(self):
        today = dt.date.today()
        for length, badge in ((7, 'week_streak'), (30, 'month_streak')):
            with self.subTest(length=length):
                self.p.data['days'] = [(today - dt.timedelta(days=d)).isoformat() for d in range(1, length)]
                self.p.record_card('1.1', 0, False)
                self.assertIn(badge, self.p.data['badges'])
                self.assertNotIn('first_blood', self.p.data['badges'])
                self.assertEqual(self.p.xp, 0)

    def test_watch_waits_for_a_save_before_assessing(self):
        ex = Exercise(1, 1, 'demo', Path(self.temp.name))
        ex.exercise_file.write_text('raise NotImplementedError\n')
        app = App.__new__(App)
        app.resolve = lambda ref: ex
        app.rel = str
        app.progress = self.p
        app.workspace = Workspace(Path(self.temp.name) / 'learner', repository_root=Path(self.temp.name))
        answer = app.workspace.ensure(ex)
        app.run_once = Mock(return_value=0)
        def save_file(_seconds):
            app.run_once.assert_not_called()
            answer.write_text('answer = 42\n')
            stamp = answer.stat().st_mtime_ns + 1000000
            os.utime(answer, ns=(stamp, stamp))
        with patch('course.cli.time.sleep', side_effect=save_file), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(app.cmd_watch(SimpleNamespace(exercise='1.1', exit_on_pass=True)), 0)
        app.run_once.assert_called_once_with(ex)
        self.assertEqual(self.p.attempts(ex.id), 0)

    def test_failed_runs_and_solved_retries_earn_streak_only(self):
        ex = Exercise(1, 1, 'demo', Path(self.temp.name))
        today = dt.date.today()
        for already_solved in (False, True):
            with self.subTest(already_solved=already_solved):
                p = Progress(Path(self.temp.name) / ('retry.json' if already_solved else 'fail.json'))
                p.data['days'] = [(today - dt.timedelta(days=d)).isoformat() for d in range(1, 7)]
                if already_solved:
                    p.data['solved'][ex.id] = {'passed_at': '2026-01-01T00:00:00.000Z', 'xp': 9}
                    p.data['xp'] = 9
                summary = p.record_run(ex, already_solved)
                self.assertEqual(summary['new_badges'], ['week_streak'])
                self.assertNotIn('first_blood', p.data['badges'])
                self.assertEqual(summary['xp'], 0)
                self.assertEqual(p.xp, 9 if already_solved else 0)


@unittest.skipUnless(shutil.which('node'), 'browser regression requires Node.js')
class TestBrowserRewards(unittest.TestCase):
    def test_browser_replay_and_streak_rewards(self):
        result = subprocess.run([shutil.which('node'), str(Path(__file__).with_name('web_rewards.js'))], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
