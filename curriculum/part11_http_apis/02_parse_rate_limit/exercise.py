"""Read rate-limit headers.

APIs tell you how close you are to being throttled through response headers:

    X-RateLimit-Remaining: 12          requests left in the current window
    X-RateLimit-Reset: 1714813260      unix time (seconds) when the window resets
    Retry-After: 30                    seconds to wait (sent with a 429)

Write `parse_rate_limit(headers, now)` returning a `RateLimit` (a namedtuple
defined below with fields `remaining` and `reset_in`), and
`wait_seconds(headers, now)`.

`parse_rate_limit` rules:
- header names are matched case-insensitively ("x-ratelimit-remaining" works);
  values are strings and may have surrounding whitespace
- `remaining`: int from X-RateLimit-Remaining; None when missing or not an integer
- `reset_in`: float seconds until the window resets:
  - Retry-After, when present and numeric, wins: reset_in is that number
  - otherwise X-RateLimit-Reset minus `now` (both unix seconds), clamped to 0.0
    when the reset time is already in the past
  - None when neither header is usable
- `now` is injected (a float unix timestamp); never call time.time() yourself

`wait_seconds` returns how long to sleep before the next request:
- reset_in when Retry-After was sent, or when remaining is 0 (or below)
- 0.0 in every other case, including when reset_in is None

Examples:
    >>> parse_rate_limit({"X-RateLimit-Remaining": "12", "X-RateLimit-Reset": "1000"}, now=940.0)
    RateLimit(remaining=12, reset_in=60.0)
    >>> wait_seconds({"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1000"}, now=940.0)
    60.0
    >>> wait_seconds({"X-RateLimit-Remaining": "5", "X-RateLimit-Reset": "1000"}, now=940.0)
    0.0
"""
from collections import namedtuple
from typing import Mapping, Optional

RateLimit = namedtuple("RateLimit", ["remaining", "reset_in"])


def parse_rate_limit(headers: Mapping[str, str], now: float) -> RateLimit:
    raise NotImplementedError("write parse_rate_limit")


def wait_seconds(headers: Mapping[str, str], now: float) -> float:
    raise NotImplementedError("write wait_seconds")
