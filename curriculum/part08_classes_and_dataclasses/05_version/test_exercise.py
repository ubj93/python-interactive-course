import unittest

from exercise import Version


class TestVersion(unittest.TestCase):
    def test_parses_parts_and_properties(self):
        """parts is a tuple of ints; major/minor/patch default to 0"""
        v = Version("14.5.1")
        self.assertEqual(v.parts, (14, 5, 1))
        self.assertEqual((v.major, v.minor, v.patch), (14, 5, 1))
        self.assertEqual((Version("15").major, Version("15").minor, Version("15").patch), (15, 0, 0))

    def test_trailing_zeros_and_prefix(self):
        """Trailing zeros are dropped (never below one part); 'v' and whitespace are ignored"""
        self.assertEqual(Version("1.2.0").parts, (1, 2))
        self.assertEqual(Version("0.0.0").parts, (0,))
        self.assertEqual(Version(" v14.5.0 \n").parts, (14, 5))
        self.assertEqual(Version("V2").parts, (2,))
        self.assertEqual(Version("1.0.3").parts, (1, 0, 3))

    def test_str_and_repr(self):
        """str is the canonical dotted form, repr rebuilds the object"""
        self.assertEqual(str(Version("v1.2.0")), "1.2")
        self.assertEqual(repr(Version("1.2.10")), "Version('1.2.10')")
        self.assertEqual(str(Version("2.0.0")), "2")

    def test_numeric_not_lexical(self):
        """1.10 is newer than 1.9 and 14.10 newer than 14.5"""
        self.assertTrue(Version("1.10") > Version("1.9"))
        self.assertTrue(Version("14.5") < Version("14.10"))
        self.assertTrue(Version("1.2.1") > Version("1.2"))

    def test_equality_and_hash(self):
        """Padded versions are equal, hash alike and dedupe in a set"""
        self.assertEqual(Version("14.5"), Version("14.5.0"))
        self.assertEqual(hash(Version("14.5")), hash(Version("v14.5.0.0")))
        self.assertEqual(len({Version("1.0"), Version("1"), Version("1.0.0"), Version("1.1")}), 2)
        self.assertNotEqual(Version("1.0"), Version("1.0.1"))

    def test_all_six_operators(self):
        """<, <=, ==, !=, >=, > all work via total_ordering"""
        a, b = Version("1.2"), Version("1.3")
        self.assertTrue(a < b and a <= b and a != b)
        self.assertTrue(b > a and b >= a)
        self.assertTrue(a <= Version("1.2.0") and a >= Version("1.2.0"))
        self.assertFalse(a > b or a >= b or a == b)

    def test_sorting_and_max(self):
        """sorted() and max() order versions correctly"""
        versions = [Version(s) for s in ["1.10", "1.9", "1.2.1", "1.2", "v2"]]
        self.assertEqual([str(v) for v in sorted(versions)], ["1.2", "1.2.1", "1.9", "1.10", "2"])
        self.assertEqual(str(max(versions)), "2")
        self.assertEqual(str(min(versions)), "1.2")

    def test_invalid_input_and_foreign_types(self):
        """Bad strings raise ValueError; comparing with other types behaves"""
        for bad in ["", "v", "1..2", "1.a", "1.2-beta", ".1", "1.", "14 5", "1.2.x"]:
            with self.assertRaises(ValueError, msg=repr(bad)):
                Version(bad)
        self.assertFalse(Version("1.2") == "1.2")
        self.assertTrue(Version("1.2") != (1, 2))
        with self.assertRaises(TypeError):
            Version("1.2") < "1.3"


if __name__ == "__main__":
    unittest.main()
