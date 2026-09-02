import unittest

from exercise import invert_index


class TestInvertIndex(unittest.TestCase):
    def test_basic(self):
        """Each serial maps back to its user"""
        self.assertEqual(
            invert_index({"jdoe": ["C02A", "C02B"], "asmith": ["C02C"]}),
            {"C02A": "jdoe", "C02B": "jdoe", "C02C": "asmith"},
        )

    def test_empty(self):
        """Empty input and empty device lists give an empty dict"""
        self.assertEqual(invert_index({}), {})
        self.assertEqual(invert_index({"jdoe": [], "asmith": []}), {})

    def test_order_of_encounter(self):
        """Keys follow user order then list order"""
        result = invert_index({"b": ["S3", "S1"], "a": ["S2"]})
        self.assertEqual(list(result), ["S3", "S1", "S2"])

    def test_repeat_under_same_user_ok(self):
        """A serial listed twice for one user is not a conflict"""
        self.assertEqual(invert_index({"jdoe": ["C02A", "C02A"]}), {"C02A": "jdoe"})

    def test_conflict_raises_with_serial(self):
        """A serial under two users raises ValueError naming the serial"""
        with self.assertRaises(ValueError) as ctx:
            invert_index({"jdoe": ["C02A"], "asmith": ["C02B", "C02A"]})
        self.assertIn("C02A", str(ctx.exception))

    def test_input_not_modified(self):
        """The input dict and its lists are left untouched"""
        data = {"jdoe": ["C02A"], "asmith": ["C02B"]}
        invert_index(data)
        self.assertEqual(data, {"jdoe": ["C02A"], "asmith": ["C02B"]})


if __name__ == "__main__":
    unittest.main()
