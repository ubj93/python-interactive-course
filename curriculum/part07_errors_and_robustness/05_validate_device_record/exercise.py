"""Validate a device record and report every problem.

Records arrive from a self-service enrollment form. Instead of rejecting the
first bad field and making the user resubmit five times, report everything at
once. Write `validate_device_record(record)` that returns a list of error
messages; an empty list means the record is valid.

The required fields, in this order: serial, hostname, os, ram_gb, last_seen.

Checks, and the exact message each produces:
1. For each required field that is absent from the dict:
       "missing field: <name>"
   (present with any value, even None, is not "missing"; it is checked below)
2. For each required field that IS present, in the same order:
   - serial: a str of 7 to 12 characters, uppercase A-Z and digits 0-9 only
       "serial: must be 7-12 uppercase letters or digits, got <value!r>"
   - hostname: a str of 1 to 63 characters, letters, digits and hyphens only,
     not starting or ending with a hyphen (case does not matter)
       "hostname: must be 1-63 letters, digits or hyphens, got <value!r>"
   - os: one of "macOS", "Windows", "Linux" (exact spelling)
       "os: must be one of Linux, Windows, macOS, got <value!r>"
   - ram_gb: an int (bool does not count) greater than 0
       "ram_gb: must be a positive integer, got <value!r>"
   - last_seen: a str in YYYY-MM-DD form that datetime.date.fromisoformat
     accepts (so "2024-13-01" is invalid)
       "last_seen: must be an ISO date YYYY-MM-DD, got <value!r>"
3. For each key that is not one of the five, in sorted order:
       "unknown field: <name>"

Messages appear in the order of the checks above. <value!r> means the repr of
the value: strings come out quoted, numbers and None do not.

Examples:
    >>> validate_device_record({"serial": "C02XG1234ABC", "hostname": "mbp-j-doe",
    ...     "os": "macOS", "ram_gb": 16, "last_seen": "2024-05-01"})
    []
    >>> validate_device_record({"serial": "c02", "os": "ChromeOS", "ram_gb": "16",
    ...     "hostname": "ok-host", "last_seen": "2024-05-01", "colour": "blue"})
    ["serial: must be 7-12 uppercase letters or digits, got 'c02'",
     "os: must be one of Linux, Windows, macOS, got 'ChromeOS'",
     "ram_gb: must be a positive integer, got '16'",
     'unknown field: colour']
"""
from datetime import date
from typing import Any, Dict, List

REQUIRED = ("serial", "hostname", "os", "ram_gb", "last_seen")
KNOWN_OS = ("Linux", "Windows", "macOS")


def validate_device_record(record: Dict[str, Any]) -> List[str]:
    raise NotImplementedError("write validate_device_record")
