import unittest

from exercise import oldest_device


class TestOldestDevice(unittest.TestCase):
    def test_single_device(self):
        """A single device is the oldest"""
        self.assertEqual(oldest_device([{"hostname": "a", "enrolled": "2024-01-01"}]), "a")

    def test_picks_earliest_date(self):
        """Returns the hostname with the earliest enrollment date"""
        fleet = [
            {"hostname": "mbp-j-doe", "enrolled": "2023-02-14"},
            {"hostname": "win-lab-01", "enrolled": "2021-06-30"},
            {"hostname": "nuc-01", "enrolled": "2022-11-01"},
        ]
        self.assertEqual(oldest_device(fleet), "win-lab-01")

    def test_earliest_can_be_last(self):
        """Order in the list does not matter; the last record can win"""
        fleet = [
            {"hostname": "a", "enrolled": "2022-01-01"},
            {"hostname": "b", "enrolled": "2021-12-31"},
        ]
        self.assertEqual(oldest_device(fleet), "b")

    def test_empty_list(self):
        """An empty list returns None"""
        self.assertIsNone(oldest_device([]))

    def test_tie_first_wins(self):
        """On equal dates the first record in the list wins"""
        fleet = [
            {"hostname": "x", "enrolled": "2020-05-05"},
            {"hostname": "y", "enrolled": "2020-05-05"},
            {"hostname": "z", "enrolled": "2020-05-05"},
        ]
        self.assertEqual(oldest_device(fleet), "x")

    def test_skips_missing_dates(self):
        """Records with no enrollment date are skipped"""
        fleet = [
            {"hostname": "a"},
            {"hostname": "b", "enrolled": None},
            {"hostname": "c", "enrolled": "2023-01-01"},
            {"hostname": "d", "enrolled": "2022-01-01"},
        ]
        self.assertEqual(oldest_device(fleet), "d")

    def test_all_missing_returns_none(self):
        """When no record has a date the result is None"""
        self.assertIsNone(oldest_device([{"hostname": "a"}, {"hostname": "b", "enrolled": None}]))

    def test_does_not_reorder_input(self):
        """The input list is not modified"""
        fleet = [
            {"hostname": "a", "enrolled": "2023-01-01"},
            {"hostname": "b", "enrolled": "2021-01-01"},
        ]
        oldest_device(fleet)
        self.assertEqual([d["hostname"] for d in fleet], ["a", "b"])


if __name__ == "__main__":
    unittest.main()
