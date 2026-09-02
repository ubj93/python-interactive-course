import unittest
from enum import Enum

from exercise import Platform


class TestPlatform(unittest.TestCase):
    def test_members_and_values(self):
        """Four members with the documented string values, usable by value"""
        self.assertTrue(issubclass(Platform, Enum))
        self.assertEqual([p.value for p in Platform], ["mac", "windows", "linux", "ios"])
        self.assertIs(Platform("mac"), Platform.MAC)

    def test_exact_values(self):
        """A value string maps straight to its member"""
        for text, member in [("mac", Platform.MAC), ("windows", Platform.WINDOWS), ("linux", Platform.LINUX), ("ios", Platform.IOS)]:
            self.assertIs(Platform.from_string(text), member, text)

    def test_case_and_whitespace(self):
        """Casing and surrounding whitespace do not matter"""
        self.assertIs(Platform.from_string("  MAC\n"), Platform.MAC)
        self.assertIs(Platform.from_string("Windows"), Platform.WINDOWS)

    def test_aliases(self):
        """Aliases from the table map to their member"""
        for text, member in [
            ("macOS", Platform.MAC), ("Mac OS X", Platform.MAC), ("OS X", Platform.MAC), ("darwin", Platform.MAC),
            ("win", Platform.WINDOWS), ("Microsoft Windows", Platform.WINDOWS),
            ("Ubuntu", Platform.LINUX), ("rhel", Platform.LINUX), ("GNU/Linux", Platform.LINUX),
            ("iPadOS", Platform.IOS), ("iPhone OS", Platform.IOS),
        ]:
            self.assertIs(Platform.from_string(text), member, text)

    def test_version_suffix_is_ignored(self):
        """Everything from the first digit on is dropped before matching"""
        self.assertIs(Platform.from_string("macOS 14.5"), Platform.MAC)
        self.assertIs(Platform.from_string("Mac OS X 10.15.7"), Platform.MAC)
        self.assertIs(Platform.from_string("win32"), Platform.WINDOWS)
        self.assertIs(Platform.from_string("iOS 17.5.1"), Platform.IOS)
        self.assertIs(Platform.from_string("Windows   11 Enterprise"), Platform.WINDOWS)

    def test_first_word_fallback(self):
        """When the whole text does not match, the first word is tried"""
        self.assertIs(Platform.from_string("Microsoft Windows 11 Enterprise"), Platform.WINDOWS)
        self.assertIs(Platform.from_string("Windows Server 2022"), Platform.WINDOWS)
        self.assertIs(Platform.from_string("Ubuntu 22.04.4 LTS"), Platform.LINUX)
        self.assertIs(Platform.from_string("Debian GNU/Linux 12"), Platform.LINUX)
        self.assertIs(Platform.from_string("macOS Sonoma"), Platform.MAC)

    def test_unknown_raises(self):
        """Unknown, empty and None input raise ValueError"""
        for bad in ["FreeBSD 14", "ChromeOS 125", "Arch Linux", "", "   ", None, "14.5"]:
            with self.assertRaises(ValueError, msg=repr(bad)):
                Platform.from_string(bad)

    def test_is_apple(self):
        """is_apple is True for MAC and IOS only"""
        self.assertTrue(Platform.MAC.is_apple)
        self.assertTrue(Platform.IOS.is_apple)
        self.assertFalse(Platform.WINDOWS.is_apple)
        self.assertFalse(Platform.LINUX.is_apple)


if __name__ == "__main__":
    unittest.main()
