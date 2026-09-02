"""Split serials into batches.

The vendor's warranty API accepts at most N serial numbers per request, so a
long list must be sent in batches. Write `chunk_serials(serials, size)` that
returns a list of lists: consecutive slices of `serials`, each holding `size`
items, in the original order.

Rules:
- the last batch holds whatever is left and may be shorter than `size`
- when the length divides evenly there is no empty trailing batch
- an empty input gives an empty list of batches
- `size` must be at least 1; otherwise raise ValueError
- return new lists; do not modify the input

Examples:
    >>> chunk_serials(["A", "B", "C", "D", "E"], 2)
    [['A', 'B'], ['C', 'D'], ['E']]
    >>> chunk_serials(["A", "B", "C", "D"], 2)
    [['A', 'B'], ['C', 'D']]
    >>> chunk_serials([], 3)
    []
"""
from typing import List


def chunk_serials(serials: List[str], size: int) -> List[List[str]]:
    raise NotImplementedError("write chunk_serials")
