import builtins
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from exercise import tail_lines


def write_log(directory, text, name="agent.log"):
    p = Path(directory) / name
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    return p


class _NoSlurp:
    """A file wrapper that allows iteration but forbids read() and readlines()."""

    def __init__(self, f):
        self._f = f

    def __iter__(self):
        return iter(self._f)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return self._f.__exit__(*exc)

    def readline(self, *args):
        return self._f.readline(*args)

    def close(self):
        self._f.close()

    def read(self, *args):
        raise AssertionError("read() loads the whole file into memory; iterate the file instead")

    def readlines(self, *args):
        raise AssertionError("readlines() loads the whole file into memory; iterate the file instead")


class TestTailLines(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name
        self.five = write_log(self.dir, "l1\nl2\nl3\nl4\nl5\n")

    def tearDown(self):
        self._tmp.cleanup()

    def test_last_two(self):
        """Returns the last two lines, oldest first, without newlines"""
        self.assertEqual(tail_lines(self.five, 2), ["l4", "l5"])

    def test_default_n_is_ten(self):
        """Defaults to 10 lines and returns all when the file is shorter"""
        self.assertEqual(tail_lines(str(self.five)), ["l1", "l2", "l3", "l4", "l5"])
        self.assertEqual(tail_lines(self.five, 5), ["l1", "l2", "l3", "l4", "l5"])

    def test_zero_and_empty(self):
        """n == 0 and an empty file both give []"""
        self.assertEqual(tail_lines(self.five, 0), [])
        empty = write_log(self.dir, "", name="empty.log")
        self.assertEqual(tail_lines(empty, 3), [])

    def test_no_trailing_newline_and_crlf(self):
        """A last line without newline counts; CRLF endings are removed"""
        p = write_log(self.dir, "a\r\nb\r\nc", name="crlf.log")
        self.assertEqual(tail_lines(p, 2), ["b", "c"])
        self.assertEqual(tail_lines(p, 3), ["a", "b", "c"])

    def test_keeps_inner_whitespace(self):
        """Only the line ending is stripped, not spaces inside the line"""
        p = write_log(self.dir, "  indented  \n\nlast\n", name="ws.log")
        self.assertEqual(tail_lines(p, 3), ["  indented  ", "", "last"])

    def test_negative_raises(self):
        """A negative n raises ValueError"""
        with self.assertRaises(ValueError):
            tail_lines(self.five, -1)

    def test_missing_file_raises(self):
        """A missing file raises FileNotFoundError"""
        with self.assertRaises(FileNotFoundError):
            tail_lines(Path(self.dir) / "nope.log", 3)

    def test_does_not_slurp(self):
        """Iterates the file instead of calling read() or readlines()"""
        p = write_log(self.dir, "".join(f"line {i}\n" for i in range(5000)), name="big.log")
        real_open = builtins.open

        def guarded_open(*args, **kwargs):
            return _NoSlurp(real_open(*args, **kwargs))

        with mock.patch("builtins.open", guarded_open):
            self.assertEqual(tail_lines(p, 3), ["line 4997", "line 4998", "line 4999"])


if __name__ == "__main__":
    unittest.main()
