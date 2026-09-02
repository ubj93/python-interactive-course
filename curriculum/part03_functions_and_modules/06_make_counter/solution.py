"""Reference solutions for make_counter and make_checkin_tracker."""
from typing import Callable, Dict


# Best practice: the closure keeps `current` alive after make_counter returns. `nonlocal`
# is required because `current += step` *rebinds* the name; without it Python would
# treat current as a new local and raise UnboundLocalError.
def make_counter(start: int = 0, step: int = 1) -> Callable[[], int]:
    current = start

    def next_value() -> int:
        nonlocal current
        value = current
        current += step
        return value

    return next_value


# Best practice: no nonlocal here because the inner function only *mutates* the dict;
# it never assigns to the name `counts`. That distinction is the lesson of the exercise.
def make_checkin_tracker() -> Callable[[str], int]:
    counts: Dict[str, int] = {}

    def record(hostname: str) -> int:
        key = hostname.strip().lower()
        counts[key] = counts.get(key, 0) + 1
        return counts[key]

    return record


# Clever: itertools.count is a ready-made infinite counter; the closure just calls next()
# on it. Shows that closures can capture any object, not only plain numbers. No nonlocal
# needed because `it` is never rebound.
def make_counter_itertools(start: int = 0, step: int = 1) -> Callable[[], int]:
    from itertools import count

    it = count(start, step)

    def next_value() -> int:
        return next(it)

    return next_value
