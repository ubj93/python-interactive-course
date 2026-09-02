"""Reference solutions for apply_pipeline."""
from typing import Any, Callable, List, Optional


# Best practice: validate the whole list first, then a plain loop that rebinds `value`.
# `is None` (not `not value`) is the whole point of the falsy rule; checking it at the
# top of each iteration also covers a None starting value without a separate branch.
def apply_pipeline(value: Any, steps: List[Callable[[Any], Any]]) -> Optional[Any]:
    for step in steps:
        if not callable(step):
            raise TypeError(f"pipeline steps must be callable, got {step!r}")
    for step in steps:
        if value is None:
            return None
        value = step(value)
    return value


# Clever: check the result right after each call and return early. Same behaviour, and
# some readers prefer seeing the stop condition next to the call that produced it. The
# up-front None guard is now explicit, which makes that rule easier to spot in review.
def apply_pipeline_early_return(value: Any, steps: List[Callable[[Any], Any]]) -> Optional[Any]:
    bad = [s for s in steps if not callable(s)]
    if bad:
        raise TypeError(f"pipeline steps must be callable, got {bad[0]!r}")
    if value is None:
        return None
    for step in steps:
        value = step(value)
        if value is None:
            return None
    return value
