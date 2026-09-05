import math
import random
import unittest

from exercise import bisect_first_bad


def make_predicate(n_builds, first_bad, calls):
    """Return a monotone is_bad(build) that records every call in `calls`."""

    def is_bad(build):
        if not 1 <= build <= n_builds:
            raise AssertionError(f"is_bad called with build {build}, outside 1..{n_builds}")
        calls.append(build)
        return first_bad is not None and build >= first_bad

    return is_bad


def budget(n_builds):
    return math.ceil(math.log2(n_builds)) + 1


class TestBisectFirstBad(unittest.TestCase):
    def test_single_build(self):
        """One build: bad gives 1, good gives None"""
        self.assertEqual(bisect_first_bad(1, make_predicate(1, 1, [])), 1)
        self.assertIsNone(bisect_first_bad(1, make_predicate(1, None, [])))

    def test_middle(self):
        """Finds a first bad build in the middle of the range"""
        self.assertEqual(bisect_first_bad(5, make_predicate(5, 4, [])), 4)
        self.assertEqual(bisect_first_bad(10, make_predicate(10, 7, [])), 7)

    def test_all_bad_and_none_bad(self):
        """All bad gives 1; none bad gives None"""
        self.assertEqual(bisect_first_bad(8, make_predicate(8, 1, [])), 1)
        self.assertIsNone(bisect_first_bad(8, make_predicate(8, None, [])))

    def test_zero_builds(self):
        """Zero builds gives None without calling the predicate"""
        calls = []
        self.assertIsNone(bisect_first_bad(0, make_predicate(0, None, calls)))
        self.assertEqual(calls, [])

    def test_every_answer_for_small_n(self):
        """Correct for every possible first bad build with n = 1..16, within the call budget"""
        for n in range(1, 17):
            for first_bad in list(range(1, n + 1)) + [None]:
                calls = []
                result = bisect_first_bad(n, make_predicate(n, first_bad, calls))
                self.assertEqual(result, first_bad, f"n={n} first_bad={first_bad}")
                self.assertLessEqual(len(calls), budget(n), f"n={n} first_bad={first_bad} calls={calls}")

    def test_call_budget_thousand(self):
        """1,000 builds are bisected in at most 11 predicate calls"""
        calls = []
        self.assertEqual(bisect_first_bad(1000, make_predicate(1000, 617, calls)), 617)
        self.assertLessEqual(len(calls), 11, calls)

    def test_never_out_of_range(self):
        """The predicate is never asked about build 0 or n_builds + 1"""
        for first_bad in (1, 2, 3, None):
            bisect_first_bad(3, make_predicate(3, first_bad, []))

    def test_large_range(self):
        """A billion builds take at most 31 calls"""
        n = 10 ** 9
        calls = []
        self.assertEqual(bisect_first_bad(n, make_predicate(n, 123456789, calls)), 123456789)
        self.assertLessEqual(len(calls), 31, len(calls))
        calls = []
        self.assertIsNone(bisect_first_bad(n, make_predicate(n, None, calls)))
        self.assertLessEqual(len(calls), 31, len(calls))

    def test_generalization_seeded(self):
        """Generalization: varied transition points and exact integer boundaries (seed 1207)"""
        rng = random.Random(1207)
        cases = [(0, None)]
        sizes = [1, 2, 3, 31, 32, 33, 255, 256, 257]
        sizes += [rng.randint(1, 4096) for _ in range(30)]
        for n in sizes:
            for first_bad in (1, n, rng.randint(1, n), None):
                # Scan a short truth table; no binary-search logic in the oracle.
                flags = [first_bad is not None and build >= first_bad for build in range(1, n + 1)]
                expected = next((build for build, bad in enumerate(flags, 1) if bad), None)
                cases.append((n, expected))
        for _ in range(8):
            n = 2 ** 53 + rng.randint(1, 2048)
            cases.extend([(n, n), (n, n - rng.randint(1, 100)), (n, None)])
        for n, expected in cases:
            # bit_length computes ceil(log2(n)) exactly, including huge integers.
            limit = (n - 1).bit_length() + 1 if n else 0
            calls = []
            context = f"n={n}, first_bad={expected}"

            def is_bad(build):
                self.assertTrue(isinstance(build, int) and 1 <= build <= n,
                                f"{context}; predicate called outside integer builds: {build!r}")
                calls.append(build)
                self.assertLessEqual(len(calls), limit, f"{context}; exceeded {limit} predicate calls")
                return expected is not None and build >= expected

            self.assertEqual(bisect_first_bad(n, is_bad), expected, context)
            self.assertLessEqual(len(calls), limit, context)


if __name__ == "__main__":
    unittest.main()
