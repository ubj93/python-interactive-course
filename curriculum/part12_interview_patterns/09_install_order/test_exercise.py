import unittest

from exercise import install_order


class TestInstallOrder(unittest.TestCase):
    def test_no_dependencies(self):
        """Independent packages come out alphabetically"""
        self.assertEqual(install_order({"osquery": [], "munki": [], "jamf": []}), ["jamf", "munki", "osquery"])

    def test_chain(self):
        """A linear chain installs from the bottom up"""
        self.assertEqual(install_order({"app": ["runtime"], "runtime": ["libc"], "libc": []}), ["libc", "runtime", "app"])

    def test_unlisted_dependency_included(self):
        """A dependency that is not a key is still a package"""
        self.assertEqual(install_order({"agent": ["sdk"]}), ["sdk", "agent"])

    def test_alphabetical_among_ready(self):
        """Ready packages are taken alphabetically, not in dict order"""
        packages = {"zsh": [], "bash": [], "fish": ["bash"], "tools": ["fish", "zsh"]}
        self.assertEqual(install_order(packages), ["bash", "fish", "zsh", "tools"])

    def test_diamond_and_duplicates(self):
        """Shared dependencies appear once; duplicate list entries are harmless"""
        packages = {"app": ["net", "ui", "net"], "net": ["core"], "ui": ["core"], "core": []}
        self.assertEqual(install_order(packages), ["core", "net", "ui", "app"])

    def test_empty(self):
        """An empty catalog gives an empty order"""
        self.assertEqual(install_order({}), [])

    def test_cycle_raises_naming_members(self):
        """A cycle raises ValueError naming every package on it, not the innocent ones"""
        with self.assertRaises(ValueError) as ctx:
            install_order({"a": ["b"], "b": ["c"], "c": ["a"], "zlib": []})
        message = str(ctx.exception)
        for name in ("a", "b", "c"):
            self.assertIn(name, message)
        self.assertNotIn("zlib", message)
        with self.assertRaises(ValueError) as ctx:
            install_order({"self": ["self"]})
        self.assertIn("self", str(ctx.exception))

    def test_large_chain(self):
        """3,000 packages in a chain given in the wrong order"""
        packages = {f"pkg{i:04d}": [f"pkg{i + 1:04d}"] for i in range(2999)}
        expected = [f"pkg{i:04d}" for i in range(2999, -1, -1)]
        self.assertEqual(install_order(packages), expected)


if __name__ == "__main__":
    unittest.main()
