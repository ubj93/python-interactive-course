"""Reference solutions for load_inventory_csv."""
import csv
from pathlib import Path
from typing import Dict, List, Optional, Union

REQUIRED = ("serial", "hostname", "os", "ram_gb", "disk_pct")


# Best practice: validate the header once, then a small helper turns one raw row into
# a typed dict or None. The loop stays readable and the "skip" policy lives in one place.
def _convert(raw: Dict[Optional[str], str]) -> Optional[Dict[str, object]]:
    if None in raw:                      # more cells than header columns
        return None
    cells = {}
    for key in REQUIRED:
        value = raw.get(key)
        if value is None:                # fewer cells than header columns
            return None
        cells[key] = value.strip()
    if not cells["serial"]:
        return None
    try:
        ram_gb = int(cells["ram_gb"])
        disk_pct = float(cells["disk_pct"])
    except ValueError:
        return None
    return {
        "serial": cells["serial"],
        "hostname": cells["hostname"],
        "os": cells["os"],
        "ram_gb": ram_gb,
        "disk_pct": disk_pct,
    }


def load_inventory_csv(path: Union[str, Path]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        if header:
            missing = [c for c in REQUIRED if c not in header]
            if missing:
                raise ValueError(f"missing columns: {', '.join(missing)}")
        for raw in reader:
            row = _convert(raw)
            if row is not None:
                rows.append(row)
    return rows


# Clever: a converter table maps column -> function; str is a no-op for text columns.
# Adding a typed column later is one line of data, not a new block of code.
CONVERTERS = {"serial": str, "hostname": str, "os": str, "ram_gb": int, "disk_pct": float}


def load_inventory_csv_table(path: Union[str, Path]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        if header and not set(CONVERTERS) <= set(header):
            raise ValueError("missing columns")
        for raw in reader:
            if None in raw or any(raw.get(k) is None for k in CONVERTERS):
                continue
            try:
                row = {k: fn(raw[k].strip()) for k, fn in CONVERTERS.items()}
            except ValueError:
                continue
            if row["serial"]:
                rows.append(row)
    return rows
