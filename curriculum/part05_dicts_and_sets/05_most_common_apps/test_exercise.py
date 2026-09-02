import unittest

from exercise import most_common_apps

INSTALLS = {
    "C02A": ["Slack", "Chrome", "Slack"],
    "C02B": ["Chrome", "Zoom"],
    "C02C": ["Zoom", "Chrome"],
}


class TestMostCommonApps(unittest.TestCase):
    def test_top_one(self):
        """The single most common app"""
        self.assertEqual(most_common_apps(INSTALLS, 1), [("Chrome", 3)])

    def test_top_k(self):
        """The first k entries in descending order of count"""
        self.assertEqual(most_common_apps(INSTALLS, 2), [("Chrome", 3), ("Zoom", 2)])

    def test_k_larger_than_apps(self):
        """k beyond the number of distinct apps returns them all"""
        self.assertEqual(most_common_apps(INSTALLS, 10), [("Chrome", 3), ("Zoom", 2), ("Slack", 1)])

    def test_k_zero_or_negative_and_empty(self):
        """k <= 0 or no data gives an empty list"""
        self.assertEqual(most_common_apps(INSTALLS, 0), [])
        self.assertEqual(most_common_apps(INSTALLS, -3), [])
        self.assertEqual(most_common_apps({}, 3), [])
        self.assertEqual(most_common_apps({"C02A": []}, 3), [])

    def test_counts_once_per_device(self):
        """Several copies on one device count as one install"""
        installs = {"a": ["Slack", "Slack", "Slack"], "b": ["Zoom"], "c": ["Zoom"]}
        self.assertEqual(most_common_apps(installs, 2), [("Zoom", 2), ("Slack", 1)])

    def test_ties_alphabetical(self):
        """Equal counts are ordered by name"""
        installs = {"a": ["Zoom", "Slack", "Chrome"], "b": ["Zoom", "Slack", "Chrome"]}
        self.assertEqual(most_common_apps(installs, 3), [("Chrome", 2), ("Slack", 2), ("Zoom", 2)])
        self.assertEqual(most_common_apps(installs, 1), [("Chrome", 2)])

    def test_case_sensitive_names(self):
        """'chrome' and 'Chrome' are different apps; uppercase sorts first"""
        installs = {"a": ["chrome"], "b": ["Chrome"]}
        self.assertEqual(most_common_apps(installs, 2), [("Chrome", 1), ("chrome", 1)])

    def test_input_not_modified(self):
        """The input lists keep their duplicates"""
        installs = {"a": ["Slack", "Slack"]}
        most_common_apps(installs, 1)
        self.assertEqual(installs, {"a": ["Slack", "Slack"]})


if __name__ == "__main__":
    unittest.main()
