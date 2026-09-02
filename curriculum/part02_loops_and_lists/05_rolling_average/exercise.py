"""Smooth CPU samples with a rolling average.

A monitoring agent samples CPU usage every minute and the raw numbers are too
spiky to alert on. Write `rolling_average(samples, n)` that returns a list of
the same length as `samples`, where element i is the mean of the last `n`
samples ending at i (samples[i-n+1] .. samples[i]).

At the start there are fewer than n samples available: average whatever is
there. The first output is therefore always samples[0], the second is the
mean of the first two, and so on until the window is full.

Rules:
- every output value is a float rounded to 2 decimal places
- the output has exactly len(samples) elements; empty input gives []
- n must be at least 1; otherwise raise ValueError
- n larger than the list is fine: every window is just "everything so far"
- do not modify the input

Examples:
    >>> rolling_average([10, 20, 30, 40], 2)
    [10.0, 15.0, 25.0, 35.0]
    >>> rolling_average([3, 6, 9], 3)
    [3.0, 4.5, 6.0]
    >>> rolling_average([], 3)
    []
"""
from typing import List


def rolling_average(samples: List[float], n: int) -> List[float]:
    raise NotImplementedError("write rolling_average")
