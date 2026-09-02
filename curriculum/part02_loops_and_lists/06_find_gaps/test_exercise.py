import unittest

from exercise import find_gaps


class TestFindGaps(unittest.TestCase):
    def test_no_gaps(self):
        """Consecutive tags have no gaps"""
        self.assertEqual(find_gaps([1, 2, 3, 4]), [])

    def test_single_missing_number(self):
        """A gap of one number is (n, n)"""
        self.assertEqual(find_gaps([1, 2, 4]), [(3, 3)])

    def test_multi_number_gap(self):
        """A gap spanning several numbers is one (start, end) tuple"""
        self.assertEqual(find_gaps([10, 15]), [(11, 14)])

    def test_several_gaps(self):
        """Several gaps come back in ascending order"""
        self.assertEqual(find_gaps([100, 101, 102, 105, 106, 110]), [(103, 104), (107, 109)])

    def test_duplicates_are_not_gaps(self):
        """Repeated tags do not create gaps"""
        self.assertEqual(find_gaps([7, 7, 9]), [(8, 8)])
        self.assertEqual(find_gaps([1, 1, 2, 2, 3]), [])

    def test_empty_and_single(self):
        """Empty input or a single tag has no gaps"""
        self.assertEqual(find_gaps([]), [])
        self.assertEqual(find_gaps([42]), [])
        self.assertEqual(find_gaps([42, 42]), [])

    def test_unsorted_raises(self):
        """Input that is not sorted ascending raises ValueError"""
        with self.assertRaises(ValueError):
            find_gaps([3, 1, 2])
        with self.assertRaises(ValueError):
            find_gaps([1, 5, 4])

    def test_input_not_modified(self):
        """The input list is not modified"""
        tags = [5, 9, 7]
        try:
            find_gaps(tags)
        except ValueError:
            pass
        self.assertEqual(tags, [5, 9, 7])
        tags = [1, 3]
        find_gaps(tags)
        self.assertEqual(tags, [1, 3])


if __name__ == "__main__":
    unittest.main()
