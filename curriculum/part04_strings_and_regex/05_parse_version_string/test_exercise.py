import unittest

from exercise import parse_version_string


class TestParseVersionString(unittest.TestCase):
    def test_full_form(self):
        """Three numbers and a build"""
        self.assertEqual(parse_version_string("14.5.1 (23F79)"), ((14, 5, 1), "23F79"))

    def test_no_build(self):
        """Without parentheses the build is None"""
        self.assertEqual(parse_version_string("14.5.1"), ((14, 5, 1), None))

    def test_missing_parts_default_to_zero(self):
        """Missing minor and patch are 0"""
        self.assertEqual(parse_version_string("14.5"), ((14, 5, 0), None))
        self.assertEqual(parse_version_string("14"), ((14, 0, 0), None))
        self.assertEqual(parse_version_string("13 (22A380)"), ((13, 0, 0), "22A380"))

    def test_parts_are_ints(self):
        """Numbers come back as int, not str"""
        (major, minor, patch), _ = parse_version_string("10.15.7")
        self.assertIsInstance(major, int)
        self.assertEqual((major, minor, patch), (10, 15, 7))

    def test_whitespace_and_leading_v(self):
        """Surrounding whitespace, a leading v, and several spaces before the build"""
        self.assertEqual(parse_version_string("  v13.6.9 (22G830) "), ((13, 6, 9), "22G830"))
        self.assertEqual(parse_version_string("V12.7   (21H1123)"), ((12, 7, 0), "21H1123"))

    def test_tuple_ordering(self):
        """Parsed versions compare numerically, not as text"""
        self.assertGreater(parse_version_string("14.10")[0], parse_version_string("14.9")[0])
        self.assertLess(parse_version_string("10.15.7")[0], parse_version_string("11")[0])

    def test_invalid_raises(self):
        """Empty, non-numeric, four parts, empty parts and trailing text raise ValueError"""
        for bad in ["", "   ", "banana", "14.5.1.2", "14..5", "14.5.1 (23F79) extra", "14.5 ()", "v", "14.a"]:
            with self.assertRaises(ValueError, msg=bad):
                parse_version_string(bad)


if __name__ == "__main__":
    unittest.main()
