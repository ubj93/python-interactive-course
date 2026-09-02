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
