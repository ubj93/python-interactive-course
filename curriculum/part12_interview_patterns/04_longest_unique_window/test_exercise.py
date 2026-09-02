import unittest

from exercise import longest_unique_window


class TestLongestUniqueWindow(unittest.TestCase):
    def test_example(self):
        """Finds the longest run of distinct hosts"""
        self.assertEqual(longest_unique_window(["mbp-1", "mbp-2", "mbp-1", "mbp-3"]), 3)

    def test_all_distinct(self):
        """All-distinct input gives its full length"""
        self.assertEqual(longest_unique_window(["a", "b", "c", "d"]), 4)

    def test_all_same(self):
        """Repeating a single host gives 1"""
        self.assertEqual(longest_unique_window(["x", "x", "x"]), 1)

    def test_works_on_strings(self):
        """A string is a sequence of characters"""
        self.assertEqual(longest_unique_window("abcabcbb"), 3)
        self.assertEqual(longest_unique_window("pwwkew"), 3)

    def test_empty_and_single(self):
        """Empty gives 0, a single element gives 1"""
        self.assertEqual(longest_unique_window([]), 0)
        self.assertEqual(longest_unique_window(""), 0)
        self.assertEqual(longest_unique_window([42]), 1)

    def test_repeat_outside_window_does_not_shrink_it(self):
        """A repeat already behind the window start must not move the start backwards"""
        self.assertEqual(longest_unique_window("abbac"), 3)
        self.assertEqual(longest_unique_window("abba"), 2)

    def test_best_window_at_the_end(self):
        """The longest run may be the tail of the input"""
        self.assertEqual(longest_unique_window([1, 1, 2, 3, 4]), 4)

    def test_large_input(self):
        """20,500 check-ins cycling through 2,000 hosts with 500 new hosts spliced in (answer 2,500)"""
        cycle = 2000
        log = [f"host-{i % cycle:04d}" for i in range(20000)]
        extra = [f"host-{cycle + i:04d}" for i in range(500)]
        log = log[:10000] + extra + log[10000:]
        self.assertEqual(longest_unique_window(log), 2500)


if __name__ == "__main__":
    unittest.main()
