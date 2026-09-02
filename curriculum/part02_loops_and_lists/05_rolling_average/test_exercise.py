import unittest

from exercise import rolling_average


class TestRollingAverage(unittest.TestCase):
    def test_window_of_one(self):
        """A window of 1 returns each sample as a float"""
        self.assertEqual(rolling_average([5, 7, 9], 1), [5.0, 7.0, 9.0])

    def test_window_of_two(self):
        """Pairs are averaged after the first sample"""
        self.assertEqual(rolling_average([10, 20, 30, 40], 2), [10.0, 15.0, 25.0, 35.0])

    def test_short_windows_at_start(self):
        """Before the window fills, the average covers what is available"""
        self.assertEqual(rolling_average([3, 6, 9, 12, 15], 3), [3.0, 4.5, 6.0, 9.0, 12.0])

    def test_window_larger_than_list(self):
        """A window bigger than the list averages everything so far"""
        self.assertEqual(rolling_average([2, 4, 6], 10), [2.0, 3.0, 4.0])

    def test_empty(self):
        """Empty input gives an empty list"""
        self.assertEqual(rolling_average([], 3), [])

    def test_rounding(self):
        """Values are rounded to two decimals"""
        self.assertEqual(rolling_average([1, 2, 2], 3), [1.0, 1.5, 1.67])
        self.assertEqual(rolling_average([0.1, 0.2, 0.4], 2), [0.1, 0.15, 0.3])

    def test_invalid_window_raises(self):
        """A window under 1 raises ValueError"""
        with self.assertRaises(ValueError):
            rolling_average([1, 2, 3], 0)
        with self.assertRaises(ValueError):
            rolling_average([1, 2, 3], -1)

    def test_input_not_modified(self):
        """The samples list is left as it was"""
        samples = [4, 8, 12]
        rolling_average(samples, 2)
        self.assertEqual(samples, [4, 8, 12])


if __name__ == "__main__":
    unittest.main()
