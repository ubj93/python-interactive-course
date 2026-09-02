"""Sort devices by several keys.

The fleet report groups devices by operating system, shows the most recently
seen machines first within each group, and breaks remaining ties by name so
the output is stable from run to run. Write `sort_devices(devices)`.

- `devices` is a list of dicts with keys "name" (str), "os" (str) and
  "last_seen" (a `datetime.date`, or None for a device that never checked in).
- Order: "os" ascending, then "last_seen" descending (newest first) with None
  after every real date, then "name" ascending.
- Return a new list; the input list must not be modified.
- Solve it with `sorted` and a key function (a tuple, or two stable passes).
  A date cannot be negated, but `date.toordinal()` gives an int that can.

Examples:
    >>> devices = [
    ...     {"name": "win-lab-01", "os": "windows", "last_seen": date(2024, 5, 1)},
    ...     {"name": "mbp-j-doe", "os": "mac", "last_seen": date(2024, 5, 3)},
    ...     {"name": "mbp-a-lee", "os": "mac", "last_seen": date(2024, 5, 9)},
    ...     {"name": "mbp-zz-old", "os": "mac", "last_seen": None},
    ... ]
    >>> [d["name"] for d in sort_devices(devices)]
    ['mbp-a-lee', 'mbp-j-doe', 'mbp-zz-old', 'win-lab-01']
"""
from datetime import date
from typing import Any, Dict, List


def sort_devices(devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    raise NotImplementedError("write sort_devices")
