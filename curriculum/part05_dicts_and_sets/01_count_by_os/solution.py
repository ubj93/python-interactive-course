"""Reference solutions for count_by_os."""
from typing import Any, Dict, List


# Best practice: the counting idiom. get(key, 0) + 1 handles "first time seen" and
# "seen before" in one expression, and insertion order gives first-seen key order for free.
def count_by_os(devices: List[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for device in devices:
        os_name = device.get("os") or "unknown"
        counts[os_name] = counts.get(os_name, 0) + 1
    return counts


# Clever: collections.Counter is the same loop, packaged. It is a dict subclass, so the
# result compares equal to a plain dict; the `or "unknown"` normalisation still has to be yours.
def count_by_os_counter(devices: List[Dict[str, Any]]) -> Dict[str, int]:
    from collections import Counter

    return dict(Counter(device.get("os") or "unknown" for device in devices))
