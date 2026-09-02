"""Count devices by operating system.

The inventory export is a list of device records (dicts). Write
`count_by_os(devices)` that returns a dict mapping each operating system name
to the number of devices running it.

Rules:
- the OS is the value of the "os" key, used exactly as written (no normalising)
- a device with no "os" key, or whose os is None or an empty string, is counted
  under the key "unknown"
- keys appear in the order the OS was first seen in the input
- an empty list gives {}

Build the dict with a loop and dict.get (or setdefault); this exercise is about
the counting idiom, so leave collections.Counter for later.

Examples:
    >>> count_by_os([{"os": "macOS"}, {"os": "Windows"}, {"os": "macOS"}])
    {'macOS': 2, 'Windows': 1}
    >>> count_by_os([{"hostname": "x"}, {"os": ""}])
    {'unknown': 2}
"""
from typing import Any, Dict, List


def count_by_os(devices: List[Dict[str, Any]]) -> Dict[str, int]:
    raise NotImplementedError("write count_by_os")
