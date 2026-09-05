"""Learner operations use temporary workspaces and never edit course content."""
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

from course.catalog import ROOT, load_catalog
from course.runner import run_learner
from course.workspace import Workspace
from test_engine import TESTS, make_exercise


class TestWorkspace(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.ex = make_exercise(self.repo / "curriculum", "def f(x):\n    raise NotImplementedError\n", TESTS)
        self.catalog = load_catalog(self.repo / "curriculum")
        self.workspace = Workspace(self.root / "learner", repository_root=self.repo)

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True, text=True)

    def commit_starter(self):
        self.git("init", "-q")
        self.git("add", "curriculum")
        self.git("-c", "user.name=Course tests", "-c", "user.email=course-tests@example.invalid", "commit", "-qm", "fixture starter")

    def test_workspace_override_and_initialization_preserve_saved_answer(self):
        with patch.dict(os.environ, {"COURSE_WORKSPACE": str(self.root / "override")}):
            self.assertEqual(Workspace(repository_root=self.repo).root, (self.root / "override").resolve())
        source = self.ex.exercise_file.read_bytes()
        answer = self.workspace.ensure(self.ex)
        self.assertEqual(answer.read_bytes(), source)
        answer.write_text("def f(x):\n    return x + 1\n")
        self.assertEqual(self.workspace.ensure(self.ex).read_text(), "def f(x):\n    return x + 1\n")
        self.assertEqual(self.ex.exercise_file.read_bytes(), source)

    def test_new_answers_use_committed_starter_without_implicitly_migrating_local_edits(self):
        self.commit_starter()
        starter = self.ex.exercise_file.read_bytes()
        self.ex.exercise_file.write_text("# could be an author edit or an old learner answer\n")
        answer = self.workspace.ensure(self.ex)
        self.assertEqual(answer.read_bytes(), starter)
        self.assertIn("author edit", self.ex.exercise_file.read_text())

    def test_download_inside_an_unrelated_repository_uses_its_own_starter(self):
        self.commit_starter()
        nested = self.repo / "download"
        downloaded = make_exercise(nested / "curriculum", "# downloaded course starter\n", TESTS)
        workspace = Workspace(self.root / "downloaded-answers", repository_root=nested)
        self.assertEqual(workspace.ensure(downloaded).read_text(), "# downloaded course starter\n")
        self.assertEqual(workspace.legacy_answers(load_catalog(nested / "curriculum")), [])

    def test_grading_uses_answer_and_disposable_fixtures(self):
        fixtures = self.ex.dir / "fixtures"
        fixtures.mkdir()
        data = fixtures / "input.txt"
        data.write_text("original")
        answer = self.workspace.ensure(self.ex)
        answer.write_text("from pathlib import Path\nPath('fixtures/input.txt').write_text('changed')\ndef f(x):\n    return x + 1\n")
        source = self.ex.exercise_file.read_bytes()
        tests = self.ex.test_file.read_bytes()
        self.assertTrue(run_learner(self.ex, self.workspace).ok)
        self.assertEqual(data.read_text(), "original")
        self.assertEqual(self.ex.exercise_file.read_bytes(), source)
        self.assertEqual(self.ex.test_file.read_bytes(), tests)

    def test_grading_copies_sibling_helpers_but_keeps_canonical_tests_and_fixtures(self):
        fixtures = self.ex.dir / "fixtures"
        fixtures.mkdir()
        (fixtures / "input.txt").write_text("course fixture")
        self.ex.test_file.write_text("import unittest\nfrom pathlib import Path\nfrom exercise import f\nclass T(unittest.TestCase):\n    def test_answer_and_fixture(self):\n        self.assertEqual(f(1), 2)\n        self.assertEqual(Path('fixtures/input.txt').read_text(), 'course fixture')\n")
        answer = self.workspace.ensure(self.ex)
        answer.write_text("from helper import f\n")
        helper = answer.with_name("helper.py")
        helper.write_text("from pathlib import Path\nPath(__file__).write_text('# disposable helper changed')\ndef f(x):\n    return x + 1\n")
        helper_before = helper.read_bytes()
        answer.with_name("test_exercise.py").write_text("raise RuntimeError('learner tests must not replace course tests')\n")
        learner_fixtures = answer.parent / "fixtures"
        learner_fixtures.mkdir()
        (learner_fixtures / "input.txt").write_text("learner fixture")
        self.assertTrue(run_learner(self.ex, self.workspace).ok)
        self.assertEqual(helper.read_bytes(), helper_before)
        self.assertEqual((fixtures / "input.txt").read_text(), "course fixture")
        self.assertEqual((learner_fixtures / "input.txt").read_text(), "learner fixture")

    def test_grading_rejects_helper_symlinks_and_answers_outside_workspace(self):
        answer = self.workspace.ensure(self.ex)
        outside = self.root / "outside.py"
        outside.write_text("raise RuntimeError('must not read or run outside modules')\n")
        helper = answer.with_name("helper.py")
        helper.symlink_to(outside)
        with self.assertRaises(ValueError):
            run_learner(self.ex, self.workspace)
        helper.unlink()
        with self.assertRaises(ValueError):
            run_learner(self.ex, self.workspace, outside)
        self.assertEqual(outside.read_text(), "raise RuntimeError('must not read or run outside modules')\n")

    def test_scratch_and_repeated_resets_preserve_all_previous_answers(self):
        answer = self.workspace.ensure(self.ex)
        answer.write_text("saved answer")
        scratch = self.workspace.ensure(self.ex, scratch=True)
        scratch.write_text("first practice")
        path, first = self.workspace.reset(self.ex, scratch=True)
        self.assertEqual(path, scratch)
        self.assertEqual(first.read_text(), "first practice")
        scratch.write_text("second practice")
        _, second = self.workspace.reset(self.ex, scratch=True)
        self.assertNotEqual(first, second)
        self.assertEqual(first.read_text(), "first practice")
        self.assertEqual(second.read_text(), "second practice")
        self.assertEqual(answer.read_text(), "saved answer")

    def test_legacy_migration_preview_and_copy_leave_author_edits_untouched(self):
        self.commit_starter()
        self.ex.exercise_file.write_text("legacy answer")
        self.assertEqual(self.workspace.legacy_answers(self.catalog), [self.ex])
        self.assertFalse(self.workspace.root.exists())
        result = self.workspace.migrate([self.ex])
        self.assertEqual(self.workspace.answer_path(self.ex).read_text(), "legacy answer")
        self.assertEqual(self.ex.exercise_file.read_text(), "legacy answer")
        self.assertEqual(Path(result["recoveries"][0]).read_text(), "legacy answer")
        self.assertEqual(result["restored"], [])

    def test_migration_conflicts_keep_both_answers_and_restore_only_when_requested(self):
        self.commit_starter()
        starter = self.ex.exercise_file.read_bytes()
        answer = self.workspace.ensure(self.ex)
        answer.write_text("new workspace answer")
        self.ex.exercise_file.write_text("legacy answer")
        result = self.workspace.migrate([self.ex], restore_starters=True)
        self.assertEqual(result["conflicts"], [str(answer)])
        self.assertEqual(answer.read_text(), "new workspace answer")
        self.assertEqual(Path(result["recoveries"][0]).read_text(), "legacy answer")
        self.assertEqual(self.ex.exercise_file.read_bytes(), starter)
        self.assertFalse(self.workspace.legacy_answers(self.catalog))

    def test_watch_waits_for_workspace_changes_and_repl_uses_a_disposable_copy(self):
        from course.cli import App

        with patch.dict(os.environ, {"COURSE_WORKSPACE": str(self.workspace.root), "COURSE_PROGRESS": str(self.root / "progress.json")}), patch("course.cli.load_catalog", return_value=self.catalog):
            app = App()
        answer = app.workspace.ensure(self.ex)
        answer.write_text("def f(x):\n    return x + 1\n")
        helper = answer.with_name("helper.py")
        helper.write_text("# learner module available in the REPL\n")
        original = self.ex.exercise_file.read_bytes()

        def save_answer(_):
            stamp = answer.stat().st_mtime_ns + 1000000
            os.utime(answer, ns=(stamp, stamp))

        with patch("sys.stdout", new_callable=io.StringIO), patch("course.cli.time.sleep", side_effect=save_answer) as sleep, patch.object(app, "run_once", return_value=0) as run:
            self.assertEqual(app.cmd_watch(SimpleNamespace(exercise="1.1", exit_on_pass=True)), 0)
        sleep.assert_called_once()
        run.assert_called_once_with(self.ex)

        loaded = []
        def inspect_repl(command, cwd):
            path = Path(command[-1])
            loaded.append(path)
            self.assertNotEqual(path, answer)
            self.assertNotEqual(path, self.ex.exercise_file)
            self.assertEqual(path.read_bytes(), answer.read_bytes())
            self.assertEqual(path.with_name("helper.py").read_bytes(), helper.read_bytes())
            self.assertEqual(Path(cwd), path.parent)
            return 0

        with patch("sys.stdout", new_callable=io.StringIO), patch("course.cli.subprocess.call", side_effect=inspect_repl):
            self.assertEqual(app.cmd_repl(SimpleNamespace(exercise="1.1")), 0)
        self.assertFalse(loaded[0].exists())
        self.assertEqual(self.ex.exercise_file.read_bytes(), original)

    def test_workspace_symlinks_and_source_locations_are_rejected(self):
        outside = self.root / "outside"
        outside.write_text("keep")
        answer = self.workspace.answer_path(self.ex)
        answer.parent.mkdir(parents=True)
        answer.symlink_to(outside)
        with self.assertRaises(ValueError):
            self.workspace.ensure(self.ex)
        with self.assertRaises(ValueError):
            self.workspace.reset(self.ex)
        self.assertEqual(outside.read_text(), "keep")
        for location in (self.repo, self.repo / "curriculum", self.repo / "docs" / "answers"):
            with self.assertRaises(ValueError):
                Workspace(location, repository_root=self.repo)


class TestWorkspaceCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.env = dict(os.environ, COURSE_WORKSPACE=str(self.root / "answers"), COURSE_PROGRESS=str(self.root / "progress.json"), PYTHONDONTWRITEBYTECODE="1")

    def cli(self, *args, code=0):
        result = subprocess.run([sys.executable, str(ROOT / "course.py"), "--no-color", *args], env=self.env, cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result.stdout

    def test_default_progress_and_recovery_files_are_gitignored(self):
        paths = [".course_progress.json", ".course_progress.json.bak", ".course_progress.json.bak." + "a" * 32]
        result = subprocess.run(["git", "check-ignore", "--no-index", "--stdin"], input="\n".join(paths) + "\n", cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), paths)

    def test_study_path_run_and_scratch_leave_curriculum_and_browser_bundle_unchanged(self):
        ex = load_catalog()[0].exercises[0]
        watched = [ex.exercise_file, ex.test_file, ROOT / "docs" / "exercises.js"]
        before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
        answer = Path(self.cli("path", "1.1").strip())
        self.assertNotEqual(answer, ex.exercise_file)
        answer.write_bytes(ex.solution_file.read_bytes())
        self.assertIn(str(answer.relative_to(self.root.resolve())), self.cli("show", "1.1"))
        self.assertIn("All", self.cli("run", "1.1"))
        progress = self.root / "progress.json"
        progress_before = progress.read_bytes()
        saved = answer.read_bytes()
        scratch = Path(self.cli("path", "1.1", "--scratch").strip())
        self.assertNotEqual(scratch, answer)
        scratch.write_bytes(ex.solution_file.read_bytes())
        self.assertIn("Scratch practice", self.cli("run", "1.1", "--scratch"))
        self.cli("reset", "1.1", "--scratch")
        self.assertEqual(progress.read_bytes(), progress_before)
        self.assertEqual(answer.read_bytes(), saved)
        self.cli("reset", "1.1")
        self.assertTrue(list(answer.parent.glob("exercise.py.bak.*")))
        self.assertTrue(list(progress.parent.glob("progress.json.bak.*")))
        self.assertEqual(before, {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in watched})

    def test_backup_restore_cli_refuses_overwrite_and_recovers_forced_replacement(self):
        answer = Path(self.cli("path", "1.1").strip())
        answer.write_text("saved answer")
        archive = self.root / "backup.zip"
        self.cli("backup", "--to", str(archive))
        self.cli("backup", "--to", str(archive), code=2)
        self.assertIn("workspace/answers/", self.cli("restore", str(archive), "--list"))
        answer.write_text("newer answer")
        self.cli("restore", str(archive), "--exercises-only", code=2)
        self.assertEqual(answer.read_text(), "newer answer")
        self.cli("restore", str(archive), "--exercises-only", "--force")
        self.assertEqual(answer.read_text(), "saved answer")
        recoveries = list(answer.parent.glob("exercise.py.bak.*"))
        self.assertEqual([path.read_text() for path in recoveries], ["newer answer"])
        malformed = self.root / "not-a-zip.zip"
        malformed.write_text("not a zip")
        self.cli("restore", str(malformed), "--list", code=2)

    def test_new_scratch_run_does_not_create_mastery_progress(self):
        self.cli("run", "1.1", "--scratch", code=1)
        self.assertFalse((self.root / "progress.json").exists())

    def test_daily_alias_scratch_commands_leave_new_and_existing_progress_unchanged(self):
        progress = self.root / "progress.json"
        for existing in (False, True):
            with self.subTest(existing=existing):
                if existing:
                    progress.write_text('{"xp": 13, "daily": {}}')
                before = progress.read_bytes() if existing else None
                self.cli("path", "daily", "--scratch")
                self.cli("run", "daily", "--scratch", code=1)
                self.cli("reset", "daily", "--scratch")
                self.assertEqual(progress.read_bytes() if progress.exists() else None, before)

    def test_migration_requires_apply_before_restoring_starters(self):
        result = subprocess.run([sys.executable, str(ROOT / "course.py"), "migrate-answers", "--restore-starters"], env=self.env, cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--apply", result.stderr)
        self.assertFalse((self.root / "answers").exists())
