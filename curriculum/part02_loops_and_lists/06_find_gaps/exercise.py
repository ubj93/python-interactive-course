"""Find unused asset tag ranges.

Asset tags are handed out as consecutive integers, but some were retired and
some were never used. Given a list of the tags currently in use, sorted in
ascending order, write `find_gaps(tags)` that returns the missing ranges
between the smallest and the largest tag as a list of (start, end) tuples,
both inclusive, in ascending order.

Rules:
- a gap of one number is (n, n)
- the input may contain duplicate tags; they are not gaps
- an empty list, or a list with a single distinct tag, has no gaps: return []
- tags below the smallest or above the largest are unknowable: ignore them
- if the list is not sorted ascending, raise ValueError
- do not modify the input

Examples:
    >>> find_gaps([100, 101, 102, 105, 106, 110])
    [(103, 104), (107, 109)]
    >>> find_gaps([1, 2, 3])
    []
    >>> find_gaps([7, 7, 9])
    [(8, 8)]
"""
from typing import List, Tuple


def find_gaps(tags: List[int]) -> List[Tuple[int, int]]:
    raise NotImplementedError("write find_gaps")
