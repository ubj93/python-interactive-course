import unittest
from datetime import date

from exercise import sort_devices


def dev(name, os_name, last_seen):
    return {"name": name, "os": os_name, "last_seen": last_seen}


def names(devices):
    return [d["name"] for d in devices]


class TestSortDevices(unittest.TestCase):
    def test_sorts_by_os(self):
        """Devices are grouped by os in ascending order"""
        devices = [dev("w", "windows", date(2024, 5, 1)), dev("l", "linux", date(2024, 5, 1)), dev("m", "mac", date(2024, 5, 1))]
        self.assertEqual(names(sort_devices(devices)), ["l", "m", "w"])

    def test_newest_first_within_os(self):
        """Within one os the most recently seen device comes first"""
        devices = [dev("old", "mac", date(2024, 1, 1)), dev("new", "mac", date(2024, 5, 9)), dev("mid", "mac", date(2024, 3, 1))]
        self.assertEqual(names(sort_devices(devices)), ["new", "mid", "old"])

    def test_name_breaks_ties(self):
        """Equal os and last_seen sort by name ascending"""
        d = date(2024, 5, 1)
        devices = [dev("mbp-c", "mac", d), dev("mbp-a", "mac", d), dev("mbp-b", "mac", d)]
        self.assertEqual(names(sort_devices(devices)), ["mbp-a", "mbp-b", "mbp-c"])

    def test_none_last_seen_goes_last_in_its_os(self):
        """None sorts after every real date, but stays inside its os group"""
        devices = [
            dev("never-mac", "mac", None),
            dev("win", "windows", date(2024, 5, 1)),
            dev("seen-mac", "mac", date(2023, 1, 1)),
            dev("never-mac-2", "mac", None),
            dev("never-mac-1", "mac", None),
        ]
        self.assertEqual(names(sort_devices(devices)), ["seen-mac", "never-mac", "never-mac-1", "never-mac-2", "win"])

    def test_all_three_keys_together(self):
        """The full ordering from the description"""
        devices = [
            dev("win-lab-01", "windows", date(2024, 5, 1)),
            dev("mbp-j-doe", "mac", date(2024, 5, 3)),
            dev("mbp-a-lee", "mac", date(2024, 5, 9)),
            dev("mbp-zz-old", "mac", None),
            dev("win-lab-02", "windows", date(2024, 5, 1)),
            dev("srv-01", "linux", date(2024, 4, 1)),
            dev("mbp-b-lee", "mac", date(2024, 5, 9)),
        ]
        self.assertEqual(
            names(sort_devices(devices)),
            ["srv-01", "mbp-a-lee", "mbp-b-lee", "mbp-j-doe", "mbp-zz-old", "win-lab-01", "win-lab-02"],
        )

    def test_does_not_mutate_input(self):
        """The input list keeps its order and the same dict objects are returned"""
        devices = [dev("b", "mac", date(2024, 5, 1)), dev("a", "mac", date(2024, 5, 1))]
        snapshot = list(devices)
        result = sort_devices(devices)
        self.assertEqual(devices, snapshot)
        self.assertIsNot(result, devices)
        self.assertIs(result[0], devices[1])

    def test_empty(self):
        """An empty list sorts to an empty list"""
        self.assertEqual(sort_devices([]), [])


if __name__ == "__main__":
    unittest.main()
