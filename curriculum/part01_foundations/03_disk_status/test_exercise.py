import unittest

from exercise import disk_status


class TestDiskStatus(unittest.TestCase):
    def test_ok(self):
        """Low usage is OK"""
        self.assertEqual(disk_status(0.0), "OK")
        self.assertEqual(disk_status(0.5), "OK")
        self.assertEqual(disk_status(0.7999), "OK")

    def test_warn_boundaries(self):
        """80% is WARN, just under 95% is still WARN"""
        self.assertEqual(disk_status(0.80), "WARN")
        self.assertEqual(disk_status(0.9499), "WARN")

    def test_crit_boundaries(self):
        """95% and 100% are CRIT"""
        self.assertEqual(disk_status(0.95), "CRIT")
        self.assertEqual(disk_status(1.0), "CRIT")

    def test_out_of_range(self):
        """Values outside 0..1 are UNKNOWN"""
        self.assertEqual(disk_status(1.2), "UNKNOWN")
        self.assertEqual(disk_status(-0.1), "UNKNOWN")

    def test_none(self):
        """None is UNKNOWN"""
        self.assertEqual(disk_status(None), "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
