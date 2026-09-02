import unittest

from exercise import safe_int


class TestSafeInt(unittest.TestCase):
    def test_numeric_strings(self):
        """Plain, signed and padded numeric strings convert"""
        self.assertEqual(safe_int("42"), 42)
        self.assertEqual(safe_int(" -3 "), -3)
        self.assertEqual(safe_int("+7"), 7)
        self.assertEqual(safe_int("007"), 7)

    def test_ints_and_floats(self):
        """Ints pass through; floats truncate toward zero"""
        self.assertEqual(safe_int(16), 16)
        self.assertEqual(safe_int(3.9), 3)
        self.assertEqual(safe_int(-3.9), -3)

    def test_bad_strings_give_default(self):
        """Text that is not an integer gives the default"""
        for s in ["abc", "3.5", "1,024", "", "16 GB", "n/a"]:
            self.assertEqual(safe_int(s), 0, s)

    def test_none_and_wrong_types_give_default(self):
        """None, lists and dicts give the default instead of raising"""
        self.assertEqual(safe_int(None), 0)
        self.assertEqual(safe_int([1, 2]), 0)
        self.assertEqual(safe_int({"a": 1}), 0)

    def test_custom_default(self):
        """The default can be any value, including None"""
        self.assertEqual(safe_int("x", default=-1), -1)
        self.assertIsNone(safe_int("x", default=None))
        self.assertEqual(safe_int("5", default=-1), 5)

    def test_does_not_swallow_other_exceptions(self):
        """An exception that is not ValueError or TypeError propagates"""

        class Explodes:
            def __int__(self):
                raise RuntimeError("boom")

        with self.assertRaises(RuntimeError):
            safe_int(Explodes())


if __name__ == "__main__":
    unittest.main()
