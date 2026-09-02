"""Reference solutions for parse_rate_limit / wait_seconds."""
from collections import namedtuple
from typing import Mapping, Optional

RateLimit = namedtuple("RateLimit", ["remaining", "reset_in"])


# Two tiny helpers keep the main function readable: one for case-insensitive lookup, one
# for "number or None". Parsing headers is all edge cases, so isolate them.
def _header(headers: Mapping[str, str], name: str) -> Optional[str]:
    want = name.lower()
    for key, value in headers.items():
        if key.lower() == want:
            return value
    return None


def _number(text: Optional[str]) -> Optional[float]:
    if text is None:
        return None
    try:
        return float(text.strip())
    except ValueError:
        return None


# Best practice: compute each field independently, Retry-After first because it is the
# server's explicit instruction; clamp with max() so a stale reset never yields a
# negative sleep.
def parse_rate_limit(headers: Mapping[str, str], now: float) -> RateLimit:
    remaining_raw = _number(_header(headers, "X-RateLimit-Remaining"))
    remaining = int(remaining_raw) if remaining_raw is not None else None

    retry_after = _number(_header(headers, "Retry-After"))
    if retry_after is not None:
        reset_in: Optional[float] = float(retry_after)
    else:
        reset_at = _number(_header(headers, "X-RateLimit-Reset"))
        reset_in = max(0.0, reset_at - now) if reset_at is not None else None
    return RateLimit(remaining, reset_in)


def wait_seconds(headers: Mapping[str, str], now: float) -> float:
    rl = parse_rate_limit(headers, now)
    told_to_wait = _number(_header(headers, "Retry-After")) is not None
    if told_to_wait or (rl.remaining is not None and rl.remaining <= 0):
        return rl.reset_in or 0.0
    return 0.0


# Clever: normalise the whole mapping to lowercase keys once, then plain dict.get does the
# lookups. Costs one pass over the headers, saves a helper.
def parse_rate_limit_lowered(headers: Mapping[str, str], now: float) -> RateLimit:
    h = {k.lower(): v for k, v in headers.items()}
    remaining_raw = _number(h.get("x-ratelimit-remaining"))
    remaining = int(remaining_raw) if remaining_raw is not None else None
    retry_after = _number(h.get("retry-after"))
    if retry_after is not None:
        return RateLimit(remaining, float(retry_after))
    reset_at = _number(h.get("x-ratelimit-reset"))
    return RateLimit(remaining, max(0.0, reset_at - now) if reset_at is not None else None)
