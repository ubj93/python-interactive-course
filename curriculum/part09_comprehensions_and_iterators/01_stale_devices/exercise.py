"""Find stale devices.

A device that has not checked in with the MDM for more than `max_days` days is
"stale" and goes on the follow-up list. Write `stale_devices(devices, today,
max_days=30)` as a single list comprehension.

- `devices` is a list of dicts with keys "hostname" (str) and "last_seen"
  (a `datetime.date`, or None when the device has never checked in).
- `today` is a `datetime.date` passed in by the caller; never call
  `date.today()` yourself, the tests pin the date.
- A device is stale when `last_seen` is None, or when the number of days from
  `last_seen` to `today` is strictly greater than `max_days`. Exactly
  `max_days` days ago is still fresh.
- Return the hostnames of the stale devices, in the same order as the input.
  An empty input gives an empty list.

Examples:
    >>> today = date(2024, 6, 1)
    >>> devices = [
    ...     {"hostname": "mbp-j-doe", "last_seen": date(2024, 5, 30)},
    ...     {"hostname": "win-lab-01", "last_seen": date(2024, 4, 1)},
    ...     {"hostname": "ipad-kiosk", "last_seen": None},
    ... ]
    >>> stale_devices(devices, today)
    ['win-lab-01', 'ipad-kiosk']
    >>> stale_devices(devices, today, max_days=1)
    ['mbp-j-doe', 'win-lab-01', 'ipad-kiosk']
"""
from datetime import date
from typing import Any, Dict, List


def stale_devices(devices: List[Dict[str, Any]], today: date, max_days: int = 30) -> List[str]:
    raise NotImplementedError("write stale_devices")
