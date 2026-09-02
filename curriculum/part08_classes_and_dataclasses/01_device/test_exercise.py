import unittest

from exercise import Device


class TestDevice(unittest.TestCase):
    def test_stores_attributes(self):
        """__init__ stores hostname, serial, os_name and ram_gb as attributes"""
        d = Device("mbp-j-doe", "C02XG1234ABC", "macOS", 16)
        self.assertEqual(d.hostname, "mbp-j-doe")
        self.assertEqual(d.serial, "C02XG1234ABC")
        self.assertEqual(d.os_name, "macOS")
        self.assertEqual(d.ram_gb, 16)

    def test_normalises_hostname(self):
        """Hostname is stripped and lowercased; serial is kept as given"""
        d = Device("  MBP-J-DOE \n", "C02XG1234ABC", "macOS", 16)
        self.assertEqual(d.hostname, "mbp-j-doe")
        self.assertEqual(d.serial, "C02XG1234ABC")

    def test_describe(self):
        """describe() returns 'hostname: os, N GB RAM'"""
        d = Device("mbp-j-doe", "C02XG1234ABC", "macOS", 16)
        self.assertEqual(d.describe(), "mbp-j-doe: macOS, 16 GB RAM")

    def test_repr(self):
        """repr looks like the constructor call with quoted strings"""
        d = Device("WIN-LAB-01", "7GH2K3Q", "Windows", 8)
        self.assertEqual(repr(d), "Device(hostname='win-lab-01', serial='7GH2K3Q', os_name='Windows', ram_gb=8)")

    def test_equality_by_serial(self):
        """Same serial means equal even if everything else differs"""
        a = Device("mbp-j-doe", "C02XG1234ABC", "macOS", 16)
        b = Device("spare-laptop", "C02XG1234ABC", "macOS", 32)
        c = Device("mbp-j-doe", "C02XG9999ZZZ", "macOS", 16)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_equality_with_other_types(self):
        """Comparing with a non-Device is False, not an error"""
        d = Device("mbp-j-doe", "C02XG1234ABC", "macOS", 16)
        self.assertFalse(d == "C02XG1234ABC")
        self.assertTrue(d != "C02XG1234ABC")
        self.assertFalse(d == None)  # noqa: E711  (exercising __eq__, not identity)

    def test_hashable_and_consistent_with_eq(self):
        """Equal devices collapse to one set member and share a dict key"""
        a = Device("mbp-j-doe", "C02XG1234ABC", "macOS", 16)
        b = Device("spare-laptop", "C02XG1234ABC", "macOS", 32)
        self.assertEqual(hash(a), hash(b))
        self.assertEqual(len({a, b}), 1)
        owners = {a: "j.doe"}
        self.assertEqual(owners[b], "j.doe")


if __name__ == "__main__":
    unittest.main()
