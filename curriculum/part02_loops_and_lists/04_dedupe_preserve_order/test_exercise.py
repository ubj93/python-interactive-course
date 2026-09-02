import unittest

from exercise import dedupe_preserve_order


class TestDedupePreserveOrder(unittest.TestCase):
    def test_no_duplicates(self):
        """A list without duplicates comes back unchanged"""
        self.assertEqual(dedupe_preserve_order(["a", "b", "c"]), ["a", "b", "c"])

    def test_removes_exact_duplicates(self):
        """Exact repeats are dropped, keeping the first"""
        self.assertEqual(dedupe_preserve_order(["a", "b", "a", "c", "b"]), ["a", "b", "c"])

    def test_case_insensitive(self):
        """Casing differences are still duplicates; the first spelling is kept"""
        hosts = ["mbp-j-doe", "win-lab-01", "MBP-J-DOE", "nuc-01", "Win-Lab-01"]
        self.assertEqual(dedupe_preserve_order(hosts), ["mbp-j-doe", "win-lab-01", "nuc-01"])

    def test_whitespace_insensitive(self):
        """Surrounding whitespace is ignored when comparing, but the first entry is kept as written"""
        self.assertEqual(dedupe_preserve_order([" nuc-01", "nuc-01 ", "nuc-01"]), [" nuc-01"])

    def test_empty(self):
        """An empty list gives an empty list"""
        self.assertEqual(dedupe_preserve_order([]), [])

    def test_order_of_first_occurrences(self):
        """Order follows first occurrences even when later repeats are interleaved"""
        hosts = ["c", "a", "b", "a", "c", "d", "b", "e"]
        self.assertEqual(dedupe_preserve_order(hosts), ["c", "a", "b", "d", "e"])

    def test_input_untouched(self):
        """The input list is not modified"""
        hosts = ["a", "A", "b"]
        result = dedupe_preserve_order(hosts)
        self.assertEqual(hosts, ["a", "A", "b"])
        self.assertIsNot(result, hosts)


if __name__ == "__main__":
    unittest.main()
