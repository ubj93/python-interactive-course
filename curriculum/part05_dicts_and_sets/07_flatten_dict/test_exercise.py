import unittest

from exercise import flatten_dict, unflatten_dict

PROFILE = {
    "payload": {"wifi": {"ssid": "corp", "hidden": False}, "vpn": {"server": "vpn.example.com"}},
    "name": "Base",
}
FLAT = {
    "payload.wifi.ssid": "corp",
    "payload.wifi.hidden": False,
    "payload.vpn.server": "vpn.example.com",
    "name": "Base",
}


class TestFlattenDict(unittest.TestCase):
    def test_flat_input_unchanged(self):
        """A dict with no nesting comes back equal"""
        self.assertEqual(flatten_dict({"a": 1, "b": "x"}), {"a": 1, "b": "x"})
        self.assertEqual(flatten_dict({}), {})

    def test_nested(self):
        """Nested keys are joined with dots, depth-first in input order"""
        self.assertEqual(flatten_dict(PROFILE), FLAT)
        self.assertEqual(list(flatten_dict(PROFILE)), list(FLAT))

    def test_leaves(self):
        """None, lists and empty dicts are leaves"""
        self.assertEqual(
            flatten_dict({"a": {"b": None, "c": [1, {"x": 2}], "d": {}}}),
            {"a.b": None, "a.c": [1, {"x": 2}], "a.d": {}},
        )

    def test_custom_separator(self):
        """The separator is configurable"""
        self.assertEqual(flatten_dict({"a": {"b": {"c": 1}}}, sep="/"), {"a/b/c": 1})

    def test_unflatten_basic(self):
        """Dotted keys are rebuilt into nested dicts"""
        self.assertEqual(unflatten_dict({"a.b": 1, "a.c": 2, "d": 3}), {"a": {"b": 1, "c": 2}, "d": 3})
        self.assertEqual(unflatten_dict({}), {})

    def test_unflatten_deep_and_separator(self):
        """Three levels deep with a custom separator"""
        self.assertEqual(unflatten_dict({"a/b/c": 1, "a/b/d": 2}, sep="/"), {"a": {"b": {"c": 1, "d": 2}}})

    def test_round_trip(self):
        """unflatten_dict(flatten_dict(d)) == d"""
        self.assertEqual(unflatten_dict(flatten_dict(PROFILE)), PROFILE)
        nested = {"a": {"b": {"c": {"d": [1, 2]}}, "e": None}, "f": {}}
        self.assertEqual(unflatten_dict(flatten_dict(nested)), nested)

    def test_unflatten_conflict_raises(self):
        """A key that is both a leaf and a prefix raises ValueError"""
        with self.assertRaises(ValueError):
            unflatten_dict({"a": 1, "a.b": 2})
        with self.assertRaises(ValueError):
            unflatten_dict({"a.b": 2, "a": 1})


if __name__ == "__main__":
    unittest.main()
