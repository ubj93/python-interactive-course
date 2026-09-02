"""Run a value through a pipeline of steps.

Device records go through a series of clean-up and validation steps before
they are written to the inventory. Each step is a function that takes the
current value and returns the next one, or returns None to say "drop this
record." Write `apply_pipeline(value, steps)` that applies the steps in
order and returns the final value.

Rules:
- steps are applied left to right: the output of one is the input of the next
- if any step returns None, stop immediately and return None; the remaining
  steps must NOT be called
- only None stops the pipeline: falsy values such as 0, "" and [] are passed
  on to the next step like any other value
- if the starting value is None, return None without calling any step
- an empty list of steps returns the value unchanged
- every step must be callable; otherwise raise TypeError BEFORE running any
  step (a half-run pipeline is worse than none)

Examples:
    >>> apply_pipeline("  MBP-J-DOE ", [str.strip, str.lower])
    'mbp-j-doe'
    >>> reject_lab = lambda h: None if h.startswith("lab-") else h
    >>> apply_pipeline("lab-01", [str.lower, reject_lab, str.upper])
    >>> apply_pipeline(0, [lambda n: n + 1, lambda n: n * 2])
    2
"""
from typing import Any, Callable, List, Optional


def apply_pipeline(value: Any, steps: List[Callable[[Any], Any]]) -> Optional[Any]:
    raise NotImplementedError("write apply_pipeline")
