"""Two packages that exactly fill a disk budget.

A deployment tool caches installer packages on a small staging volume. Before
a rollout it wants to pick two cached packages whose sizes together fill a
given number of megabytes exactly. Write `two_sum(sizes, target)` that takes
a list of package sizes (ints) and a target, and returns a tuple `(i, j)` of
two different indexes with `i < j` and `sizes[i] + sizes[j] == target`.
Return None when no such pair exists.

Rules:
- an index may not be paired with itself; two equal values at different
  indexes are a valid pair
- when more than one pair is valid, any valid pair is accepted
- sizes may include 0 and negative numbers (credits); treat them like any
  other value
- an empty list or a single element gives None
- return a tuple, not a list

Complexity target: O(n) time and O(n) extra space, in a single pass. The
last test has 20,000 sizes and its only valid pair is far apart: a nested
loop over all pairs takes a few seconds, a dictionary of "sizes seen so
far" finishes in milliseconds.

Examples:
    >>> two_sum([120, 40, 75, 60], 100)
    (1, 3)
    >>> two_sum([4, 4], 8)
    (0, 1)
    >>> two_sum([5, 3], 10)
    None
"""
from typing import List, Optional, Tuple


def two_sum(sizes: List[int], target: int) -> Optional[Tuple[int, int]]:
    raise NotImplementedError("write two_sum")
