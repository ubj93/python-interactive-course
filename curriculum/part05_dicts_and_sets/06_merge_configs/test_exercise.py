import unittest

from exercise import merge_configs


class TestMergeConfigs(unittest.TestCase):
    def test_flat_override(self):
        """Later scalar values win, new keys are added"""
        self.assertEqual(merge_configs({"a": 1, "b": 2}, {"b": 3, "c": 4}), {"a": 1, "b": 3, "c": 4})

    def test_no_args_and_single(self):
        """No configs gives {}; one config gives an equal copy"""
        self.assertEqual(merge_configs(), {})
        self.assertEqual(merge_configs({"a": {"b": 1}}), {"a": {"b": 1}})

    def test_nested_merge(self):
        """Nested dicts are merged key by key"""
        base = {"agent": {"interval": 60, "tags": ["base"]}, "site": "hq"}
        over = {"agent": {"interval": 30, "debug": True}}
        self.assertEqual(
            merge_configs(base, over),
            {"agent": {"interval": 30, "tags": ["base"], "debug": True}, "site": "hq"},
        )

    def test_lists_replaced_not_merged(self):
        """A later list replaces the earlier list entirely"""
        self.assertEqual(merge_configs({"tags": ["a", "b"]}, {"tags": ["c"]}), {"tags": ["c"]})

    def test_dict_vs_scalar_and_none(self):
        """A scalar replaces a dict, a dict replaces a scalar, None replaces a value"""
        self.assertEqual(merge_configs({"a": {"b": 1}}, {"a": 2}), {"a": 2})
        self.assertEqual(merge_configs({"a": 2}, {"a": {"b": 1}}), {"a": {"b": 1}})
        self.assertEqual(merge_configs({"a": 2}, {"a": None}), {"a": None})

    def test_key_order(self):
        """First-seen key order is kept, new keys appended"""
        result = merge_configs({"z": 1, "a": {"y": 1, "b": 2}}, {"a": {"b": 3, "c": 4}, "m": 5})
        self.assertEqual(list(result), ["z", "a", "m"])
        self.assertEqual(list(result["a"]), ["y", "b", "c"])

    def test_three_layers_and_type_error(self):
        """Three configs merge left to right; a non-dict argument raises TypeError"""
        result = merge_configs({"a": {"x": 1}}, {"a": {"y": 2}}, {"a": {"x": 3}, "b": 0})
        self.assertEqual(result, {"a": {"x": 3, "y": 2}, "b": 0})
        with self.assertRaises(TypeError):
            merge_configs({"a": 1}, ["not", "a", "dict"])

    def test_inputs_not_modified_or_shared(self):
        """Inputs are unchanged and the result does not share nested objects with them"""
        base = {"agent": {"interval": 60, "tags": ["base"]}}
        over = {"agent": {"debug": True}}
        result = merge_configs(base, over)
        self.assertEqual(base, {"agent": {"interval": 60, "tags": ["base"]}})
        self.assertEqual(over, {"agent": {"debug": True}})
        result["agent"]["tags"].append("changed")
        result["agent"]["interval"] = 1
        self.assertEqual(base["agent"]["tags"], ["base"])
        self.assertEqual(base["agent"]["interval"], 60)


if __name__ == "__main__":
    unittest.main()
