import unittest

from exercise import make_checkin_tracker, make_counter


class TestMakeCounter(unittest.TestCase):
    def test_counts_from_zero(self):
        """Default counter yields 0, 1, 2, ..."""
        counter = make_counter()
        self.assertEqual([counter(), counter(), counter()], [0, 1, 2])

    def test_start_and_step(self):
        """start and step are honoured; start is returned first"""
        counter = make_counter(100, 5)
        self.assertEqual([counter(), counter(), counter()], [100, 105, 110])
        self.assertEqual(make_counter(start=7)(), 7)

    def test_negative_and_zero_step(self):
        """A negative step counts down; a zero step repeats the start"""
        down = make_counter(3, -1)
        self.assertEqual([down(), down(), down(), down()], [3, 2, 1, 0])
        flat = make_counter(9, 0)
        self.assertEqual([flat(), flat()], [9, 9])

    def test_counters_are_independent(self):
        """Two counters keep separate state"""
        a = make_counter()
        b = make_counter(10)
        self.assertEqual([a(), a(), b(), a(), b()], [0, 1, 10, 2, 11])


class TestMakeCheckinTracker(unittest.TestCase):
    def test_counts_per_hostname(self):
        """Each hostname is counted separately, including the current call"""
        record = make_checkin_tracker()
        self.assertEqual([record("a"), record("b"), record("a"), record("a")], [1, 1, 2, 3])

    def test_case_and_whitespace_insensitive(self):
        """Different spellings of the same hostname share one count"""
        record = make_checkin_tracker()
        self.assertEqual([record("mbp-j-doe"), record("MBP-J-DOE"), record(" mbp-j-doe ")], [1, 2, 3])

    def test_trackers_are_independent(self):
        """Two trackers do not share counts"""
        first = make_checkin_tracker()
        second = make_checkin_tracker()
        first("a")
        first("a")
        self.assertEqual(second("a"), 1)
        self.assertEqual(first("a"), 3)


if __name__ == "__main__":
    unittest.main()
