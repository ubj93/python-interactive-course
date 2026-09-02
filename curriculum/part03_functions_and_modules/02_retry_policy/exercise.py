"""Build a retry policy from keyword overrides.

Every HTTP helper in our tooling takes a retry policy: a dict describing how
many times to try and how long to wait. Write `retry_policy(**overrides)`
that starts from these defaults and applies whatever the caller overrides:

    max_attempts: 3
    base_delay:   1.0     seconds before the first retry
    max_delay:    30.0    cap on any single wait
    backoff:      2.0     multiplier applied to the delay after each attempt
    retry_on:     (429, 500, 502, 503, 504)   HTTP statuses worth retrying

Rules:
- an override whose name is not one of the five keys raises TypeError, with
  the unknown name in the message (this is what Python itself does when you
  pass an unexpected keyword to a normal function)
- max_attempts must be an int of at least 1, else ValueError
- base_delay and max_delay must be >= 0, and max_delay >= base_delay, else ValueError
- backoff must be >= 1, else ValueError
- retry_on may be given as any iterable of ints (list, set, tuple, range);
  it is stored as a tuple, sorted ascending, without duplicates
- the returned dict has exactly the five keys, and it is a NEW dict on every
  call: modifying one result must not change the defaults or the next result

Examples:
    >>> retry_policy()
    {'max_attempts': 3, 'base_delay': 1.0, 'max_delay': 30.0, 'backoff': 2.0, 'retry_on': (429, 500, 502, 503, 504)}
    >>> retry_policy(max_attempts=5, retry_on=[503, 429, 503])
    {'max_attempts': 5, 'base_delay': 1.0, 'max_delay': 30.0, 'backoff': 2.0, 'retry_on': (429, 503)}
    >>> retry_policy(max_attemps=5)
    Traceback (most recent call last):
    ...
    TypeError: unexpected keyword argument 'max_attemps'
"""
from typing import Any, Dict

DEFAULTS: Dict[str, Any] = {
    "max_attempts": 3,
    "base_delay": 1.0,
    "max_delay": 30.0,
    "backoff": 2.0,
    "retry_on": (429, 500, 502, 503, 504),
}


def retry_policy(**overrides: Any) -> Dict[str, Any]:
    raise NotImplementedError("write retry_policy")
