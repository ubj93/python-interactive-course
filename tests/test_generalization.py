"""Regression checks for the three public, seeded generalization tests."""
from pathlib import Path
import tempfile
import time
import unittest

from course.catalog import Exercise
from course.runner import run_tests
from generalization_cases import grading_cases


class TestGeneralization(unittest.TestCase):
    def test_references_and_plausible_wrong_implementations(self):
        for case in grading_cases():
            with self.subTest(case=case["name"]), tempfile.TemporaryDirectory() as tmp:
                directory = Path(tmp)
                for name, source in case["files"].items():
                    (directory / name).write_text(source, encoding="utf-8")
                started = time.perf_counter()
                result = run_tests(Exercise(12, 0, case["slug"], directory, {"timeout_s": 5}))
                elapsed = time.perf_counter() - started
                failures = [test.message for test in result.tests if test.status != "pass"]
                self.assertFalse(result.timed_out, case["name"])
                self.assertIsNone(result.import_error, result.import_error)
                self.assertFalse(result.crashed, result.crashed)
                self.assertEqual(result.ok, case["passes"], failures)
                self.assertIn("test_generalization_seeded", [test.name for test in result.tests])
                if "full suite" not in case["name"]:
                    self.assertEqual(len(result.tests), 1)
                if not case["passes"]:
                    self.assertEqual(result.tests[0].status, "fail")
                    self.assertLess(len(failures[0]), 400, failures[0])
                print(f"{case['name']}: {elapsed:.3f}s" + ("; " + failures[0] if failures else ""))


if __name__ == "__main__":
    unittest.main()
