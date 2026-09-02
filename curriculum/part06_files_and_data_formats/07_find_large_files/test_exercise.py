import tempfile
import unittest
from pathlib import Path

from exercise import find_large_files


def make_tree(root, files):
    """files: {relative path: size in bytes}"""
    for rel, size in files.items():
        p = Path(root) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"x" * size)


class TestFindLargeFiles(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        make_tree(
            self.root,
            {
                "install.log": 300,
                "cache/blob.bin": 5000,
                "cache/tiny.log": 10,
                "logs/old.LOG": 300,
                "logs/archive/app.tar.gz": 700,
                "README": 300,
            },
        )
        (self.root / "empty_dir").mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def test_threshold_inclusive(self):
        """Files at or above min_bytes are returned, smaller ones are not"""
        result = find_large_files(self.root, 700)
        self.assertEqual(result, [("cache/blob.bin", 5000), ("logs/archive/app.tar.gz", 700)])

    def test_recurses_and_sorts_by_size_then_path(self):
        """Walks subdirectories; sorted by size desc, ties by path asc"""
        self.assertEqual(
            find_large_files(str(self.root), 300),
            [
                ("cache/blob.bin", 5000),
                ("logs/archive/app.tar.gz", 700),
                ("README", 300),
                ("install.log", 300),
                ("logs/old.LOG", 300),
            ],
        )

    def test_suffix_filter_case_and_dot_insensitive(self):
        """'log', '.log' and '.LOG' all select the same files"""
        expected = [("install.log", 300), ("logs/old.LOG", 300), ("cache/tiny.log", 10)]
        for suffixes in (["log"], [".log"], [".LOG"], ["Log", "nothing"]):
            self.assertEqual(find_large_files(self.root, 1, suffixes), expected, suffixes)

    def test_multiple_suffixes_and_last_suffix_only(self):
        """Several suffixes combine; app.tar.gz matches 'gz' not 'tar'"""
        self.assertEqual(
            find_large_files(self.root, 1, ["bin", ".gz"]),
            [("cache/blob.bin", 5000), ("logs/archive/app.tar.gz", 700)],
        )
        self.assertEqual(find_large_files(self.root, 1, ["tar"]), [])

    def test_no_extension_and_empty_suffixes(self):
        """'' matches files without an extension; [] and None keep everything"""
        self.assertEqual(find_large_files(self.root, 1, [""]), [("README", 300)])
        self.assertEqual(len(find_large_files(self.root, 1, [])), 6)
        self.assertEqual(len(find_large_files(self.root, 1, None)), 6)

    def test_directories_excluded_and_nothing_found(self):
        """Directories never appear and a high threshold gives []"""
        result = find_large_files(self.root, 0)
        self.assertNotIn("cache", [name for name, _ in result])
        self.assertNotIn("empty_dir", [name for name, _ in result])
        self.assertEqual(find_large_files(self.root, 10 ** 9), [])

    def test_missing_root_raises(self):
        """A missing directory or a file as root raises NotADirectoryError"""
        with self.assertRaises(NotADirectoryError):
            find_large_files(self.root / "nope", 1)
        with self.assertRaises(NotADirectoryError):
            find_large_files(self.root / "install.log", 1)


if __name__ == "__main__":
    unittest.main()
