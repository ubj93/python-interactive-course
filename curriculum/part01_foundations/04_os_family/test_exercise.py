import unittest

from exercise import os_family


class TestOsFamily(unittest.TestCase):
    def test_mac_variants(self):
        """macOS, Mac OS X and OS X are all 'mac'"""
        for s in ["macOS 14.5", "Mac OS X 10.15.7", "OS X 10.11", "MACOS Sonoma"]:
            self.assertEqual(os_family(s), "mac", s)

    def test_windows(self):
        """Windows in any casing with whitespace"""
        self.assertEqual(os_family("  microsoft windows 11 enterprise "), "windows")
        self.assertEqual(os_family("Windows Server 2022"), "windows")

    def test_linux_distros(self):
        """Common distro names map to 'linux'"""
        for s in ["Ubuntu 22.04.4 LTS", "Debian GNU/Linux 12", "Fedora 40", "RHEL 9.3", "CentOS 7", "Arch Linux"]:
            self.assertEqual(os_family(s), "linux", s)

    def test_ios(self):
        """iOS and iPadOS are 'ios' (checked before mac)"""
        self.assertEqual(os_family("iOS 17.5.1"), "ios")
        self.assertEqual(os_family("iPadOS 17.5"), "ios")

    def test_other(self):
        """Unknown, empty and None are 'other'"""
        self.assertEqual(os_family("FreeBSD 14"), "other")
        self.assertEqual(os_family(""), "other")
        self.assertEqual(os_family(None), "other")
        self.assertEqual(os_family("ChromeOS 125"), "other")


if __name__ == "__main__":
    unittest.main()
