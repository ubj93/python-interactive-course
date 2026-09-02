"""Reference solutions for TokenBucket."""
from typing import Callable


# Best practice: one private _refill() that every public method calls first, so the
# "how many tokens do I have right now" question is answered in exactly one place.
# The clock is injected and stored; nothing here imports time. max(0.0, ...) guards
# against a clock that steps backwards (NTP adjustments do that on real machines).
class TokenBucket:
    def __init__(self, capacity: int, refill_per_second: float, now: Callable[[], float]) -> None:
        if capacity < 1:
            raise ValueError(f"capacity must be >= 1, got {capacity}")
        if refill_per_second <= 0:
            raise ValueError(f"refill_per_second must be > 0, got {refill_per_second}")
        self.capacity = capacity
        self.rate = float(refill_per_second)
        self._now = now
        self._tokens = float(capacity)
        self._last = now()

    def _refill(self) -> None:
        t = self._now()
        elapsed = max(0.0, t - self._last)
        self._tokens = min(float(self.capacity), self._tokens + elapsed * self.rate)
        self._last = t

    def _check_cost(self, cost: int) -> None:
        if cost > self.capacity:
            raise ValueError(f"cost {cost} exceeds capacity {self.capacity}")

    def allow(self, cost: int = 1) -> bool:
        self._check_cost(cost)
        self._refill()
        if self._tokens >= cost:
            self._tokens -= cost
            return True
        return False

    @property
    def available(self) -> float:
        self._refill()
        return self._tokens

    def seconds_until(self, cost: int = 1) -> float:
        self._check_cost(cost)
        self._refill()
        if self._tokens >= cost:
            return 0.0
        return (cost - self._tokens) / self.rate
