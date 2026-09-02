import argparse
import io
import unittest
from contextlib import redirect_stderr

from exercise import build_parser, parse_args


class TestParseArgs(unittest.TestCase):
    def test_defaults(self):
        """Only the serial given: every option takes its default"""
        ns = parse_args(["C02XG1234ABC"])
        self.assertEqual(ns.serial, "C02XG1234ABC")
        self.assertEqual(ns.format, "table")
        self.assertEqual(ns.days, 30)
        self.assertEqual(ns.tags, [])
        self.assertFalse(ns.verbose)
        self.assertFalse(ns.online)
        self.assertFalse(ns.offline)

    def test_returns_namespace_and_parser(self):
        """build_parser gives an ArgumentParser, parse_args a Namespace"""
        self.assertIsInstance(build_parser(), argparse.ArgumentParser)
        self.assertIsInstance(parse_args(["S1"]), argparse.Namespace)
        self.assertEqual(build_parser().prog, "devreport")

    def test_days_is_int_and_format_choice(self):
        """--days converts to int and --format accepts its choices"""
        ns = parse_args(["S1", "--days", "7", "--format", "json"])
        self.assertEqual(ns.days, 7)
        self.assertIsInstance(ns.days, int)
        self.assertEqual(ns.format, "json")

    def test_flags(self):
        """-v/--verbose and --online/--offline are boolean flags"""
        self.assertTrue(parse_args(["S1", "-v"]).verbose)
        self.assertTrue(parse_args(["S1", "--verbose"]).verbose)
        self.assertTrue(parse_args(["S1", "--online"]).online)
        self.assertTrue(parse_args(["S1", "--offline"]).offline)

    def test_repeated_tag(self):
        """--tag can be repeated and is collected into tags"""
        ns = parse_args(["S1", "--tag", "lab", "--tag", "loaner"])
        self.assertEqual(ns.tags, ["lab", "loaner"])

    def test_tags_do_not_leak_between_parses(self):
        """A second parse starts from an empty tags list"""
        parse_args(["S1", "--tag", "lab"])
        self.assertEqual(parse_args(["S2"]).tags, [])
        self.assertEqual(parse_args(["S3", "--tag", "x"]).tags, ["x"])

    def test_usage_errors_exit(self):
        """Missing serial, bad choice and non-int days raise SystemExit"""
        for argv in [[], ["S1", "--format", "xml"], ["S1", "--days", "soon"], ["S1", "--nope"]]:
            with redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit, msg=argv):
                    parse_args(argv)

    def test_online_offline_exclusive(self):
        """--online and --offline together is a usage error"""
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parse_args(["S1", "--online", "--offline"])


if __name__ == "__main__":
    unittest.main()
