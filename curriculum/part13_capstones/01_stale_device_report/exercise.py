"""Stale device report.

Security wants a weekly Markdown report of laptops that have stopped checking in
to the MDM. You get the raw inventory export as CSV text with this header:

    serial,hostname,user,os,last_checkin

`last_checkin` is an ISO date (YYYY-MM-DD) or empty when the machine has never
checked in. The export is messy: blank lines, stray whitespace, mixed casing,
rows with missing trailing columns, and the same serial exported twice (a
re-enrolled machine). Split the work into four functions.

parse_inventory(text) -> list of dicts
- one dict per data row with keys serial, hostname, user, os, last_checkin
- every value is stripped; serial is uppercased; hostname and user are lowercased;
  a missing column (short row) becomes ""; an empty os becomes "unknown"
- skip rows whose serial is empty, and rows that are entirely blank

find_duplicates(devices) -> dict
- {serial: row_count} for every serial that appears more than once

find_stale(devices, today, max_days) -> list of dicts
- collapse duplicate serials first: keep the row with the most recent parseable
  last_checkin (if none parses, keep the first row)
- a device is stale when it never checked in, its date does not parse, or
  (today - last_checkin).days > max_days; exactly max_days is NOT stale
- return a copy of each stale row with an extra key "days": the age in days,
  or None when it never checked in (or the date did not parse)
- order: os (case-insensitive), then never-checked-in rows first, then oldest
  first (days descending), then serial

render_report(stale, duplicates, today, max_days, total) -> str
- `stale` is already in report order; `total` is the number of unique serials
- exact format, lines joined with "\\n", no trailing newline, blank line
  between sections, empty cells rendered as "-", "never" and "-" for the
  never-checked-in rows:

    # Stale device report

    Generated: 2024-06-01. Cutoff: 30 days. Devices: 7. Stale: 3. Never checked in: 1. Duplicate serials: 1.

    ## macOS (2)

    | serial | hostname | user | last check-in | days |
    |---|---|---|---|---|
    | C02DEF | mbp-b | bob | never | - |
    | C02ABC | mbp-a | alice | 2024-04-01 | 61 |

    ## Windows (1)

    | serial | hostname | user | last check-in | days |
    |---|---|---|---|---|
    | 7GH2K3Q | win-01 | carol | 2024-04-20 | 42 |

    ## Duplicate serials

    - C02ABC (2 rows)

- one "## <os> (<count>)" section per os, in the order the rows arrive
- when `stale` is empty, write the single line "No stale devices." instead of
  the sections; omit the "## Duplicate serials" section when there are none
  (duplicates are listed sorted by serial)

stale_device_report(text, today, max_days) -> str composes the four.

Examples:
    >>> rows = parse_inventory("serial,hostname,user,os,last_checkin\\n c02abc ,MBP-A,Alice,macOS,2024-04-01\\n")
    >>> rows[0]["serial"], rows[0]["hostname"], rows[0]["user"]
    ('C02ABC', 'mbp-a', 'alice')
    >>> find_stale(rows, date(2024, 6, 1), 30)[0]["days"]
    61
"""
import csv
from datetime import date
from typing import Dict, List, Optional


def parse_inventory(text: str) -> List[Dict[str, str]]:
    raise NotImplementedError("write parse_inventory")


def find_duplicates(devices: List[Dict[str, str]]) -> Dict[str, int]:
    raise NotImplementedError("write find_duplicates")


def find_stale(devices: List[Dict[str, str]], today: date, max_days: int) -> List[dict]:
    raise NotImplementedError("write find_stale")


def render_report(stale: List[dict], duplicates: Dict[str, int], today: date, max_days: int, total: int) -> str:
    raise NotImplementedError("write render_report")


def stale_device_report(text: str, today: date, max_days: int) -> str:
    raise NotImplementedError("write stale_device_report")
