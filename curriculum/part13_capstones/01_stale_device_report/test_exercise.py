import unittest
from datetime import date

from exercise import find_duplicates, find_stale, parse_inventory, render_report, stale_device_report

HEADER = "serial,hostname,user,os,last_checkin\n"
TODAY = date(2024, 6, 1)


def row(serial, hostname="h", user="u", os="macOS", last_checkin=""):
    return {"serial": serial, "hostname": hostname, "user": user, "os": os, "last_checkin": last_checkin}


class TestStaleDeviceReport(unittest.TestCase):
    def test_parse_normalises_fields(self):
        """parse_inventory strips, uppercases serials, lowercases hostname and user"""
        rows = parse_inventory(HEADER + " c02abc ,MBP-A ,Alice@Example.com, macOS ,2024-04-01\n")
        self.assertEqual(rows, [row("C02ABC", "mbp-a", "alice@example.com", "macOS", "2024-04-01")])

    def test_parse_skips_blank_and_short_rows(self):
        """parse_inventory skips blank lines and empty serials; short rows get empty strings"""
        text = HEADER + "\n,,,,\nC02ABC,mbp-a\n   \n,mbp-x,x,macOS,2024-01-01\nC02DEF,mbp-d,dan,,2024-05-01\n"
        rows = parse_inventory(text)
        self.assertEqual(rows, [row("C02ABC", "mbp-a", "", "unknown", ""), row("C02DEF", "mbp-d", "dan", "unknown", "2024-05-01")])

    def test_find_duplicates(self):
        """find_duplicates counts serials that appear more than once"""
        devices = [row("A"), row("B"), row("A"), row("C"), row("A")]
        self.assertEqual(find_duplicates(devices), {"A": 3})
        self.assertEqual(find_duplicates([row("A"), row("B")]), {})

    def test_find_stale_cutoff_and_order(self):
        """find_stale: exactly max_days is fresh, older is stale, never first then oldest, grouped by os"""
        devices = [
            row("A1", os="macOS", last_checkin="2024-05-02"),  # 30 days: fresh
            row("A2", os="macOS", last_checkin="2024-05-01"),  # 31 days: stale
            row("A3", os="macOS", last_checkin=""),            # never
            row("W1", os="Windows", last_checkin="2024-01-01"),
            row("A4", os="macOS", last_checkin="2024-03-01"),  # 92 days
            row("A5", os="macOS", last_checkin="2024-03-01"),  # tie broken by serial
        ]
        stale = find_stale(devices, TODAY, 30)
        self.assertEqual([(r["serial"], r["days"]) for r in stale],
                         [("A3", None), ("A4", 92), ("A5", 92), ("A2", 31), ("W1", 152)])
        self.assertNotIn("days", devices[1], "input rows must not be mutated")

    def test_find_stale_collapses_duplicates(self):
        """find_stale keeps the newest check-in for a duplicated serial; bad dates count as never"""
        devices = [row("A1", last_checkin="2024-01-01"), row("A1", last_checkin="2024-05-30"),
                   row("B1", last_checkin="yesterday"), row("C1", last_checkin=""), row("C1", last_checkin="2024-02-01")]
        stale = find_stale(devices, TODAY, 30)
        self.assertEqual([(r["serial"], r["days"]) for r in stale], [("B1", None), ("C1", 121)])

    def test_render_report_format(self):
        """render_report produces the exact Markdown layout with two os groups and duplicates"""
        stale = [
            {**row("C02DEF", "mbp-b", "bob", "macOS", ""), "days": None},
            {**row("C02ABC", "mbp-a", "alice", "macOS", "2024-04-01"), "days": 61},
            {**row("7GH2K3Q", "win-01", "", "Windows", "2024-04-20"), "days": 42},
        ]
        expected = "\n".join([
            "# Stale device report",
            "",
            "Generated: 2024-06-01. Cutoff: 30 days. Devices: 7. Stale: 3. Never checked in: 1. Duplicate serials: 1.",
            "",
            "## macOS (2)",
            "",
            "| serial | hostname | user | last check-in | days |",
            "|---|---|---|---|---|",
            "| C02DEF | mbp-b | bob | never | - |",
            "| C02ABC | mbp-a | alice | 2024-04-01 | 61 |",
            "",
            "## Windows (1)",
            "",
            "| serial | hostname | user | last check-in | days |",
            "|---|---|---|---|---|",
            "| 7GH2K3Q | win-01 | - | 2024-04-20 | 42 |",
            "",
            "## Duplicate serials",
            "",
            "- C02ABC (2 rows)",
        ])
        self.assertEqual(render_report(stale, {"C02ABC": 2}, TODAY, 30, 7), expected)

    def test_render_report_nothing_stale(self):
        """render_report with no stale rows says so and omits the duplicates section"""
        expected = ("# Stale device report\n\nGenerated: 2024-06-01. Cutoff: 45 days. Devices: 3. "
                    "Stale: 0. Never checked in: 0. Duplicate serials: 0.\n\nNo stale devices.")
        self.assertEqual(render_report([], {}, TODAY, 45, 3), expected)

    def test_end_to_end_messy_export(self):
        """stale_device_report handles a messy export end to end"""
        text = (
            "serial,hostname,user,os,last_checkin\r\n"
            "c02abc,MBP-A,alice,macOS,2024-01-15\r\n"
            "\r\n"
            "C02ABC,mbp-a,alice,macOS,2024-05-28\r\n"
            "c02def, MBP-D ,Dan,macOS,\r\n"
            "7GH2K3Q,win-01,carol,Windows,2024-04-20\r\n"
            ",,,,\r\n"
            "7GH2K3R,win-02,erin,windows,2024-05-31\r\n"
            "XY1,lab-01,,,2024-02-01\r\n"
        )
        expected = "\n".join([
            "# Stale device report",
            "",
            "Generated: 2024-06-01. Cutoff: 30 days. Devices: 5. Stale: 3. Never checked in: 1. Duplicate serials: 1.",
            "",
            "## macOS (1)",
            "",
            "| serial | hostname | user | last check-in | days |",
            "|---|---|---|---|---|",
            "| C02DEF | mbp-d | dan | never | - |",
            "",
            "## unknown (1)",
            "",
            "| serial | hostname | user | last check-in | days |",
            "|---|---|---|---|---|",
            "| XY1 | lab-01 | - | 2024-02-01 | 121 |",
            "",
            "## Windows (1)",
            "",
            "| serial | hostname | user | last check-in | days |",
            "|---|---|---|---|---|",
            "| 7GH2K3Q | win-01 | carol | 2024-04-20 | 42 |",
            "",
            "## Duplicate serials",
            "",
            "- C02ABC (2 rows)",
        ])
        self.assertEqual(stale_device_report(text, TODAY, 30), expected)


if __name__ == "__main__":
    unittest.main()
