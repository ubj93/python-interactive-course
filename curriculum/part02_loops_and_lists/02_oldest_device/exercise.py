"""Find the longest-enrolled device.

Each device record has a "hostname" and an "enrolled" date written as an
ISO string "YYYY-MM-DD" (the day the machine was enrolled in the MDM). Write
`oldest_device(devices)` that returns the hostname of the device with the
earliest enrollment date.

ISO dates sort correctly as plain strings, so "2021-06-30" < "2022-01-05"
is True and you do not need the datetime module.

Rules:
- an empty list returns None
- when several devices share the earliest date, return the first one that
  appears in the list
- records whose "enrolled" key is missing or None are skipped; if every
  record is skipped, return None
- do not sort or modify the input list; one pass is enough

Examples:
    >>> fleet = [
    ...     {"hostname": "mbp-j-doe", "enrolled": "2023-02-14"},
    ...     {"hostname": "win-lab-01", "enrolled": "2021-06-30"},
    ...     {"hostname": "nuc-01", "enrolled": "2022-11-01"},
    ... ]
    >>> oldest_device(fleet)
    'win-lab-01'
    >>> oldest_device([])
"""
from typing import Any, Dict, List, Optional


def oldest_device(devices: List[Dict[str, Any]]) -> Optional[str]:
    raise NotImplementedError("write oldest_device")
