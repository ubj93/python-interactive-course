"""Functions with private state.

Two small factories, both built on closures. Neither may use a global
variable or a class; the state lives inside the enclosing function's scope
and is reachable only through the function you return.

1. `make_counter(start=0, step=1)` returns a function that takes no
   arguments. The first call returns `start`; each later call returns the
   previous value plus `step`. Use it to hand out ticket or batch numbers.

2. `make_checkin_tracker()` returns a function `record(hostname)` that
   returns how many times that hostname has checked in so far, INCLUDING
   the current call. Hostnames are compared case-insensitively with
   surrounding whitespace ignored, so "MBP-J-DOE" and " mbp-j-doe " are the
   same machine.

Rules:
- every call to a factory creates independent state: two counters, or two
  trackers, never affect each other
- step may be negative or zero
- the tracker must not modify or normalise anything except for comparison;
  it only needs to return the count

Hint on mechanics: rebinding a number from the inner function needs
`nonlocal`; mutating a dict held by the outer function does not.

Examples:
    >>> next_ticket = make_counter(100)
    >>> next_ticket(), next_ticket(), next_ticket()
    (100, 101, 102)
    >>> record = make_checkin_tracker()
    >>> record("mbp-j-doe"), record("nuc-01"), record(" MBP-J-DOE ")
    (1, 1, 2)
"""
from typing import Callable


def make_counter(start: int = 0, step: int = 1) -> Callable[[], int]:
    raise NotImplementedError("write make_counter")


def make_checkin_tracker() -> Callable[[str], int]:
    raise NotImplementedError("write make_checkin_tracker")
