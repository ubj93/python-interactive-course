"""Reference solutions for sort_devices."""
from datetime import date
from typing import Any, Dict, List, Tuple


# Best practice: one key function returning a tuple, one element per rule. The boolean
# `is None` sorts False (has a date) before True (None); negating the ordinal flips the
# date; the name is last. sorted() returns a new list and never touches the input.
def sort_devices(devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    def key(d: Dict[str, Any]) -> Tuple[str, bool, int, str]:
        seen = d["last_seen"]
        return (d["os"], seen is None, -seen.toordinal() if seen is not None else 0, d["name"])

    return sorted(devices, key=key)


# Clever: several stable sorts, least significant key first. No negation trick needed for
# the descending key, just reverse=True on that pass. Use this when a key cannot be
# negated (strings) or when the rules are easier to read one per line.
def sort_devices_multipass(devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    result = sorted(devices, key=lambda d: d["name"])
    result.sort(key=lambda d: (d["last_seen"] is not None, d["last_seen"] or date.min), reverse=True)
    result.sort(key=lambda d: d["os"])
    return result
