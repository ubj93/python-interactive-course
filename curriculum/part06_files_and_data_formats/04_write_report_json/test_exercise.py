import json
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

from exercise import read_report_json, write_report_json


class TestWriteReportJson(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "report.json"

    def tearDown(self):
        self._tmp.cleanup()

    def read_raw(self):
        with open(self.path, encoding="utf-8") as f:
            return f.read()

    def test_round_trip(self):
        """What is written can be read back unchanged"""
        report = {"fleet": "eu-west", "devices": [{"serial": "C02XG1234ABC", "ok": True, "issues": None}], "count": 1}
        write_report_json(self.path, report)
        self.assertEqual(read_report_json(self.path), report)

    def test_pretty_and_sorted(self):
        """Uses two-space indent and sorted keys"""
        write_report_json(str(self.path), {"b": 1, "a": {"z": True, "y": None}})
        expected = '{\n  "a": {\n    "y": null,\n    "z": true\n  },\n  "b": 1\n}\n'
        self.assertEqual(self.read_raw(), expected)

    def test_trailing_newline(self):
        """The file ends with exactly one newline"""
        write_report_json(self.path, {"x": 1})
        raw = self.read_raw()
        self.assertTrue(raw.endswith("}\n"))
        self.assertFalse(raw.endswith("\n\n"))

    def test_non_ascii_kept(self):
        """Non-ASCII text is written literally, not escaped"""
        write_report_json(self.path, {"site": "Zürich", "team": "日本"})
        raw = self.read_raw()
        self.assertIn("Zürich", raw)
        self.assertNotIn("\\u00fc", raw)
        self.assertEqual(read_report_json(self.path), {"site": "Zürich", "team": "日本"})

    def test_default_converts_special_types(self):
        """datetime, date, set and Path are converted by the default hook"""
        report = {
            "generated": datetime(2024, 5, 1, 10, 30, 0),
            "day": date(2024, 5, 1),
            "tags": {"loaner", "lab", "eu"},
            "log": Path("/var/log/jamf.log"),
        }
        write_report_json(self.path, report)
        self.assertEqual(
            read_report_json(self.path),
            {
                "day": "2024-05-01",
                "generated": "2024-05-01T10:30:00",
                "log": "/var/log/jamf.log",
                "tags": ["eu", "lab", "loaner"],
            },
        )

    def test_unsupported_type_raises(self):
        """A value the hook does not know raises TypeError"""
        with self.assertRaises(TypeError):
            write_report_json(self.path, {"weird": object()})

    def test_read_missing_file_raises(self):
        """Reading a missing file raises FileNotFoundError"""
        with self.assertRaises(FileNotFoundError):
            read_report_json(Path(self._tmp.name) / "missing.json")

    def test_output_is_valid_json(self):
        """The raw file parses with the json module"""
        write_report_json(self.path, {"nested": [1, 2.5, "three", [None]]})
        self.assertEqual(json.loads(self.read_raw()), {"nested": [1, 2.5, "three", [None]]})


if __name__ == "__main__":
    unittest.main()
