import unittest
from datetime import date, timedelta

from exercise import stale_devices

TODAY = date(2024, 6, 1)


def dev(hostname, days_ago):
    return {"hostname": hostname, "last_seen": None if days_ago is None else TODAY - timedelta(days=days_ago)}


class TestStaleDevices(unittest.TestCase):
    def test_nothing_stale(self):
        """Recently seen devices are not reported"""
        self.assertEqual(stale_devices([dev("a", 0), dev("b", 3), dev("c", 29)], TODAY), [])

    def test_some_stale(self):
        """Devices older than 30 days are reported"""
        devices = [dev("mbp-j-doe", 2), dev("win-lab-01", 61), dev("mbp-a-lee", 45)]
        self.assertEqual(stale_devices(devices, TODAY), ["win-lab-01", "mbp-a-lee"])

    def test_boundary_is_fresh(self):
        """Exactly max_days ago is fresh; one day more is stale"""
        self.assertEqual(stale_devices([dev("edge", 30)], TODAY), [])
        self.assertEqual(stale_devices([dev("edge", 31)], TODAY), ["edge"])

    def test_never_seen_is_stale(self):
        """last_seen of None counts as stale"""
        self.assertEqual(stale_devices([dev("ipad-kiosk", None), dev("ok", 1)], TODAY), ["ipad-kiosk"])

    def test_custom_max_days_and_order(self):
        """max_days is honoured and the input order is preserved"""
        devices = [dev("d", 10), dev("c", 8), dev("b", 7), dev("a", 9)]
        self.assertEqual(stale_devices(devices, TODAY, max_days=7), ["d", "c", "a"])
        self.assertEqual(stale_devices(devices, TODAY, max_days=0), ["d", "c", "b", "a"])

    def test_empty_input(self):
        """No devices gives an empty list"""
        self.assertEqual(stale_devices([], TODAY), [])


if __name__ == "__main__":
    unittest.main()
