import unittest

from exercise import count_by_os


class TestCountByOs(unittest.TestCase):
    def test_single_os(self):
        """Three macOS devices"""
        self.assertEqual(count_by_os([{"os": "macOS"}] * 3), {"macOS": 3})

    def test_mixed(self):
        """Counts each OS separately"""
        devices = [{"os": "macOS"}, {"os": "Windows"}, {"os": "macOS"}, {"os": "Linux"}]
        self.assertEqual(count_by_os(devices), {"macOS": 2, "Windows": 1, "Linux": 1})

    def test_empty(self):
        """An empty list gives an empty dict"""
        self.assertEqual(count_by_os([]), {})

    def test_missing_or_blank_is_unknown(self):
        """Missing key, None and empty string count as 'unknown'"""
        devices = [{"hostname": "a"}, {"os": None}, {"os": ""}, {"os": "macOS"}]
        self.assertEqual(count_by_os(devices), {"unknown": 3, "macOS": 1})

    def test_no_normalising(self):
        """'macOS' and 'macos' are different keys"""
        self.assertEqual(count_by_os([{"os": "macOS"}, {"os": "macos"}]), {"macOS": 1, "macos": 1})

    def test_first_seen_order(self):
        """Keys come out in the order each OS was first seen"""
        devices = [{"os": "Windows"}, {"os": "macOS"}, {"os": "Windows"}, {"os": "iOS"}]
        self.assertEqual(list(count_by_os(devices)), ["Windows", "macOS", "iOS"])


if __name__ == "__main__":
    unittest.main()
