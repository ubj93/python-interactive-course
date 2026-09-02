import unittest

from exercise import validate_device_record


def good(**overrides):
    record = {"serial": "C02XG1234ABC", "hostname": "mbp-j-doe", "os": "macOS", "ram_gb": 16, "last_seen": "2024-05-01"}
    record.update(overrides)
    return record


class TestValidateDeviceRecord(unittest.TestCase):
    def test_valid_record(self):
        """A correct record produces no errors"""
        self.assertEqual(validate_device_record(good()), [])
        self.assertEqual(validate_device_record(good(serial="7GH2K3Q", hostname="A", os="Linux", ram_gb=1)), [])

    def test_missing_fields_in_order(self):
        """Missing fields are reported first, in the required order"""
        self.assertEqual(
            validate_device_record({"os": "macOS"}),
            ["missing field: serial", "missing field: hostname", "missing field: ram_gb", "missing field: last_seen"],
        )
        self.assertEqual(
            validate_device_record({}),
            [f"missing field: {name}" for name in ("serial", "hostname", "os", "ram_gb", "last_seen")],
        )

    def test_serial_and_hostname_rules(self):
        """Serial and hostname format problems use the documented messages"""
        for serial in ["c02xg1234abc", "C02XG1", "C02XG1234ABCD", "C02X-1234ABC", "", 12345678, None]:
            errors = validate_device_record(good(serial=serial))
            self.assertEqual(errors, [f"serial: must be 7-12 uppercase letters or digits, got {serial!r}"], serial)
        for hostname in ["", "-lab", "lab-", "lab_01", "a" * 64, "mbp j", 42]:
            errors = validate_device_record(good(hostname=hostname))
            self.assertEqual(errors, [f"hostname: must be 1-63 letters, digits or hyphens, got {hostname!r}"], hostname)
        self.assertEqual(validate_device_record(good(hostname="MBP-J-DOE-01")), [])
        self.assertEqual(validate_device_record(good(hostname="a" * 63)), [])

    def test_os_and_ram_rules(self):
        """OS must be one of three spellings; ram_gb a positive int, not a bool"""
        for os_name in ["ChromeOS", "macos", "windows", None]:
            self.assertEqual(
                validate_device_record(good(os=os_name)),
                [f"os: must be one of Linux, Windows, macOS, got {os_name!r}"],
                os_name,
            )
        for ram in ["16", 0, -8, 16.0, True, None]:
            self.assertEqual(
                validate_device_record(good(ram_gb=ram)), [f"ram_gb: must be a positive integer, got {ram!r}"], ram
            )

    def test_last_seen_rule(self):
        """last_seen must be a real ISO date string"""
        for seen in ["2024-13-01", "2024-02-30", "01/05/2024", "2024-5-1", "", None, 20240501]:
            self.assertEqual(
                validate_device_record(good(last_seen=seen)),
                [f"last_seen: must be an ISO date YYYY-MM-DD, got {seen!r}"],
                seen,
            )
        self.assertEqual(validate_device_record(good(last_seen="2024-02-29")), [])

    def test_unknown_fields_sorted_last(self):
        """Unknown fields come after everything else, sorted by name"""
        self.assertEqual(
            validate_device_record(good(zeta=1, alpha=2, colour="blue")),
            ["unknown field: alpha", "unknown field: colour", "unknown field: zeta"],
        )

    def test_everything_at_once(self):
        """All error kinds combine in the documented order"""
        record = {"serial": "c02", "os": "ChromeOS", "ram_gb": "16", "last_seen": "2024-13-01", "colour": "blue"}
        self.assertEqual(
            validate_device_record(record),
            [
                "missing field: hostname",
                "serial: must be 7-12 uppercase letters or digits, got 'c02'",
                "os: must be one of Linux, Windows, macOS, got 'ChromeOS'",
                "ram_gb: must be a positive integer, got '16'",
                "last_seen: must be an ISO date YYYY-MM-DD, got '2024-13-01'",
                "unknown field: colour",
            ],
        )


if __name__ == "__main__":
    unittest.main()
