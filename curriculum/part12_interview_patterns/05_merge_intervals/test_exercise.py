import unittest

from exercise import merge_intervals


class TestMergeIntervals(unittest.TestCase):
    def test_disjoint_sorted(self):
        """Non-overlapping sorted windows come back unchanged"""
        self.assertEqual(merge_intervals([(0, 10), (20, 30)]), [(0, 10), (20, 30)])

    def test_overlap_merges(self):
        """Overlapping windows merge into one"""
        self.assertEqual(merge_intervals([(540, 600), (720, 780), (590, 660)]), [(540, 660), (720, 780)])

    def test_touching_merges(self):
        """Windows that touch at a boundary merge"""
        self.assertEqual(merge_intervals([(60, 120), (120, 180)]), [(60, 180)])

    def test_unsorted_input(self):
        """Input order does not matter; output is sorted by start"""
        self.assertEqual(merge_intervals([(300, 360), (0, 30), (100, 200), (150, 250)]), [(0, 30), (100, 250), (300, 360)])

    def test_contained_window(self):
        """A window inside another disappears into it (the end must not shrink)"""
        self.assertEqual(merge_intervals([(0, 100), (10, 20), (30, 40)]), [(0, 100)])

    def test_zero_length(self):
        """Zero-length windows merge when touching and otherwise stand alone"""
        self.assertEqual(merge_intervals([(5, 5), (5, 10), (20, 20)]), [(5, 10), (20, 20)])

    def test_empty_and_invalid(self):
        """Empty input gives []; start > end raises ValueError; input is not modified"""
        self.assertEqual(merge_intervals([]), [])
        with self.assertRaises(ValueError):
            merge_intervals([(10, 5)])
        windows = [(20, 30), (0, 10)]
        merge_intervals(windows)
        self.assertEqual(windows, [(20, 30), (0, 10)])

    def test_large_input(self):
        """10,000 windows in reverse order that pair up into 5,000 merged ones"""
        windows = [(i * 30, i * 30 + 10) for i in range(5000)] + [(i * 30 + 10, i * 30 + 20) for i in range(5000)]
        windows.reverse()
        expected = [(i * 30, i * 30 + 20) for i in range(5000)]
        self.assertEqual(merge_intervals(windows), expected)


if __name__ == "__main__":
    unittest.main()
