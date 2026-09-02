import unittest

from exercise import is_valid_serial


class TestIsValidSerial(unittest.TestCase):
    def test_apple_valid(self):
        """10- and 12-character Apple serials are valid"""
        self.assertTrue(is_valid_serial("C02XG1234ABC"))
        self.assertTrue(is_valid_serial("FVFXC1234A"))
        self.assertTrue(is_valid_serial("1234567890"))

    def test_dell_valid(self):
        """7-character Dell tags with a digit are valid"""
        self.assertTrue(is_valid_serial("7GH2K3Q"))
        self.assertTrue(is_valid_serial("ABCDEF1"))

    def test_dell_needs_digit(self):
        """A 7-letter tag with no digit is invalid"""
        self.assertFalse(is_valid_serial("ABCDEFG"))

    def test_wrong_length(self):
        """8, 9, 11 and 13 characters are invalid"""
        for s in ["FVFXC123", "FVFXC1234", "C02XG1234AB", "C02XG1234ABCD"]:
            self.assertFalse(is_valid_serial(s), s)

    def test_bad_characters(self):
        """Lowercase, spaces, hyphens and punctuation are invalid"""
        for s in ["c02xg1234abc", "C02XG 234ABC", "C02X-1234ABC", "7GH2K3!", "C02XG1234ÄBC"]:
            self.assertFalse(is_valid_serial(s), s)

    def test_empty_and_none(self):
        """Empty string and None are invalid"""
        self.assertFalse(is_valid_serial(""))
        self.assertFalse(is_valid_serial(None))


if __name__ == "__main__":
    unittest.main()
