import unittest

from exercise import render_table


class TestRenderTable(unittest.TestCase):
    def test_header_only(self):
        """No rows gives the header line and the separator"""
        self.assertEqual(render_table(["host", "os"], []), "host  os\n----  --")

    def test_left_aligned_text(self):
        """Text cells are left-aligned and padded to the column width"""
        self.assertEqual(
            render_table(["host", "os"], [["mbp-1", "macOS"], ["win-lab-01", "Windows"]]),
            "host        os\n----------  -------\nmbp-1       macOS\nwin-lab-01  Windows",
        )

    def test_right_aligned_numbers(self):
        """int and float cells are right-aligned"""
        self.assertEqual(
            render_table(["host", "ram"], [["mbp-1", 16], ["win-lab-01", 8]]),
            "host        ram\n----------  ---\nmbp-1        16\nwin-lab-01    8",
        )
        self.assertEqual(
            render_table(["disk%"], [[83.5], [7]]),
            "disk%\n-----\n 83.5\n    7",
        )

    def test_width_from_header(self):
        """A header longer than every cell sets the width"""
        self.assertEqual(render_table(["hostname"], [["a"], ["bb"]]), "hostname\n--------\na\nbb")

    def test_none_and_bool(self):
        """None renders as '-' and bools are left-aligned text"""
        self.assertEqual(
            render_table(["host", "managed"], [["mbp-1", True], ["mbp-2", None]]),
            "host   managed\n-----  -------\nmbp-1  True\nmbp-2  -",
        )

    def test_no_trailing_whitespace(self):
        """Padding on the last column is trimmed and there is no final newline"""
        out = render_table(["n", "host"], [[1, "a"], [22, "bbbb"]])
        for line in out.split("\n"):
            self.assertEqual(line, line.rstrip(), repr(line))
        self.assertFalse(out.endswith("\n"))
        self.assertEqual(out, "n   host\n--  ----\n 1  a\n22  bbbb")

    def test_bad_input_raises(self):
        """A row of the wrong length or empty headers raises ValueError"""
        with self.assertRaises(ValueError):
            render_table(["a", "b"], [[1]])
        with self.assertRaises(ValueError):
            render_table([], [])


if __name__ == "__main__":
    unittest.main()
