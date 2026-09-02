import unittest

from exercise import collect_items, expand_includes, find_conflicts, resolve_manifest

MANIFESTS = {
    "site_default": {"included_manifests": ["security_baseline"], "managed_installs": ["Chrome", "Slack"]},
    "security_baseline": {"managed_installs": ["CrowdStrike"], "managed_uninstalls": ["Slack"]},
    "eng_laptops": {"included_manifests": ["site_default", "security_baseline"], "managed_installs": ["Docker"]},
}


class TestManifestResolver(unittest.TestCase):
    def test_expand_includes_depth_first(self):
        """expand_includes lists the manifest first, then includes depth-first in listed order"""
        manifests = {"a": {"included_manifests": ["b", "c"]}, "b": {"included_manifests": ["d"]}, "c": {}, "d": {}}
        self.assertEqual(expand_includes(manifests, "a"), ["a", "b", "d", "c"])
        self.assertEqual(expand_includes(manifests, "c"), ["c"])
        self.assertEqual(expand_includes({"solo": {"managed_installs": ["x"]}}, "solo"), ["solo"])

    def test_expand_includes_diamond_once(self):
        """expand_includes visits a manifest reachable by two paths only once"""
        self.assertEqual(expand_includes(MANIFESTS, "eng_laptops"), ["eng_laptops", "site_default", "security_baseline"])
        manifests = {"top": {"included_manifests": ["l", "r"]}, "l": {"included_manifests": ["base"]}, "r": {"included_manifests": ["base"]}, "base": {}}
        self.assertEqual(expand_includes(manifests, "top"), ["top", "l", "base", "r"])

    def test_expand_includes_errors(self):
        """expand_includes raises KeyError for unknown names and ValueError naming the cycle"""
        with self.assertRaises(KeyError):
            expand_includes(MANIFESTS, "nope")
        with self.assertRaises(KeyError):
            expand_includes({"a": {"included_manifests": ["ghost"]}}, "a")
        cyclic = {"a": {"included_manifests": ["b"]}, "b": {"included_manifests": ["c"]}, "c": {"included_manifests": ["a"]}}
        with self.assertRaises(ValueError) as ctx:
            expand_includes(cyclic, "a")
        self.assertIn("a -> b -> c -> a", str(ctx.exception))
        with self.assertRaises(ValueError) as ctx:
            expand_includes({"self": {"included_manifests": ["self"]}}, "self")
        self.assertIn("self -> self", str(ctx.exception))

    def test_collect_items_order_and_dedupe(self):
        """collect_items keeps first-seen order, drops duplicates, strips names, ignores empties"""
        manifests = {
            "a": {"managed_installs": ["Zoom ", "Chrome", "", " Zoom"], "managed_uninstalls": ["Java"]},
            "b": {"managed_installs": ["Chrome", "Slack"], "managed_uninstalls": ["Flash", None, "Java"]},
            "c": {},
        }
        self.assertEqual(collect_items(manifests, ["a", "b", "c"]), (["Zoom", "Chrome", "Slack"], ["Java", "Flash"]))
        self.assertEqual(collect_items(manifests, ["b", "a"]), (["Chrome", "Slack", "Zoom"], ["Flash", "Java"]))
        self.assertEqual(collect_items(manifests, []), ([], []))

    def test_find_conflicts(self):
        """find_conflicts returns the sorted intersection"""
        self.assertEqual(find_conflicts(["b", "a", "c"], ["c", "x", "a"]), ["a", "c"])
        self.assertEqual(find_conflicts(["a"], ["b"]), [])
        self.assertEqual(find_conflicts([], []), [])

    def test_resolve_manifest_end_to_end(self):
        """resolve_manifest composes the pieces and removes conflicts from both lists"""
        self.assertEqual(
            resolve_manifest(MANIFESTS, "eng_laptops"),
            {
                "manifests": ["eng_laptops", "site_default", "security_baseline"],
                "installs": ["Docker", "Chrome", "CrowdStrike"],
                "uninstalls": [],
                "conflicts": ["Slack"],
                "missing": [],
            },
        )
        self.assertEqual(
            resolve_manifest(MANIFESTS, "security_baseline"),
            {"manifests": ["security_baseline"], "installs": ["CrowdStrike"], "uninstalls": ["Slack"], "conflicts": [], "missing": []},
        )

    def test_resolve_manifest_with_catalog(self):
        """resolve_manifest reports items absent from the catalog without removing them"""
        result = resolve_manifest(MANIFESTS, "eng_laptops", catalog=["Chrome", "Docker", "Slack"])
        self.assertEqual(result["missing"], ["CrowdStrike"])
        self.assertEqual(result["installs"], ["Docker", "Chrome", "CrowdStrike"])
        result = resolve_manifest(MANIFESTS, "security_baseline", catalog=set())
        self.assertEqual(result["missing"], ["CrowdStrike", "Slack"])
        self.assertEqual(resolve_manifest(MANIFESTS, "security_baseline", catalog=["CrowdStrike", "Slack"])["missing"], [])

    def test_resolve_manifest_messy_tree(self):
        """resolve_manifest on a deeper tree with a diamond, whitespace, and multiple conflicts"""
        manifests = {
            "laptop-alice": {"included_manifests": ["dept-eng", "site"], "managed_installs": ["Docker", " VSCode"], "managed_uninstalls": ["Zoom"]},
            "dept-eng": {"included_manifests": ["site"], "managed_installs": ["Zoom", "Docker", "Git"], "managed_uninstalls": ["Flash "]},
            "site": {"included_manifests": ["baseline"], "managed_installs": ["Chrome", "Flash", ""]},
            "baseline": {"managed_installs": ["CrowdStrike", "Chrome"], "managed_uninstalls": ["Java", "VSCode"]},
        }
        self.assertEqual(
            resolve_manifest(manifests, "laptop-alice", catalog={"Docker", "Git", "Chrome", "CrowdStrike", "Java"}),
            {
                "manifests": ["laptop-alice", "dept-eng", "site", "baseline"],
                "installs": ["Docker", "Git", "Chrome", "CrowdStrike"],
                "uninstalls": ["Java"],
                "conflicts": ["Flash", "VSCode", "Zoom"],
                "missing": [],
            },
        )


if __name__ == "__main__":
    unittest.main()
