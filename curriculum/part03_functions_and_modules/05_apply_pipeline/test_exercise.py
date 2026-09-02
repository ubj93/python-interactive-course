import unittest

from exercise import apply_pipeline


class TestApplyPipeline(unittest.TestCase):
    def test_no_steps(self):
        """No steps returns the value unchanged"""
        self.assertEqual(apply_pipeline("x", []), "x")
        self.assertEqual(apply_pipeline(5, []), 5)

    def test_steps_in_order(self):
        """Steps run left to right, feeding each other"""
        self.assertEqual(apply_pipeline("  MBP-J-DOE ", [str.strip, str.lower]), "mbp-j-doe")
        self.assertEqual(apply_pipeline(3, [lambda n: n + 1, lambda n: n * 10]), 40)
        self.assertEqual(apply_pipeline(3, [lambda n: n * 10, lambda n: n + 1]), 31)

    def test_none_stops_pipeline(self):
        """A step returning None stops the pipeline and the result is None"""
        reject_lab = lambda h: None if h.startswith("lab-") else h
        self.assertIsNone(apply_pipeline("LAB-01", [str.lower, reject_lab, str.upper]))
        self.assertEqual(apply_pipeline("MBP-01", [str.lower, reject_lab, str.upper]), "MBP-01")

    def test_later_steps_not_called_after_none(self):
        """Steps after the one that returned None are never run"""
        calls = []

        def record(tag):
            def step(v):
                calls.append(tag)
                return v
            return step

        def drop(v):
            calls.append("drop")
            return None

        self.assertIsNone(apply_pipeline("x", [record("a"), drop, record("b"), record("c")]))
        self.assertEqual(calls, ["a", "drop"])

    def test_falsy_values_keep_going(self):
        """0, empty string and empty list are not None and continue through the pipeline"""
        self.assertEqual(apply_pipeline(0, [lambda n: n + 1, lambda n: n * 2]), 2)
        self.assertEqual(apply_pipeline("abc", [lambda s: "", lambda s: s + "!"]), "!")
        self.assertEqual(apply_pipeline([1], [lambda xs: [], len]), 0)

    def test_initial_none(self):
        """A None starting value returns None and calls no step"""
        calls = []
        self.assertIsNone(apply_pipeline(None, [lambda v: calls.append(v) or v]))
        self.assertEqual(calls, [])

    def test_non_callable_raises_before_running(self):
        """A non-callable step raises TypeError and no step runs, even earlier valid ones"""
        calls = []

        def first(v):
            calls.append("first")
            return v

        with self.assertRaises(TypeError):
            apply_pipeline("x", [first, "not a function"])
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
