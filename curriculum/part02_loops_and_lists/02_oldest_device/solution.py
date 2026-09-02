"""Reference solutions for oldest_device."""
from typing import Any, Dict, List, Optional


# Best practice: the running-best pattern. Starting from None handles the empty list and
# the all-skipped list without special cases; strict `<` keeps the first of equal dates.
def oldest_device(devices: List[Dict[str, Any]]) -> Optional[str]:
    best: Optional[Dict[str, Any]] = None
    for device in devices:
        enrolled = device.get("enrolled")
        if enrolled is None:
            continue
        if best is None or enrolled < best["enrolled"]:
            best = device
    return None if best is None else best["hostname"]


# Clever: min() with a key does the running best for you, and default=None covers the
# empty case. min() is stable too: it keeps the first of equal keys, just like the loop.
def oldest_device_min(devices: List[Dict[str, Any]]) -> Optional[str]:
    dated = [d for d in devices if d.get("enrolled") is not None]
    best = min(dated, key=lambda d: d["enrolled"], default=None)
    return None if best is None else best["hostname"]
