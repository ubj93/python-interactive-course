import unittest
from datetime import datetime, timedelta

from exercise import pairwise_deltas

T0 = datetime(2024, 5, 1, 9, 0, 0)


def times(*offsets_seconds):
    return [T0 + timedelta(seconds=s) for s in offsets_seconds]


class TestPairwiseDeltas(unittest.TestCase):
    def test_basic_gaps(self):
        """Seconds between each consecutive pair"""
        self.assertEqual(pairwise_deltas(times(0, 30, 900)), [30.0, 870.0])

    def test_fewer_than_two(self):
        """Empty and single-element input give an empty list"""
        self.assertEqual(pairwise_deltas([]), [])
        self.assertEqual(pairwise_deltas([T0]), [])

    def test_result_is_floats_with_one_fewer_element(self):
        """Every delta is a float and the list is one shorter than the input"""
        result = pairwise_deltas(times(0, 60, 120, 180, 240))
        self.assertEqual(len(result), 4)
        self.assertTrue(all(isinstance(x, float) for x in result))
        self.assertEqual(result, [60.0, 60.0, 60.0, 60.0])

    def test_equal_and_fractional_gaps(self):
        """Repeated timestamps give 0.0; microseconds give fractions"""
        self.assertEqual(pairwise_deltas([T0, T0, T0]), [0.0, 0.0])
        self.assertEqual(pairwise_deltas([T0, T0 + timedelta(milliseconds=250)]), [0.25])

    def test_spans_days(self):
        """Gaps longer than a day are reported in seconds"""
        self.assertEqual(pairwise_deltas([T0, T0 + timedelta(days=2, hours=1)]), [2 * 86400 + 3600.0])

    def test_accepts_tuple_input(self):
        """A tuple of datetimes works the same as a list"""
        self.assertEqual(pairwise_deltas(tuple(times(0, 5, 15))), [5.0, 10.0])

    def test_out_of_order_raises(self):
        """A timestamp earlier than its predecessor raises ValueError naming the index"""
        with self.assertRaises(ValueError) as ctx:
            pairwise_deltas(times(0, 60, 30, 90))
        self.assertIn("2", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
