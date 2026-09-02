import os
import tempfile
import unittest
from pathlib import Path

from exercise import read_hostnames


def write_file(directory, name, text):
    p = Path(directory) / name
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    return p


class TestReadHostnames(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def test_one_per_line(self):
        """Returns one hostname per line in file order"""
        p = write_file(self.dir, "hosts.txt", "mbp-j-doe\nwin-lab-01\nubuntu-ci\n")
        self.assertEqual(read_hostnames(p), ["mbp-j-doe", "win-lab-01", "ubuntu-ci"])

    def test_strips_whitespace(self):
        """Strips spaces, tabs and Windows line endings"""
        p = write_file(self.dir, "hosts.txt", "  mbp-j-doe \r\n\twin-lab-01\t\r\nubuntu-ci")
        self.assertEqual(read_hostnames(p), ["mbp-j-doe", "win-lab-01", "ubuntu-ci"])

    def test_skips_blank_lines(self):
        """Blank and whitespace-only lines are skipped"""
        p = write_file(self.dir, "hosts.txt", "\nmbp-j-doe\n\n   \n\t\nwin-lab-01\n\n")
        self.assertEqual(read_hostnames(p), ["mbp-j-doe", "win-lab-01"])

    def test_skips_comments(self):
        """Lines whose first non-blank character is # are skipped"""
        p = write_file(self.dir, "hosts.txt", "# lab machines\nmbp-j-doe\n   # indented\n#win-lab-02\nwin-lab-01\n")
        self.assertEqual(read_hostnames(p), ["mbp-j-doe", "win-lab-01"])

    def test_keeps_case_and_accepts_str_path(self):
        """Does not change case and accepts a plain string path"""
        p = write_file(self.dir, "hosts.txt", "MBP-J-DOE\nWin_Lab_01\n")
        self.assertEqual(read_hostnames(str(p)), ["MBP-J-DOE", "Win_Lab_01"])

    def test_empty_file(self):
        """An empty file gives an empty list"""
        p = write_file(self.dir, "empty.txt", "")
        self.assertEqual(read_hostnames(p), [])

    def test_missing_file_raises(self):
        """A missing file raises FileNotFoundError"""
        with self.assertRaises(FileNotFoundError):
            read_hostnames(os.path.join(self.dir, "does-not-exist.txt"))


if __name__ == "__main__":
    unittest.main()
