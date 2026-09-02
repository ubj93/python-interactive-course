import unittest

from exercise import parse_syslog, parse_syslog_line


class TestParseSyslogLine(unittest.TestCase):
    def test_basic_line(self):
        """All five fields from a normal line"""
        self.assertEqual(
            parse_syslog_line("Jun 12 14:03:22 mbp-j-doe mdmclient[512]: Received push notification"),
            {
                "timestamp": "Jun 12 14:03:22",
                "host": "mbp-j-doe",
                "process": "mdmclient",
                "pid": 512,
                "message": "Received push notification",
            },
        )

    def test_pid_is_int(self):
        """The pid is an int, not a string"""
        parsed = parse_syslog_line("Jun 12 14:03:22 host softwareupdated[345]: idle")
        self.assertEqual(parsed["pid"], 345)
        self.assertIsInstance(parsed["pid"], int)

    def test_no_pid(self):
        """A process without brackets has pid None"""
        parsed = parse_syslog_line("Jun 12 14:03:22 mbp-j-doe kernel: AppleCamIn::wakeEventHandlerThread")
        self.assertEqual(parsed["process"], "kernel")
        self.assertIsNone(parsed["pid"])
        self.assertEqual(parsed["message"], "AppleCamIn::wakeEventHandlerThread")

    def test_single_digit_day(self):
        """A space-padded day is kept exactly as written"""
        parsed = parse_syslog_line("Jun  2 09:00:01 mbp-j-doe kernel: hello")
        self.assertEqual(parsed["timestamp"], "Jun  2 09:00:01")
        self.assertEqual(parsed["host"], "mbp-j-doe")

    def test_dotted_process_and_colons_in_message(self):
        """Process names may contain dots; the message keeps its own colons"""
        parsed = parse_syslog_line("Jun 12 14:03:23 win-lab-01 com.apple.xpc.launchd[1]: Service exited: reason: crash")
        self.assertEqual(parsed["process"], "com.apple.xpc.launchd")
        self.assertEqual(parsed["pid"], 1)
        self.assertEqual(parsed["message"], "Service exited: reason: crash")

    def test_empty_message(self):
        """Nothing after the colon gives an empty message"""
        parsed = parse_syslog_line("Jun 12 14:03:22 host mdmclient[512]: ")
        self.assertEqual(parsed["message"], "")

    def test_unparseable_returns_none(self):
        """Lines of the wrong shape give None"""
        for bad in ["", "not a syslog line", "2024-06-12T14:03:22Z host proc[1]: msg", "Jun 12 14:03:22 host"]:
            self.assertIsNone(parse_syslog_line(bad), bad)

    def test_parse_many_skips_junk(self):
        """parse_syslog keeps order, skips blanks and bad lines, tolerates newlines"""
        lines = [
            "Jun 12 14:03:22 h1 mdmclient[512]: one\n",
            "",
            "garbage",
            "Jun 12 14:03:23 h2 kernel: two\n",
        ]
        parsed = parse_syslog(lines)
        self.assertEqual([p["message"] for p in parsed], ["one", "two"])
        self.assertEqual([p["host"] for p in parsed], ["h1", "h2"])
        self.assertEqual(parse_syslog([]), [])


if __name__ == "__main__":
    unittest.main()
