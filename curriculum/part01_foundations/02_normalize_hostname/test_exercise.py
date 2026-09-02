import unittest

from exercise import normalize_hostname


class TestNormalizeHostname(unittest.TestCase):
    def test_strips_and_lowercases(self):
        """Strips whitespace and lowercases"""
        self.assertEqual(normalize_hostname("  MBP-J-DOE \n"), "mbp-j-doe")

    def test_drops_domain(self):
        """Keeps only the part before the first dot"""
        self.assertEqual(normalize_hostname("mbp-j-doe.corp.example.com"), "mbp-j-doe")

    def test_underscores_become_hyphens(self):
        """Replaces underscores with hyphens"""
        self.assertEqual(normalize_hostname("win_lab_01"), "win-lab-01")

    def test_everything_at_once(self):
        """Handles all rules together"""
        self.assertEqual(normalize_hostname("\tWIN_Lab_01.corp.example.com  "), "win-lab-01")

    def test_blank_input(self):
        """Whitespace-only input gives an empty string"""
        self.assertEqual(normalize_hostname("   "), "")
        self.assertEqual(normalize_hostname(""), "")

    def test_already_clean(self):
        """Clean input is returned unchanged"""
        self.assertEqual(normalize_hostname("mbp-j-doe"), "mbp-j-doe")


if __name__ == "__main__":
    unittest.main()
