import tempfile
import unittest
from pathlib import Path

from exercise import count_log_levels


def write_log(directory, text):
    p = Path(directory) / "agent.log"
    p.write_text(text, encoding="utf-8")
    return p


class TestCountLogLevels(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def test_counts_each_level(self):
        """Counts ERROR, WARN and INFO lines"""
        p = write_log(
            self.dir,
            "2024-05-01 10:00:01 [INFO] mdmclient: checking in\n"
            "2024-05-01 10:00:02 [WARN] mdmclient: profile missing\n"
            "2024-05-01 10:00:03 [ERROR] mdmclient: push token rejected\n"
            "2024-05-01 10:00:04 [INFO] mdmclient: done\n",
        )
        self.assertEqual(count_log_levels(p), {"ERROR": 1, "WARN": 1, "INFO": 2})

    def test_empty_file_has_all_keys(self):
        """An empty file gives zeros for all three keys, in order"""
        p = write_log(self.dir, "")
        result = count_log_levels(p)
        self.assertEqual(result, {"ERROR": 0, "WARN": 0, "INFO": 0})
        self.assertEqual(list(result), ["ERROR", "WARN", "INFO"])

    def test_warning_alias(self):
        """[WARNING] is counted as WARN"""
        p = write_log(self.dir, "t [WARNING] a\nt [WARN] b\nt [WARNING] c\n")
        self.assertEqual(count_log_levels(p), {"ERROR": 0, "WARN": 3, "INFO": 0})

    def test_ignores_other_and_lowercase_levels(self):
        """DEBUG, lowercase levels and lines without a level are ignored"""
        p = write_log(self.dir, "t [DEBUG] a\nt [error] b\nt [Info] c\nno level here\n\nt [ERROR] d\n")
        self.assertEqual(count_log_levels(p), {"ERROR": 1, "WARN": 0, "INFO": 0})

    def test_only_first_bracket_counts(self):
        """A bracketed token later in the message does not count"""
        p = write_log(
            self.dir,
            "t [ERROR] rejected [ERROR 403]\n"
            "t [INFO] saw [WARN] in payload [ERROR]\n"
            "   t [WARN] indented line\n",
        )
        self.assertEqual(count_log_levels(p), {"ERROR": 1, "WARN": 1, "INFO": 1})

    def test_large_file(self):
        """Handles a file with tens of thousands of lines"""
        lines = []
        for i in range(30000):
            level = ("INFO", "WARN", "ERROR", "DEBUG")[i % 4]
            lines.append(f"2024-05-01 10:00:{i % 60:02d} [{level}] mdmclient: event {i}")
        p = write_log(self.dir, "\n".join(lines) + "\n")
        self.assertEqual(count_log_levels(p), {"ERROR": 7500, "WARN": 7500, "INFO": 7500})

    def test_missing_file_raises(self):
        """A missing file raises FileNotFoundError"""
        with self.assertRaises(FileNotFoundError):
            count_log_levels(Path(self.dir) / "nope.log")


if __name__ == "__main__":
    unittest.main()
