"""Days since a device last checked in.

MDM APIs hand back timestamps as ISO 8601 strings, and they are not consistent:
one vendor sends "2024-05-01T10:00:00Z", another "2024-05-01T10:00:00+00:00",
and an internal tool sends a naive "2024-05-01 10:00:00" that everyone agrees is
UTC. Write two functions.

`parse_timestamp(raw)` returns a timezone-aware `datetime` in UTC:

- accepts a trailing "Z" (Python 3.9's `datetime.fromisoformat` does not, so
  replace it with "+00:00" before parsing),
- accepts an explicit offset such as "+02:00" and converts the instant to UTC,
- treats a naive timestamp (no offset at all) as already being UTC,
- tolerates surrounding whitespace,
- raises ValueError for None, an empty string, or anything it cannot parse.

`days_since(raw, now)` returns the number of whole days between the parsed
timestamp and `now`. `now` is injected by the caller (tests pass a fixed aware
datetime so the result is deterministic; never call datetime.now() yourself).

Rules:
- round down: 2 days and 23 hours is 2
- a timestamp in the future returns 0
- a naive `now` is treated as UTC, the same as a naive timestamp
- bad timestamps raise ValueError (parse_timestamp does that for you)

Examples:
    >>> parse_timestamp("2024-05-01T12:00:00+02:00")
    datetime.datetime(2024, 5, 1, 10, 0, tzinfo=datetime.timezone.utc)
    >>> now = datetime(2024, 5, 4, 9, 0, tzinfo=timezone.utc)
    >>> days_since("2024-05-01T10:00:00Z", now)
    2
"""
from datetime import datetime, timezone
from typing import Optional


def parse_timestamp(raw: Optional[str]) -> datetime:
    raise NotImplementedError("write parse_timestamp")


def days_since(raw: Optional[str], now: datetime) -> int:
    raise NotImplementedError("write days_since")
