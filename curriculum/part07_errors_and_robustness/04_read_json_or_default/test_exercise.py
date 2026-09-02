import tempfile
import unittest
from pathlib import Path

from exercise import read_json_or_default


class TestReadJsonOrDefault(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, name, text):
        p = self.dir / name
        p.write_text(text, encoding="utf-8")
        return p

    def test_reads_valid_json(self):
        """Valid JSON is parsed and returned"""
        p = self.write("state.json", '{"devices": ["C02XG1234ABC"], "n": 1}')
        self.assertEqual(read_json_or_default(p, {}), {"devices": ["C02XG1234ABC"], "n": 1})
        self.assertEqual(read_json_or_default(str(p), {}), {"devices": ["C02XG1234ABC"], "n": 1})

    def test_missing_file_gives_default(self):
        """A missing file returns the default"""
        self.assertEqual(read_json_or_default(self.dir / "missing.json", {"devices": []}), {"devices": []})
        self.assertEqual(read_json_or_default(self.dir / "missing.json", []), [])
        self.assertIsNone(read_json_or_default(self.dir / "missing.json", None))

    def test_empty_file_gives_default(self):
        """An empty or whitespace-only file returns the default"""
        self.assertEqual(read_json_or_default(self.write("empty.json", ""), {"n": 0}), {"n": 0})
        self.assertEqual(read_json_or_default(self.write("blank.json", " \n\t\n"), {"n": 0}), {"n": 0})

    def test_invalid_json_raises_with_path(self):
        """Broken JSON raises ValueError naming the file, chained to the decode error"""
        p = self.write("broken.json", '{"n": ')
        with self.assertRaises(ValueError) as cm:
            read_json_or_default(p, {})
        self.assertIn("broken.json", str(cm.exception))
        self.assertIsNotNone(cm.exception.__cause__)

    def test_non_ascii_content(self):
        """UTF-8 content is decoded correctly"""
        p = self.write("site.json", '{"site": "Zürich"}')
        self.assertEqual(read_json_or_default(p, {}), {"site": "Zürich"})

    def test_default_is_copied(self):
        """Mutating a returned default does not change the default for the next call"""
        default = {"devices": [], "seen": {"count": 0}}
        first = read_json_or_default(self.dir / "missing.json", default)
        first["devices"].append("C02XG1234ABC")
        first["seen"]["count"] = 99
        second = read_json_or_default(self.dir / "missing.json", default)
        self.assertEqual(second, {"devices": [], "seen": {"count": 0}})
        self.assertEqual(default, {"devices": [], "seen": {"count": 0}})

    def test_other_os_errors_propagate(self):
        """A directory in place of the file raises an OSError rather than returning the default"""
        with self.assertRaises(OSError) as cm:
            read_json_or_default(self.dir, {"n": 0})
        self.assertNotIsInstance(cm.exception, FileNotFoundError)


if __name__ == "__main__":
    unittest.main()
