"""Count the devices that are online.

The MDM API returns the fleet as a list of dicts, one per device. Each record
has a "hostname" and usually a "status". Write `count_online(devices)` that
returns how many records are online.

Rules:
- a device is online when its status, ignoring case and surrounding
  whitespace, is exactly "online" ("Online", " ONLINE " both count)
- a record with no "status" key, or whose status is None, is not online
- an empty list gives 0
- do not modify the records

Examples:
    >>> fleet = [
    ...     {"hostname": "mbp-j-doe", "status": "online"},
    ...     {"hostname": "win-lab-01", "status": "offline"},
    ...     {"hostname": "nuc-01", "status": " Online "},
    ... ]
    >>> count_online(fleet)
    2
    >>> count_online([])
    0
"""
from typing import Any, Dict, List


def count_online(devices: List[Dict[str, Any]]) -> int:
    raise NotImplementedError("write count_online")
