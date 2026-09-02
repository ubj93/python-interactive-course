import tempfile
import unittest
from pathlib import Path

from exercise import load_inventory_csv


def write_csv(directory, text):
    p = Path(directory) / "inv.csv"
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    return p


HEADER = "serial,hostname,os,ram_gb,disk_pct\n"


class TestLoadInventoryCsv(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def test_good_rows_with_types(self):
        """Parses rows and converts ram_gb to int and disk_pct to float"""
        p = write_csv(self.dir, HEADER + "C02XG1234ABC,mbp-j-doe,macOS,16,0.62\n7GH2K3Q,win-lab-01,Windows,8,0.91\n")
        rows = load_inventory_csv(p)
        self.assertEqual(
            rows,
            [
                {"serial": "C02XG1234ABC", "hostname": "mbp-j-doe", "os": "macOS", "ram_gb": 16, "disk_pct": 0.62},
                {"serial": "7GH2K3Q", "hostname": "win-lab-01", "os": "Windows", "ram_gb": 8, "disk_pct": 0.91},
            ],
        )
        self.assertIsInstance(rows[0]["ram_gb"], int)
        self.assertIsInstance(rows[0]["disk_pct"], float)

    def test_header_only_and_empty(self):
        """A header-only file and an empty file both give []"""
        self.assertEqual(load_inventory_csv(write_csv(self.dir, HEADER)), [])
        self.assertEqual(load_inventory_csv(write_csv(self.dir, "")), [])

    def test_strips_cells(self):
        """Whitespace around cells is stripped before conversion"""
        p = write_csv(self.dir, HEADER + " 7GH2K3Q , win-lab-01 , Windows , 8 , 0.91 \n")
        self.assertEqual(
            load_inventory_csv(str(p)),
            [{"serial": "7GH2K3Q", "hostname": "win-lab-01", "os": "Windows", "ram_gb": 8, "disk_pct": 0.91}],
        )

    def test_skips_malformed_rows(self):
        """Bad numbers, empty serials, short and long rows are skipped"""
        p = write_csv(
            self.dir,
            HEADER
            + "C02XG1234ABC,mbp-j-doe,macOS,16,0.62\n"
            + "C02ZZ9999XYZ,mbp-broken,macOS,sixteen,0.4\n"
            + ",orphan-box,Linux,4,0.5\n"
            + "JK1L2M3,ubuntu-ci,Linux,64\n"
            + "C02YY8888ABC,mbp-extra,macOS,8,0.33,unexpected\n"
            + "ABCDEF1,win-lab-02,Windows,16,n/a\n"
            + "FVFXC1234A,mbp-a-lee,macOS,32,0.15\n",
        )
        self.assertEqual([r["serial"] for r in load_inventory_csv(p)], ["C02XG1234ABC", "FVFXC1234A"])

    def test_quoted_cells_and_extra_columns(self):
        """Quoted cells with commas work and extra header columns are ignored"""
        p = write_csv(
            self.dir,
            "serial,hostname,os,ram_gb,disk_pct,department\n"
            '"C02XW5555ABC","mbp-quoted, with comma",macOS,16,0.77,Design\n',
        )
        self.assertEqual(
            load_inventory_csv(p),
            [{"serial": "C02XW5555ABC", "hostname": "mbp-quoted, with comma", "os": "macOS", "ram_gb": 16, "disk_pct": 0.77}],
        )

    def test_fixture_file(self):
        """The shipped fixtures/inventory.csv yields exactly the four good rows"""
        rows = load_inventory_csv("fixtures/inventory.csv")
        self.assertEqual([r["serial"] for r in rows], ["C02XG1234ABC", "7GH2K3Q", "FVFXC1234A", "C02XW5555ABC"])
        self.assertEqual(rows[1], {"serial": "7GH2K3Q", "hostname": "win-lab-01", "os": "Windows", "ram_gb": 8, "disk_pct": 0.91})

    def test_missing_required_column_raises(self):
        """A header without one of the required columns raises ValueError"""
        p = write_csv(self.dir, "serial,hostname,os,ram_gb\nC02XG1234ABC,mbp-j-doe,macOS,16\n")
        with self.assertRaises(ValueError):
            load_inventory_csv(p)


if __name__ == "__main__":
    unittest.main()
