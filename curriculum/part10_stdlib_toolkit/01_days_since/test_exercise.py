import unittest
from datetime import datetime, timedelta, timezone

from exercise import days_since, parse_timestamp

UTC = timezone.utc
NOW = datetime(2024, 5, 4, 9, 0, 0, tzinfo=UTC)


class TestParseTimestamp(unittest.TestCase):
    def test_z_suffix(self):
        """A trailing Z parses to an aware UTC datetime"""
        dt = parse_timestamp("2024-05-01T10:00:00Z")
        self.assertEqual(dt, datetime(2024, 5, 1, 10, 0, tzinfo=UTC))
        self.assertEqual(dt.utcoffset(), timedelta(0))

    def test_offset_is_converted_to_utc(self):
        """+02:00 is the same instant as 2 hours earlier in UTC"""
        dt = parse_timestamp("2024-05-01T12:00:00+02:00")
        self.assertEqual(dt, datetime(2024, 5, 1, 10, 0, tzinfo=UTC))
        self.assertEqual(dt.hour, 10)
        self.assertEqual(dt.utcoffset(), timedelta(0))

    def test_naive_is_assumed_utc(self):
        """A timestamp without an offset is treated as UTC"""
        dt = parse_timestamp("  2024-05-01 10:00:00\n")
        self.assertIsNotNone(dt.tzinfo)
        self.assertEqual(dt, datetime(2024, 5, 1, 10, 0, tzinfo=UTC))

    def test_bad_input_raises(self):
        """None, empty and unparseable strings raise ValueError"""
        for raw in [None, "", "   ", "yesterday", "2024-13-01T00:00:00Z"]:
            with self.assertRaises(ValueError, msg=repr(raw)):
                parse_timestamp(raw)


class TestDaysSince(unittest.TestCase):
    def test_whole_days(self):
        """Exact multiples of 24 hours count as whole days"""
        self.assertEqual(days_since("2024-05-01T09:00:00Z", NOW), 3)
        self.assertEqual(days_since("2024-05-04T09:00:00Z", NOW), 0)

    def test_rounds_down(self):
        """2 days and 23 hours is 2 days"""
        self.assertEqual(days_since("2024-05-01T10:00:00Z", NOW), 2)
        self.assertEqual(days_since("2024-05-01T12:00:00+02:00", NOW), 2)

    def test_future_is_zero(self):
        """A check-in in the future gives 0, not a negative number"""
        self.assertEqual(days_since("2024-05-09T00:00:00Z", NOW), 0)

    def test_naive_now_is_utc(self):
        """A naive now is treated as UTC instead of raising"""
        self.assertEqual(days_since("2024-05-01T09:00:00Z", datetime(2024, 5, 4, 9, 0)), 3)


if __name__ == "__main__":
    unittest.main()
