"""Reference solutions for parse_timestamp / days_since."""
from datetime import datetime, timezone
from typing import Optional


# Best practice: normalise the string (Z -> +00:00), let fromisoformat do the parsing and
# raise on garbage, then make the result aware. astimezone(utc) converts offsets to UTC
# and is a no-op for something already in UTC.
def parse_timestamp(raw: Optional[str]) -> datetime:
    if raw is None or not raw.strip():
        raise ValueError("empty timestamp")
    s = raw.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


# Subtracting two aware datetimes gives a timedelta; .days already floors toward -inf,
# and max(0, ...) clamps the future case.
def days_since(raw: Optional[str], now: datetime) -> int:
    then = parse_timestamp(raw)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return max(0, (now - then).days)


# Clever: strptime's %z accepts "Z" and "+02:00" since 3.7, so a format list covers all
# the shapes without string surgery. Slower and stricter (no fractional seconds), but it
# is what you will see in code bases older than fromisoformat.
FORMATS = ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]


def parse_timestamp_strptime(raw: Optional[str]) -> datetime:
    if raw is None or not raw.strip():
        raise ValueError("empty timestamp")
    s = raw.strip()
    for fmt in FORMATS:
        try:
            dt = datetime.strptime(s, fmt)
        except ValueError:
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    raise ValueError(f"unrecognised timestamp: {raw!r}")
