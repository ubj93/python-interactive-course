"""Merge maintenance windows.

Three teams file maintenance windows for the same fleet as (start, end)
pairs of minutes since midnight. The change board wants the combined
blackout periods. Write `merge_intervals(windows)` that returns the merged
list.

Rules:
- each window is a tuple (start, end) of ints with start <= end
- windows may arrive in any order; the result is sorted by start
- two windows merge when they overlap *or touch*: (60, 120) and (120, 180)
  become (60, 180)
- a window fully inside another disappears into it: (0, 100) and (10, 20)
  become (0, 100)
- a zero-length window (start == end) is allowed; it merges into a
  neighbour it touches, otherwise it stands alone
- a window with start > end raises ValueError
- return a new list of tuples and do not modify the input list
- an empty list gives an empty list

Complexity target: O(n log n) time for the sort, then one O(n) sweep; O(n)
extra space for the result. The last test has 10,000 windows.

Examples:
    >>> merge_intervals([(540, 600), (720, 780), (590, 660)])
    [(540, 660), (720, 780)]
    >>> merge_intervals([(60, 120), (120, 180)])
    [(60, 180)]
"""
from typing import List, Tuple


def merge_intervals(windows: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    raise NotImplementedError("write merge_intervals")
