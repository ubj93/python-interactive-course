"""Load a device inventory from CSV.

The asset system exports a CSV with the header

    serial,hostname,os,ram_gb,disk_pct

Write `load_inventory_csv(path)` that reads the file with `csv.DictReader` and
returns a list of dicts, one per good row, in file order. Each dict has exactly
the keys serial, hostname, os (strings), ram_gb (int) and disk_pct (float).

Rules:
- open the file with encoding="utf-8" and newline=""
- strip whitespace from every cell before using it
- ram_gb must convert with int(), disk_pct with float(); otherwise the row is
  malformed
- a row with an empty serial is malformed
- a row with fewer cells than the header (DictReader fills the missing keys with
  None) or more cells than the header (extras land under the key None) is malformed
- malformed rows are skipped silently; the good rows around them are still returned
- extra header columns are ignored; a header missing any of the five required
  columns raises ValueError
- a file with only a header (or nothing at all) returns []
- `path` may be a str or a pathlib.Path

A sample export is in fixtures/inventory.csv; open it and predict the result before
running the tests.

Examples:
    >>> load_inventory_csv("fixtures/inventory.csv")[0]
    {'serial': 'C02XG1234ABC', 'hostname': 'mbp-j-doe', 'os': 'macOS', 'ram_gb': 16, 'disk_pct': 0.62}
"""
import csv
from pathlib import Path
from typing import Dict, List, Union

REQUIRED = ("serial", "hostname", "os", "ram_gb", "disk_pct")


def load_inventory_csv(path: Union[str, Path]) -> List[Dict[str, object]]:
    raise NotImplementedError("write load_inventory_csv")
