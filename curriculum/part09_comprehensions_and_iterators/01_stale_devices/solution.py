"""Reference solutions for stale_devices."""
from datetime import date, timedelta
from typing import Any, Dict, List


# Best practice: filter-and-map in one comprehension. `is None or` short-circuits, so the
# subtraction never runs on None. The date passed in makes the function pure and testable.
def stale_devices(devices: List[Dict[str, Any]], today: date, max_days: int = 30) -> List[str]:
    return [
        d["hostname"]
        for d in devices
        if d["last_seen"] is None or (today - d["last_seen"]).days > max_days
    ]


# Clever: compute the cutoff date once and compare dates directly. Cheaper in a tight loop
# and the rule reads the way people say it: "last seen before the cutoff".
def stale_devices_cutoff(devices: List[Dict[str, Any]], today: date, max_days: int = 30) -> List[str]:
    cutoff = today - timedelta(days=max_days)
    return [d["hostname"] for d in devices if d["last_seen"] is None or d["last_seen"] < cutoff]
