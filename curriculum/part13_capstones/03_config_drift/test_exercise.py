import unittest

from exercise import config_drift, diff_values, is_ignored


def rec(path, kind, expected=None, actual=None):
    return {"path": path, "kind": kind, "expected": expected, "actual": actual}


class TestConfigDrift(unittest.TestCase):
    def test_is_ignored_prefixes(self):
        """is_ignored matches an exact path or a dotted child, never a sibling with the same start"""
        self.assertTrue(is_ignored("dock.apps", ["dock.apps"]))
        self.assertTrue(is_ignored("dock.apps.1.name", {"dock.apps"}))
        self.assertFalse(is_ignored("dock.apps_extra", ["dock.apps"]))
        self.assertFalse(is_ignored("dock", ["dock.apps"]))
        self.assertFalse(is_ignored("anything", []))

    def test_scalar_change_is_type_sensitive(self):
        """diff_values reports changed scalars and treats a type change as drift"""
        self.assertEqual(diff_values(1, 2, "x"), [rec("x", "changed", 1, 2)])
        self.assertEqual(diff_values(1, 1.0, "x"), [rec("x", "changed", 1, 1.0)])
        self.assertEqual(diff_values(True, 1, "x"), [rec("x", "changed", True, 1)])
        self.assertEqual(diff_values("a", "a", "x"), [])
        self.assertEqual(diff_values(None, None, "x"), [])

    def test_missing_and_extra_keys(self):
        """diff_values finds missing and extra keys at nested paths"""
        expected = {"a": {"b": 1, "c": 2}}
        actual = {"a": {"b": 1, "d": 4}, "e": 5}
        got = sorted(diff_values(expected, actual), key=lambda r: r["path"])
        self.assertEqual(got, [rec("a.c", "missing", 2, None), rec("a.d", "extra", None, 4), rec("e", "extra", None, 5)])

    def test_lists_positional(self):
        """diff_values compares lists by position and recurses into list elements"""
        expected = {"apps": [{"name": "Safari"}, {"name": "Slack"}, {"name": "Zoom"}]}
        actual = {"apps": [{"name": "Safari"}, {"name": "Teams"}]}
        got = sorted(diff_values(expected, actual), key=lambda r: r["path"])
        self.assertEqual(got, [rec("apps.1.name", "changed", "Slack", "Teams"), rec("apps.2", "missing", {"name": "Zoom"}, None)])
        self.assertEqual(diff_values([1], [1, 2, 3], "n"), [rec("n.1", "extra", None, 2), rec("n.2", "extra", None, 3)])

    def test_container_kind_mismatch(self):
        """diff_values reports a dict against a list or scalar as one changed record"""
        self.assertEqual(diff_values({"a": {"b": 1}}, {"a": [1]}), [rec("a", "changed", {"b": 1}, [1])])
        self.assertEqual(diff_values({"a": [1, 2]}, {"a": "1,2"}), [rec("a", "changed", [1, 2], "1,2")])

    def test_config_drift_sorted_by_segments(self):
        """config_drift sorts by path segments so apps.10 precedes apps.2"""
        expected = {"apps": list(range(12)), "z": 1, "b": {"y": 1, "x": 2}}
        actual = {"apps": [0, 1, 9, 3, 4, 5, 6, 7, 8, 9, 99, 11], "z": 2, "b": {"y": 1, "x": 3}}
        paths = [r["path"] for r in config_drift(expected, actual)]
        self.assertEqual(paths, ["apps.10", "apps.2", "b.x", "z"])

    def test_config_drift_ignore_prunes(self):
        """config_drift drops records under ignored prefixes, including whole subtrees"""
        expected = {"dock": {"apps": ["a", "b"], "size": 48}, "uuid": "1", "os": {"build": "23F79"}}
        actual = {"dock": {"apps": ["a", "c", "d"], "size": 32}, "uuid": "2", "os": {"build": "23G80"}}
        self.assertEqual(
            config_drift(expected, actual, ignore=["dock.apps", "uuid"]),
            [rec("dock.size", "changed", 48, 32), rec("os.build", "changed", "23F79", "23G80")],
        )
        self.assertEqual(config_drift(expected, actual, ignore=["dock", "uuid", "os"]), [])

    def test_config_drift_realistic_profile(self):
        """config_drift on a realistic baseline vs endpoint; identical configs give []"""
        baseline = {
            "security": {"firewall": {"enabled": True, "stealth": True}, "filevault": True, "screen_lock_secs": 300},
            "software": {"munki": {"repo": "https://munki.example.com", "catalogs": ["production"]}},
            "dock": {"tilesize": 48},
        }
        endpoint = {
            "security": {"firewall": {"enabled": True, "stealth": False, "logging": "detail"}, "filevault": True, "screen_lock_secs": "300"},
            "software": {"munki": {"repo": "https://munki.example.com", "catalogs": ["production", "testing"]}, "jamf": {"enrolled": True}},
        }
        self.assertEqual(
            config_drift(baseline, endpoint),
            [
                rec("dock", "missing", {"tilesize": 48}, None),
                rec("security.firewall.logging", "extra", None, "detail"),
                rec("security.firewall.stealth", "changed", True, False),
                rec("security.screen_lock_secs", "changed", 300, "300"),
                rec("software.jamf", "extra", None, {"enrolled": True}),
                rec("software.munki.catalogs.1", "extra", None, "testing"),
            ],
        )
        self.assertEqual(config_drift(baseline, baseline), [])


if __name__ == "__main__":
    unittest.main()
