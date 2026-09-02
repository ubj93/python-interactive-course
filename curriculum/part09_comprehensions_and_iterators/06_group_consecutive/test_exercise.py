import unittest

from exercise import group_consecutive, longest_failing_streak


class TestGroupConsecutive(unittest.TestCase):
    def test_basic_runs(self):
        """Adjacent builds with the same status form one run"""
        results = [("b1", "pass"), ("b2", "fail"), ("b3", "fail"), ("b4", "pass"), ("b5", "fail")]
        self.assertEqual(
            group_consecutive(results),
            [("pass", ["b1"]), ("fail", ["b2", "b3"]), ("pass", ["b4"]), ("fail", ["b5"])],
        )

    def test_empty_and_single(self):
        """Empty input gives no runs; one build gives one run"""
        self.assertEqual(group_consecutive([]), [])
        self.assertEqual(group_consecutive([("b1", "fail")]), [("fail", ["b1"])])

    def test_one_long_run(self):
        """All the same status is a single run"""
        results = [(f"b{i}", "pass") for i in range(1, 6)]
        self.assertEqual(group_consecutive(results), [("pass", ["b1", "b2", "b3", "b4", "b5"])])

    def test_non_adjacent_are_separate(self):
        """The same status separated by another status is two runs, not one"""
        results = [("b1", "fail"), ("b2", "pass"), ("b3", "fail")]
        self.assertEqual(group_consecutive(results), [("fail", ["b1"]), ("pass", ["b2"]), ("fail", ["b3"])])
        self.assertEqual(len(group_consecutive(results)), 3)

    def test_longest_failing_streak(self):
        """The longest run of fails is returned as build ids"""
        results = [("b1", "fail"), ("b2", "pass"), ("b3", "fail"), ("b4", "fail"), ("b5", "fail"), ("b6", "pass"), ("b7", "fail")]
        self.assertEqual(longest_failing_streak(results), ["b3", "b4", "b5"])

    def test_tie_takes_the_earliest(self):
        """Equal-length failing runs resolve to the first one"""
        results = [("b1", "fail"), ("b2", "fail"), ("b3", "pass"), ("b4", "fail"), ("b5", "fail")]
        self.assertEqual(longest_failing_streak(results), ["b1", "b2"])

    def test_no_failures(self):
        """Without any fail the streak is empty; passes never count"""
        self.assertEqual(longest_failing_streak([("b1", "pass"), ("b2", "pass")]), [])
        self.assertEqual(longest_failing_streak([]), [])


if __name__ == "__main__":
    unittest.main()
