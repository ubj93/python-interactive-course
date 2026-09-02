"""A token-bucket rate limiter with an injected clock.

The MDM API allows a burst of N calls and then a steady rate. A token bucket
models that: the bucket holds up to `capacity` tokens, every call spends
tokens, and tokens trickle back in at `refill_per_second`. To keep the tests
deterministic the bucket never reads the wall clock: it calls the `now`
function it was given, which returns seconds as a float.

`TokenBucket(capacity, refill_per_second, now)`:
- `capacity` must be an int >= 1 and `refill_per_second` a number > 0;
  otherwise raise ValueError.
- The bucket starts full, and records `now()` as the last refill time.

Refill rule (apply it at the start of every public call):
    elapsed = now() - last_refill_time   (treat a negative elapsed as 0)
    tokens  = min(capacity, tokens + elapsed * refill_per_second)
    last_refill_time = that now() value

Methods:
- `allow(cost=1)`: refill, then if at least `cost` tokens are available
  subtract them and return True; otherwise return False and spend nothing.
  A `cost` greater than `capacity` can never succeed: raise ValueError.
- `available` (property): refill, then return the current token count as a
  float.
- `seconds_until(cost=1)`: refill, then return 0.0 when `cost` tokens are
  already available, otherwise the seconds until they will be:
  (cost - tokens) / refill_per_second. Raise ValueError when cost > capacity.

Examples (with a fake clock `clock` whose `.t` attribute the test sets):
    >>> clock = FakeClock()             # clock() returns clock.t, starting at 0.0
    >>> bucket = TokenBucket(capacity=3, refill_per_second=1.0, now=clock)
    >>> bucket.allow(), bucket.allow(), bucket.allow(), bucket.allow()
    (True, True, True, False)
    >>> bucket.seconds_until()
    1.0
    >>> clock.t = 2.0
    >>> bucket.available
    2.0
    >>> bucket.allow(cost=2), bucket.allow()
    (True, False)
"""
from typing import Callable


class TokenBucket:
    def __init__(self, capacity: int, refill_per_second: float, now: Callable[[], float]) -> None:
        raise NotImplementedError("write TokenBucket.__init__")

    def allow(self, cost: int = 1) -> bool:
        raise NotImplementedError("write TokenBucket.allow")

    @property
    def available(self) -> float:
        raise NotImplementedError("write TokenBucket.available")

    def seconds_until(self, cost: int = 1) -> float:
        raise NotImplementedError("write TokenBucket.seconds_until")
