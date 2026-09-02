"""Reference solutions for count_online."""
from typing import Any, Dict, List


# Best practice: the count accumulator. `.get` tolerates a missing key, `or ""` turns None
# into something strip() accepts, and the normalisation happens once per record.
def count_online(devices: List[Dict[str, Any]]) -> int:
    online = 0
    for device in devices:
        status = (device.get("status") or "").strip().lower()
        if status == "online":
            online += 1
    return online


# Clever: sum() over a generator of booleans. True counts as 1, False as 0. Same logic,
# one expression; fine once the reader knows the idiom, harder to add a print() to.
def count_online_sum(devices: List[Dict[str, Any]]) -> int:
    return sum((d.get("status") or "").strip().lower() == "online" for d in devices)
