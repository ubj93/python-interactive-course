"""Timestamp compatibility shared by progress and timed CLI features.

New timestamps use UTC ISO 8601 with milliseconds and a trailing ``Z``, matching
the browser. Legacy timestamps without an offset are interpreted as local wall
time on the device reading them. Calendar-day keys always use that device's local
date; existing day keys and saved timestamps are preserved when loading progress.
"""
from __future__ import annotations

import datetime as dt
import re
from typing import Optional

UTC = dt.timezone.utc
_TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)?")


def utc_now() -> dt.datetime:
    return dt.datetime.now(UTC)


def timestamp(value: Optional[dt.datetime] = None) -> str:
    """Serialize an instant in the format used by JavaScript's toISOString()."""
    instant = value if value is not None else utc_now()
    return instant.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def parse_timestamp(value: object) -> Optional[dt.datetime]:
    """Return an aware UTC instant, or None for unsupported/invalid values.

    Replacing Z explicitly keeps this compatible with Python 3.9. astimezone()
    treats a naive datetime as local time, including its date's DST offset. Local
    times skipped by a DST change are invalid; repeated times use the first one.
    """
    if not isinstance(value, str) or not _TIMESTAMP.fullmatch(value):
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        instant = parsed.astimezone(UTC)
        if parsed.tzinfo is None and instant.astimezone().replace(tzinfo=None) != parsed:
            return None
        return instant
    except (ValueError, OverflowError, OSError):
        return None


def local_day(value: Optional[dt.datetime] = None) -> str:
    instant = value if value is not None else utc_now()
    return instant.astimezone().date().isoformat()


def timestamp_day(value: object) -> Optional[str]:
    instant = parse_timestamp(value)
    try:
        return local_day(instant) if instant is not None else None
    except (ValueError, OverflowError, OSError):
        # A valid UTC boundary date may lie outside the local calendar's range.
        return None


def elapsed_seconds(opened: object, now: Optional[dt.datetime] = None) -> Optional[float]:
    start = parse_timestamp(opened)
    if start is None:
        return None
    current = now if now is not None else utc_now()
    seconds = (current.astimezone(UTC) - start).total_seconds()
    return seconds if seconds >= 0 else None
