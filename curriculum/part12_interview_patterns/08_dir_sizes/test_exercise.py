import unittest

from exercise import dir_sizes


class TestDirSizes(unittest.TestCase):
    def test_flat_files(self):
        """A root with only files sums them"""
        self.assertEqual(dir_sizes({"a.txt": 10, "b.txt": 5}), {"/": 15})

    def test_empty_root(self):
        """An empty tree is a root of size 0"""
        self.assertEqual(dir_sizes({}), {"/": 0})

    def test_nested_folders(self):
        """Folder totals include their subfolders"""
        tree = {"Applications": {"Safari.app": 300, "Utilities": {"Terminal.app": 50}}, "swapfile": 1000}
        self.assertEqual(
            dir_sizes(tree),
            {"/Applications/Utilities": 50, "/Applications": 350, "/": 1350},
        )

    def test_empty_folder_listed(self):
        """Empty folders appear with size 0"""
        self.assertEqual(dir_sizes({"Library": {}, "x": 1}), {"/Library": 0, "/": 1})

    def test_same_name_in_different_folders(self):
        """Folders with the same name in different places get distinct paths"""
        tree = {"Users": {"jdoe": {"Library": {"a": 1}}, "asmith": {"Library": {"b": 2, "c": 3}}}}
        result = dir_sizes(tree)
        self.assertEqual(result["/Users/jdoe/Library"], 1)
        self.assertEqual(result["/Users/asmith/Library"], 5)
        self.assertEqual(result["/Users"], 6)
        self.assertEqual(result["/"], 6)
        self.assertEqual(len(result), 6)

    def test_deep_chain(self):
        """A chain 200 folders deep produces correct paths and running totals"""
        node = {"leaf.bin": 1}
        for k in range(199, -1, -1):
            node = {f"d{k:03d}": node, "note.txt": 1}
        result = dir_sizes(node)
        self.assertEqual(result["/"], 201)
        self.assertEqual(result["/d000"], 200)
        path = "/" + "/".join(f"d{j:03d}" for j in range(200))
        self.assertEqual(result[path], 1)
        mid = "/" + "/".join(f"d{j:03d}" for j in range(100))
        self.assertEqual(result[mid], 101)
        self.assertEqual(len(result), 201)

    def test_large_wide_tree(self):
        """A tree of 3,061 folders: 60 top folders with 50 subfolders each"""
        tree = {f"top{i:02d}": {f"sub{j:02d}": {"file.bin": 1} for j in range(50)} for i in range(60)}
        result = dir_sizes(tree)
        self.assertEqual(len(result), 1 + 60 + 3000)
        self.assertEqual(result["/"], 3000)
        self.assertEqual(result["/top07"], 50)
        self.assertEqual(result["/top59/sub49"], 1)


if __name__ == "__main__":
    unittest.main()
