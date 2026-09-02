import unittest

from exercise import RULES, classify, count_offenders, log_triage, parse_line, top_offenders


class TestLogTriage(unittest.TestCase):
    def test_parse_syslog_lines(self):
        """parse_line reads syslog lines with and without a pid, lowercasing the host"""
        self.assertEqual(
            parse_line("Jun  1 12:00:01 HOST01 munki[123]: Could not resolve repo.example.com"),
            {"host": "host01", "process": "munki", "message": "Could not resolve repo.example.com"},
        )
        self.assertEqual(
            parse_line("Jun 12 09:05:59 lab-mac-2 jamf: Permission denied for /Library/Managed\n"),
            {"host": "lab-mac-2", "process": "jamf", "message": "Permission denied for /Library/Managed"},
        )

    def test_parse_json_lines(self):
        """parse_line reads JSON objects; process defaults to empty"""
        self.assertEqual(
            parse_line('{"host": "Host02", "process": "osquery", "message": " No space left on device "}'),
            {"host": "host02", "process": "osquery", "message": "No space left on device"},
        )
        self.assertEqual(
            parse_line('  {"message": "Unauthorized", "host": "host03"}'),
            {"host": "host03", "process": "", "message": "Unauthorized"},
        )

    def test_parse_junk_is_none(self):
        """parse_line returns None for blanks, banners, broken JSON and incomplete objects"""
        junk = [
            "",
            "   ",
            "=== collector restart ===",
            "Jun  1 12:00:01 host01",
            '{"host": "h", "message": "x"',
            '["host", "message"]',
            '{"host": "h"}',
            '{"host": 7, "message": "x"}',
        ]
        for line in junk:
            self.assertIsNone(parse_line(line), repr(line))

    def test_classify_rules_table(self):
        """classify matches case-insensitively, first rule wins, None when nothing matches"""
        self.assertEqual(classify("ERROR: Connection REFUSED by 10.0.0.1"), "network")
        self.assertEqual(classify("Permission denied: no space left on device"), "auth")
        self.assertIsNone(classify("all good"))
        custom = [("boot", "kernel panic"), ("auth", "denied")]
        self.assertEqual(classify("access denied", custom), "auth")
        self.assertIsNone(classify("permission denied", []))

    def test_count_offenders(self):
        """count_offenders keys on (host, class) and drops unclassified records"""
        records = [
            {"host": "a", "process": "x", "message": "timed out"},
            {"host": "a", "process": "x", "message": "Connection refused"},
            {"host": "a", "process": "y", "message": "nothing to see"},
            {"host": "b", "process": "x", "message": "No space left on device"},
        ]
        self.assertEqual(count_offenders(records), {("a", "network"): 2, ("b", "disk"): 1})
        self.assertEqual(count_offenders([]), {})

    def test_top_offenders_ties(self):
        """top_offenders sorts by count desc, then host, then class, and truncates to n"""
        counts = {("b", "auth"): 2, ("a", "network"): 2, ("a", "disk"): 2, ("c", "network"): 5, ("d", "install"): 1}
        self.assertEqual(top_offenders(counts, 3), [("c", "network", 5), ("a", "disk", 2), ("a", "network", 2)])
        self.assertEqual(top_offenders(counts, 10)[-1], ("d", "install", 1))
        self.assertEqual(top_offenders({}, 3), [])

    def test_log_triage_end_to_end(self):
        """log_triage composes parse, classify, count and rank"""
        text = "\n".join([
            "Jun  1 12:00:01 host01 munki[123]: Could not resolve repo.example.com",
            '{"host": "host02", "process": "osquery", "message": "No space left on device"}',
            "Jun  1 12:00:02 host01 munki[123]: Could not resolve repo.example.com",
            "Jun  1 12:00:03 host01 jamf: Permission denied",
            '{"host": "host02", "message": "read-only file system"}',
            "Jun  1 12:00:04 host03 softwareupdate[9]: installed fine",
        ])
        self.assertEqual(log_triage(text, 2), [("host01", "network", 2), ("host02", "disk", 2)])
        self.assertEqual(log_triage(text)[2], ("host01", "auth", 1))

    def test_log_triage_messy_input(self):
        """log_triage survives CRLF, junk lines, and host casing differences"""
        text = (
            "=== begin ===\r\n"
            "\r\n"
            "Jun  1 12:00:01 HOST01 munki[1]: Install failed for Firefox\r\n"
            '{"host": "host01", "message": "package signature invalid"}\r\n'
            "Jun  1 12:00:03 host01 munki[1]: Install fai\r\n"
            "{not json}\r\n"
            "Jun  1 12:00:04 host02 jamf: Unauthorized\r\n"
            "Jun  1 12:00:05 Host02 jamf: UNAUTHORIZED again\r\n"
            "Jun  1 12:00:06 host02 jamf: connection refused\r\n"
            "Jun  1 12:00:07 host02 jamf: everything is fine\r\n"
        )
        self.assertEqual(
            log_triage(text, 5),
            [("host01", "install", 2), ("host02", "auth", 2), ("host02", "network", 1)],
        )


if __name__ == "__main__":
    unittest.main()
