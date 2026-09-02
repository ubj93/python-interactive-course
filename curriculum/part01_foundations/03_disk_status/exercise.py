"""Classify disk usage.

A monitoring agent reports disk usage as a fraction between 0 and 1. Write
`disk_status(used_fraction)` that returns:

- "CRIT" when usage is 95% or more,
- "WARN" when usage is 80% or more but under 95%,
- "OK"   otherwise.

If the value is outside the range 0..1 (inclusive) or is `None`, return "UNKNOWN".

Examples:
    >>> disk_status(0.5)
    'OK'
    >>> disk_status(0.8)
    'WARN'
    >>> disk_status(0.95)
    'CRIT'
    >>> disk_status(1.2)
    'UNKNOWN'
"""
from typing import Optional


def disk_status(used_fraction: Optional[float]) -> str:
    raise NotImplementedError("write disk_status")
