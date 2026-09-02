import io
import os
import tempfile
import unittest
from itertools import count

from exercise import read_lines_lazy


class TestReadLinesLazy(unittest.TestCase):
    def test_strips_newlines_and_whitespace(self):
        """Lines come back without surrounding whitespace or newlines"""
        src = io.StringIO("mbp-j-doe\n  win-lab-01  \n\tmbp-a-lee\n")
        self.assertEqual(list(read_lines_lazy(src)), ["mbp-j-doe", "win-lab-01", "mbp-a-lee"])

    def test_skips_blank_lines(self):
        """Empty and whitespace-only lines are skipped"""
        src = io.StringIO("\n\n a \n   \n\t\nb\n\n")
        self.assertEqual(list(read_lines_lazy(src)), ["a", "b"])

    def test_skips_comment_lines(self):
        """Lines that start with # (after whitespace) are skipped"""
        src = io.StringIO("# header\nmbp-j-doe\n   # indented comment\n#\nwin-lab-01\n")
        self.assertEqual(list(read_lines_lazy(src)), ["mbp-j-doe", "win-lab-01"])

    def test_strips_inline_comments(self):
        """Text after a # on a data line is dropped, and the rest is stripped"""
        src = io.StringIO("mbp-j-doe   # jane's laptop\nwin-lab-01#lab\nmbp-a-lee # a # b\n")
        self.assertEqual(list(read_lines_lazy(src)), ["mbp-j-doe", "win-lab-01", "mbp-a-lee"])

    def test_accepts_any_iterable_and_returns_an_iterator(self):
        """A plain list works, and the result is an iterator with __next__"""
        result = read_lines_lazy(["a", "# c", "", "b"])
        self.assertTrue(hasattr(result, "__next__"))
        self.assertNotIsInstance(result, list)
        self.assertEqual(list(result), ["a", "b"])
        self.assertEqual(list(read_lines_lazy([])), [])

    def test_is_lazy(self):
        """Only as many source lines as needed are consumed"""
        consumed = []

        def endless():
            for i in count():
                consumed.append(i)
                yield "# comment" if i % 2 else f"host-{i}"

        gen = read_lines_lazy(endless())
        self.assertEqual(next(gen), "host-0")
        self.assertEqual(next(gen), "host-2")
        self.assertEqual(consumed, [0, 1, 2])

    def test_real_file(self):
        """Works on an open text file"""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "hosts.txt")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("# hosts\nmbp-j-doe\n\nwin-lab-01 # lab\n")
            with open(path, encoding="utf-8") as fh:
                self.assertEqual(list(read_lines_lazy(fh)), ["mbp-j-doe", "win-lab-01"])


if __name__ == "__main__":
    unittest.main()
