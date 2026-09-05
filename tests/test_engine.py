"""Unit tests for the course engine (not the curriculum; tools/verify.py covers that)."""
import datetime as dt
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from course.catalog import KYU_XP, Exercise, find_exercise, find_part, load_catalog
from course.progress import Progress
from course.runner import run_solution, run_tests

ROOT = Path(__file__).resolve().parent.parent


def make_exercise(tmp: Path, body: str, tests: str, meta=None) -> Exercise:
    d = tmp / "part01_demo" / "01_demo"
    d.mkdir(parents=True)
    (tmp / "part01_demo" / "LESSON.md").write_text("# Part 1 · Demo\n")
    (d / "exercise.py").write_text(body)
    (d / "test_exercise.py").write_text(tests)
    (d / "solution.py").write_text(body)
    (d / "meta.json").write_text(json.dumps(meta or {"title": "Demo", "kyu": 7, "hints": ["h1", "h2"], "tags": ["t"]}))
    return load_catalog(tmp)[0].exercises[0]


TESTS = """
import unittest
from exercise import f
class T(unittest.TestCase):
    def test_one(self):
        \"\"\"one\"\"\"
        self.assertEqual(f(1), 2)
    def test_two(self):
        \"\"\"two\"\"\"
        self.assertEqual(f(2), 3)
"""


class TestCatalog(unittest.TestCase):
    def test_real_catalog_loads(self):
        cat = load_catalog()
        self.assertTrue(cat)
        self.assertEqual(cat[0].num, 1)
        self.assertNotIn("Part 1", cat[0].title)
        ids = [e.id for p in cat for e in p.exercises]
        self.assertEqual(len(ids), len(set(ids)))

    def test_find(self):
        cat = load_catalog()
        self.assertEqual(find_exercise(cat, "1.1").id, "1.1")
        self.assertEqual(find_exercise(cat, "01.01").id, "1.1")
        self.assertEqual(find_exercise(cat, "1-2").id, "1.2")
        self.assertEqual(find_exercise(cat, "greet_device").id, "1.1")
        self.assertIsNone(find_exercise(cat, "99.99"))
        self.assertEqual(find_part(cat, "1").num, 1)
        self.assertEqual(find_part(cat, "foundations").num, 1)

    def test_xp_from_kyu(self):
        cat = load_catalog()
        ex = cat[0].exercises[0]
        self.assertEqual(ex.xp, KYU_XP[ex.kyu])


class TestRunner(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_pass_and_fail_are_reported_per_test(self):
        ex = make_exercise(self.tmp, "def f(x):\n    return x + 1 if x == 1 else 0\n", TESTS)
        res = run_tests(ex)
        self.assertFalse(res.ok)
        self.assertEqual([t.status for t in res.tests], ["pass", "fail"])
        self.assertEqual([t.doc for t in res.tests], ["one", "two"])
        self.assertIn("3", res.tests[1].message)

    def test_all_pass(self):
        ex = make_exercise(self.tmp, "def f(x):\n    return x + 1\n", TESTS)
        res = run_tests(ex)
        self.assertTrue(res.ok)
        self.assertEqual(res.passed, 2)
        self.assertTrue(run_solution(ex).ok)

    def test_import_error(self):
        ex = make_exercise(self.tmp, "def f(x:\n", TESTS)
        res = run_tests(ex)
        self.assertFalse(res.ok)
        self.assertIn("SyntaxError", res.import_error)

    def test_timeout(self):
        ex = make_exercise(self.tmp, "def f(x):\n    while True: pass\n", TESTS, {"title": "t", "kyu": 8, "timeout_s": 1, "hints": ["h"], "tags": ["t"]})
        res = run_tests(ex)
        self.assertTrue(res.timed_out)
        self.assertFalse(res.ok)

    def test_learner_stdout_is_captured(self):
        ex = make_exercise(self.tmp, "print('debug!')\ndef f(x):\n    return x + 1\n", TESTS)
        res = run_tests(ex)
        self.assertTrue(res.ok)
        self.assertIn("debug!", res.stdout)


class TestProgress(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.ex = make_exercise(self.tmp, "def f(x):\n    return x + 1\n", TESTS, {"title": "t", "kyu": 6, "hints": ["a", "b"], "tags": ["t"], "time_limit_min": 5})
        self.p = Progress(self.tmp / "progress.json")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_first_try_bonus_and_persistence(self):
        s = self.p.record_run(self.ex, True)
        self.assertEqual(s["xp"], round(KYU_XP[6] * 1.25 * 1.1))
        self.assertIn("first_blood", s["new_badges"])
        again = Progress(self.tmp / "progress.json")
        self.assertTrue(again.is_solved(self.ex.id))
        self.assertEqual(again.xp, s["xp"])
        self.assertEqual(again.streak(), 1)

    def test_hints_reduce_xp_and_failed_attempts_remove_bonus(self):
        self.p.record_run(self.ex, False)
        self.assertEqual(self.p.reveal_hint(self.ex), "a")
        self.assertEqual(self.p.reveal_hint(self.ex), "b")
        self.assertIsNone(self.p.reveal_hint(self.ex))
        s = self.p.record_run(self.ex, True)
        self.assertEqual(s["xp"], round(KYU_XP[6] * 0.5 * 1.1))
        self.assertEqual(self.p.attempts(self.ex.id), 2)

    def test_peeking_cuts_xp(self):
        self.p.mark_peeked(self.ex)
        s = self.p.record_run(self.ex, True)
        self.assertEqual(s["xp"], max(1, round(KYU_XP[6] * 0.1)))

    def test_no_double_xp(self):
        self.p.record_run(self.ex, True)
        s = self.p.record_run(self.ex, True)
        self.assertEqual(s["xp"], 0)
        self.assertTrue(s["already_solved"])

    def test_rank_progression(self):
        kyu, title, frac, need = self.p.rank(100)
        self.assertEqual(kyu, 8)
        self.p.data["xp"] = 100
        kyu, title, frac, need = self.p.rank(100)
        self.assertEqual(kyu, 1)
        self.assertIsNone(need)

    def test_streak_breaks_after_a_gap(self):
        today = dt.date.today()
        self.p.data["days"] = [(today - dt.timedelta(days=d)).isoformat() for d in (0, 1, 2, 5)]
        self.assertEqual(self.p.streak(), 3)
        self.p.data["days"] = [(today - dt.timedelta(days=3)).isoformat()]
        self.assertEqual(self.p.streak(), 0)


if __name__ == "__main__":
    unittest.main()


class TestBackupRestore(unittest.TestCase):
    """All learner, source, archive and progress files live in a temporary fixture."""

    def setUp(self):
        import subprocess
        from course.workspace import Workspace

        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.tmp = Path(self.temporary.name)
        self.ex = make_exercise(self.tmp / "curriculum", "def f(x): return x + 1\n", TESTS)
        self.catalog = load_catalog(self.tmp / "curriculum")
        self.original = self.ex.exercise_file.read_bytes()
        for args in (("init", "-q"), ("add", "curriculum"),
                     ("-c", "user.name=Course tests", "-c", "user.email=course-tests@example.invalid",
                      "commit", "-qm", "fixture starter")):
            subprocess.run(["git", *args], cwd=self.tmp, check=True, capture_output=True)
        self.workspace = Workspace(self.tmp / "learner", repository_root=self.tmp)
        self.progress_path = self.tmp / "progress.json"
        Progress(self.progress_path).record_run(self.ex, True)
        self.member = "workspace/answers/part01_demo/01_demo/exercise.py"
        self.legacy = "curriculum/part01_demo/01_demo/exercise.py"
        self.archive_count = 0

    def tearDown(self):
        self.assertEqual(self.ex.exercise_file.read_bytes(), self.original)

    def archive(self, members, entries=None, progress=True):
        import zipfile

        self.archive_count += 1
        archive = self.tmp / ("archive-%s.zip" % self.archive_count)
        with zipfile.ZipFile(archive, "x") as zf:
            zf.writestr("manifest.json", json.dumps({"exercises": list(members) if entries is None else entries}))
            if progress:
                zf.writestr("progress.json", self.progress_path.read_bytes())
            for name, data in members.items():
                zf.writestr(name, data)
        return archive

    def restore(self, archive, progress_path=None, **kwargs):
        from course import backup as b

        return b.restore(archive, progress_path or self.tmp / "restored.json",
                         catalog=self.catalog, workspace=self.workspace, **kwargs)

    def test_backup_round_trip_includes_answers_scratch_helpers_and_recovery(self):
        from course import backup as b
        from course.workspace import Workspace, recovery_copy

        answer = self.workspace.ensure(self.ex)
        answer.write_text("# learner answer\n")
        recovered = recovery_copy(answer)
        scratch = self.workspace.ensure(self.ex, scratch=True)
        scratch.write_text("# scratch practice\n")
        helper = answer.with_name("helper.py")
        helper.write_text("# helper\n")
        migration = self.workspace.root / "recovery" / ("migration-" + "a" * 32) / "part01_demo" / "01_demo" / "exercise.py"
        migration.parent.mkdir(parents=True)
        migration.write_text("# migrated legacy answer\n")
        expected = {p.relative_to(self.workspace.root).as_posix(): p.read_bytes()
                    for p in (answer, recovered, scratch, helper, migration)}
        archive, count, has_progress = b.backup(self.catalog, self.progress_path,
                                               self.tmp / "backup.zip", self.workspace)
        self.assertEqual(count, 5)
        self.assertTrue(has_progress)
        self.assertEqual(set(b.inspect(archive)["exercises"]), {"workspace/" + p for p in expected})
        destination = Workspace(self.tmp / "fresh")
        result = b.restore(archive, self.tmp / "fresh-progress.json",
                           catalog=self.catalog, workspace=destination)
        self.assertEqual(len(result["exercises"]), 5)
        self.assertEqual(result["recoveries"], [])
        self.assertTrue(Progress(self.tmp / "fresh-progress.json").is_solved(self.ex.id))
        for name, data in expected.items():
            self.assertEqual((destination.root / name).read_bytes(), data)

    def test_backup_has_no_source_answers_and_never_replaces_an_archive(self):
        from course import backup as b

        archive, count, included = b.backup(self.catalog, self.progress_path,
                                            self.tmp / "named.zip", self.workspace)
        self.assertEqual(count, 0)
        self.assertTrue(included)
        original_archive = archive.read_bytes()
        with self.assertRaises(FileExistsError):
            b.backup(self.catalog, self.progress_path, archive, self.workspace)
        self.assertEqual(archive.read_bytes(), original_archive)
        first = b.backup(self.catalog, self.tmp / "missing.json", self.tmp / "backups", self.workspace)
        second = b.backup(self.catalog, self.tmp / "missing.json", self.tmp / "backups", self.workspace)
        self.assertNotEqual(first[0], second[0])
        self.assertFalse(first[2])

    def test_backup_preserves_conflicting_legacy_and_workspace_answers_without_migrating(self):
        from course import backup as b
        from course.workspace import Workspace

        workspace = self.workspace
        answer = workspace.ensure(self.ex)
        answer.write_text("# current workspace answer\n")
        legacy = b"# older answer awaiting migration\n"
        self.ex.exercise_file.write_bytes(legacy)
        try:
            archive, count, included = b.backup(self.catalog, self.progress_path,
                                                self.tmp / "legacy-backup.zip", workspace)
            self.assertEqual(count, 2)
            self.assertTrue(included)
            manifest = b.inspect(archive)
            self.assertEqual(len(manifest["legacy_recoveries"]), 1)
            recovery = manifest["legacy_recoveries"][0]
            self.assertTrue(recovery.startswith("workspace/recovery/migration-"))
            self.assertEqual(self.ex.exercise_file.read_bytes(), legacy)
            self.assertEqual(answer.read_text(), "# current workspace answer\n")
            self.assertFalse((workspace.root / "recovery").exists())
            destination = Workspace(self.tmp / "fresh", repository_root=self.tmp)
            result = b.restore(archive, self.tmp / "fresh-progress.json",
                               catalog=self.catalog, workspace=destination)
            self.assertEqual(len(result["exercises"]), 2)
            self.assertEqual(destination.answer_path(self.ex).read_text(), "# current workspace answer\n")
            self.assertEqual(destination.root.joinpath(*recovery.split("/")[1:]).read_bytes(), legacy)
        finally:
            # Only the temporary fixture is edited; keep the source-invariance
            # teardown assertion for every other backup/restore test.
            self.ex.exercise_file.write_bytes(self.original)

    def test_gitless_backup_preserves_unverified_source_only_as_recovery(self):
        from course import backup as b
        from course.workspace import Workspace

        with tempfile.TemporaryDirectory() as directory:
            download = Path(directory)
            ex = make_exercise(download / "curriculum", "# possibly an old answer\n", TESTS)
            catalog = load_catalog(download / "curriculum")
            workspace = Workspace(download / "learner", repository_root=download)
            source = ex.exercise_file.read_bytes()
            archive, count, _ = b.backup(catalog, self.progress_path,
                                         self.tmp / "gitless.zip", workspace)
            self.assertEqual(count, 1)
            manifest = b.inspect(archive)
            self.assertEqual(manifest["exercises"], manifest["legacy_recoveries"])
            self.assertFalse(workspace.root.exists())
            self.assertEqual(ex.exercise_file.read_bytes(), source)
            restored = Workspace(download / "restored", repository_root=download)
            b.restore(archive, download / "progress.json", catalog=catalog, workspace=restored)
            self.assertFalse(restored.answer_path(ex).exists())
            recovery = manifest["legacy_recoveries"][0]
            self.assertEqual(restored.root.joinpath(*recovery.split("/")[1:]).read_bytes(), source)

    def test_legacy_answers_route_to_workspace_and_unknown_exercises_are_skipped(self):
        unknown = "curriculum/part99_missing/01_unknown/exercise.py"
        archive = self.archive({self.legacy: b"# old answer\n", unknown: b"# unrelated\n"})
        result = self.restore(archive)
        self.assertEqual(self.workspace.answer_path(self.ex).read_bytes(), b"# old answer\n")
        self.assertEqual(result["skipped"], [unknown])
        self.assertFalse((self.tmp / "curriculum" / "part99_missing").exists())

    def test_late_answer_conflict_prevents_all_writes_even_in_exercises_only(self):
        answer = self.workspace.ensure(self.ex)
        answer.write_text("# keep my work\n")
        helper = self.member.replace("exercise.py", "helper.py")
        archive = self.archive({helper: b"# new helper", self.member: b"# incoming"})
        for options in ({}, {"exercises_only": True}):
            with self.subTest(options=options), self.assertRaises(FileExistsError):
                self.restore(archive, **options)
            self.assertFalse((self.tmp / "restored.json").exists())
            self.assertFalse(answer.with_name("helper.py").exists())
            self.assertEqual(answer.read_text(), "# keep my work\n")
            self.assertEqual(list(answer.parent.glob("*.bak.*")), [])

    def test_progress_conflict_prevents_answer_write_and_force_keeps_unique_copies(self):
        answer = self.workspace.ensure(self.ex)
        answer.write_text("# prior answer\n")
        destination_progress = self.tmp / "existing-progress.json"
        destination_progress.write_text('{"xp": 77}')
        archive = self.archive({self.member: b"# incoming answer\n"})
        with self.assertRaises(FileExistsError):
            self.restore(archive, destination_progress)
        first = self.restore(archive, destination_progress, force=True)
        self.assertEqual(len(first["recoveries"]), 2)
        first_copies = {name: Path(name).read_bytes() for name in first["recoveries"]}
        self.assertEqual(set(first_copies.values()), {b'{"xp": 77}', b"# prior answer\n"})
        second = self.restore(archive, destination_progress, force=True)
        self.assertTrue(set(first["recoveries"]).isdisjoint(second["recoveries"]))
        for name, data in first_copies.items():
            self.assertEqual(Path(name).read_bytes(), data)
        self.assertEqual(answer.read_bytes(), b"# incoming answer\n")

    def test_progress_only_and_exercises_only_preserve_excluded_destinations(self):
        archive = self.archive({self.member: b"# answer"})
        first = self.restore(archive, progress_only=True)
        self.assertEqual(first["exercises"], [])
        self.assertFalse(self.workspace.answer_path(self.ex).exists())
        progress_before = (self.tmp / "restored.json").read_bytes()
        second = self.restore(archive, exercises_only=True)
        self.assertIsNone(second["progress"])
        self.assertEqual((self.tmp / "restored.json").read_bytes(), progress_before)
        self.assertEqual(self.workspace.answer_path(self.ex).read_bytes(), b"# answer")
        with self.assertRaises(ValueError):
            self.restore(archive, exercises_only=True, progress_only=True)

    def test_traversal_paths_are_rejected_before_progress_write(self):
        for name in ("../outside.py", "/outside.py", "workspace/answers/part01_demo/01_demo/../exercise.py",
                     "workspace\\answers\\part01_demo\\01_demo\\exercise.py", "workspace//answers/exercise.py"):
            with self.subTest(name=name):
                archive = self.archive({self.member: b"# valid", name: b"# unsafe"})
                with self.assertRaises(ValueError):
                    self.restore(archive)
                self.assertFalse((self.tmp / "restored.json").exists())
                self.assertFalse(self.workspace.root.exists())

    def test_duplicate_members_manifest_entries_and_destinations_are_rejected(self):
        import warnings
        import zipfile

        duplicate = self.archive({self.member: b"# first"})
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(duplicate, "a") as zf:
                zf.writestr(self.member, b"# second")
        archives = [duplicate,
                    self.archive({self.member: b"# data"}, [self.member, self.member]),
                    self.archive({self.member: b"# new", self.legacy: b"# legacy"}),
                    self.archive({self.member.replace("exercise.py", "helper.py"): b"# lower",
                                  self.member.replace("exercise.py", "HELPER.py"): b"# upper"})]
        for archive in archives:
            with self.subTest(archive=archive), self.assertRaises(ValueError):
                self.restore(archive)
            self.assertFalse((self.tmp / "restored.json").exists())
            self.assertFalse(self.workspace.root.exists())

    def test_archive_symlink_is_rejected_without_writes(self):
        import stat
        import zipfile

        archive = self.archive({})
        info = zipfile.ZipInfo(self.member)
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        with zipfile.ZipFile(archive, "a") as zf:
            zf.writestr(info, "/tmp/outside")
        with self.assertRaises(ValueError):
            self.restore(archive)
        self.assertFalse((self.tmp / "restored.json").exists())

    def test_destination_symlinks_are_rejected_without_touching_link_targets(self):
        from course import backup as b

        outside = self.tmp / "outside"
        outside.mkdir()
        self.workspace.root.mkdir()
        (self.workspace.root / "answers").symlink_to(outside, target_is_directory=True)
        archive = self.archive({self.member: b"# incoming"})
        with self.assertRaises(ValueError):
            self.restore(archive, force=True)
        with self.assertRaises(ValueError):
            b.backup(self.catalog, self.progress_path, self.tmp / "linked.zip", self.workspace)
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse((self.tmp / "restored.json").exists())
        linked_progress = self.tmp / "linked-progress.json"
        linked_progress.symlink_to(self.progress_path)
        before = self.progress_path.read_bytes()
        with self.assertRaises(ValueError):
            self.restore(archive, linked_progress, force=True, progress_only=True)
        self.assertEqual(self.progress_path.read_bytes(), before)

    def test_invalid_progress_is_rejected_before_answers_are_written(self):
        import zipfile

        archive = self.archive({self.member: b"# answer"}, progress=False)
        with zipfile.ZipFile(archive, "a") as zf:
            zf.writestr("progress.json", "not JSON")
        with self.assertRaises(ValueError):
            self.restore(archive)
        self.assertFalse(self.workspace.root.exists())

    def test_progress_and_answer_destination_collisions_do_not_write_anything(self):
        archive = self.archive({self.member: b"# answer"})
        answer = self.workspace.answer_path(self.ex)
        for progress_target in (answer.parent, answer.parent / "unused" / ".." / answer.name):
            with self.subTest(target=progress_target), self.assertRaises(ValueError):
                self.restore(archive, progress_target)
            self.assertFalse(self.workspace.root.exists())

    def test_inspect_and_restore_reject_malformed_manifest_shapes(self):
        import zipfile
        from course import backup as b

        for number, value in enumerate(([], {"exercises": "not a list"}, {"exercises": [17]})):
            archive = self.tmp / ("malformed-%s.zip" % number)
            with zipfile.ZipFile(archive, "x") as zf:
                zf.writestr("manifest.json", json.dumps(value))
                zf.writestr("progress.json", self.progress_path.read_bytes())
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    b.inspect(archive)
                with self.assertRaises(ValueError):
                    self.restore(archive)
                self.assertFalse((self.tmp / "restored.json").exists())


class TestLessons(unittest.TestCase):
    SAMPLE = """# Sample

--- teach
### One idea
Text.
```python
x = 1
```

--- quiz
Pick one
- [ ] no
- [x] yes
> because

--- predict
What prints?
```python
print(7 // 2)
```
answer: 3 | 3.0
> floor

--- fill
Blank
```python
name = raw.___()
```
answer: strip
> strip

--- exercise 1.1

--- recap
- done
"""

    def setUp(self):
        from course.lessons import parse_lesson

        self.tmp = Path(tempfile.mkdtemp())
        f = self.tmp / "01_sample.md"
        f.write_text(self.SAMPLE)
        self.lesson = parse_lesson(f, 1, 1, "sample")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_parse(self):
        l = self.lesson
        self.assertEqual(l.title, "Sample")
        self.assertEqual([c.kind for c in l.cards], ["teach", "quiz", "predict", "fill", "exercise", "recap"])
        self.assertIn("x = 1", l.cards[0].body)
        self.assertEqual(l.cards[1].options, ["no", "yes"])
        self.assertEqual(l.cards[1].correct, 1)
        self.assertEqual(l.cards[2].answers, ["3", "3.0"])
        self.assertEqual(l.cards[3].explanation, "strip")
        self.assertEqual(l.exercise_ids, ["1.1"])
        self.assertEqual(l.xp, 3)

    def test_check_answers(self):
        quiz, predict, fill = self.lesson.cards[1], self.lesson.cards[2], self.lesson.cards[3]
        self.assertTrue(quiz.check("b"))
        self.assertTrue(quiz.check("2"))
        self.assertTrue(quiz.check("yes"))
        self.assertFalse(quiz.check("a"))
        self.assertTrue(predict.check(" 3 "))
        self.assertTrue(predict.check("'3'"))
        self.assertFalse(predict.check("4"))
        self.assertTrue(fill.check("strip"))
        self.assertFalse(fill.check("lower"))

    def test_validate_real_part1(self):
        from course.lessons import load_lessons, validate_lesson

        cat = load_catalog()
        lessons = load_lessons(cat[0])
        self.assertEqual(len(lessons), len(cat[0].exercises))
        for l in lessons:
            self.assertEqual(validate_lesson(l, cat[0]), [], l.id)

    def test_card_progress_xp(self):
        p = Progress(self.tmp / "p.json")
        self.assertEqual(p.record_card("1.1", 1, checkable=True, correct=True), 1)
        self.assertEqual(p.record_card("1.1", 1, checkable=True, correct=True), 0)   # no double xp
        self.assertEqual(p.record_card("1.1", 2, checkable=True, correct=False), 0)
        self.assertFalse(p.card_state("1.1", 2)["done"])
        self.assertEqual(p.record_card("1.1", 2, checkable=True, correct=True), 0)   # second try: done, no xp
        self.assertTrue(p.card_state("1.1", 2)["done"])
        self.assertEqual(p.record_card("1.1", 3, checkable=True, correct=False), 0)
        self.assertEqual(p.record_card("1.1", 3, checkable=True, correct=False), 0)
        self.assertTrue(p.card_state("1.1", 3)["done"])   # two misses: move on
        self.assertEqual(p.xp, 1)
        done, total, complete = p.lesson_progress(self.lesson)
        self.assertEqual((done, total, complete), (3, 6, False))


class TestCodeCards(unittest.TestCase):
    SRC = """# Code

--- teach
### Idea
Text.

--- code
Print the hostname in lowercase.
```python
hostname = "MBP-J-DOE"
```
expect: mbp-j-doe
check: hostname == "MBP-J-DOE"
solution: print(hostname.lower())
> lower() returns a lowercase copy.

--- code
Set `n` to the number of characters in `serial`.
```python
serial = "C02XG1234ABC"
```
check: n == 12
solution: n = len(serial)
> len counts characters.

--- quiz
Q
- [x] a
- [ ] b
> e

--- exercise 1.1
"""

    def setUp(self):
        from course.lessons import parse_lesson

        self.tmp = Path(tempfile.mkdtemp())
        f = self.tmp / "01_code.md"
        f.write_text(self.SRC)
        self.lesson = parse_lesson(f, 1, 1, "code")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_parse_and_validate(self):
        from course.lessons import validate_lesson

        c = self.lesson.cards[1]
        self.assertEqual(c.kind, "code")
        self.assertEqual(c.expect, "mbp-j-doe")
        self.assertEqual(c.checks, ['hostname == "MBP-J-DOE"'])
        self.assertEqual(c.solution, "print(hostname.lower())")
        self.assertEqual(c.starter, 'hostname = "MBP-J-DOE"\n')
        self.assertEqual(c.prompt, "Print the hostname in lowercase.")
        self.assertTrue(c.checkable)
        self.assertEqual(self.lesson.xp, 3)
        self.assertEqual(validate_lesson(self.lesson, load_catalog()[0]), [])

    def test_grading(self):
        from course.runner import run_code_card

        c = self.lesson.cards[1]
        self.assertTrue(run_code_card(c, c.starter + c.solution + "\n").ok)
        bad = run_code_card(c, c.starter + "print(hostname)\n")
        self.assertFalse(bad.ok)
        self.assertEqual([t.status for t in bad.tests], ["fail", "pass"])
        c2 = self.lesson.cards[2]
        self.assertTrue(run_code_card(c2, c2.starter + "n = len(serial)\n").ok)
        self.assertFalse(run_code_card(c2, c2.starter + "n = 11\n").ok)
        self.assertFalse(run_code_card(c2, c2.starter + "print(\n").ok)
