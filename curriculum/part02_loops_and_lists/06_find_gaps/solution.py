"""Reference solutions for find_gaps."""
from typing import List, Tuple


# Best practice: zip(tags, tags[1:]) walks neighbouring pairs, which cannot run off the
# end the way tags[i + 1] can. A descending pair is the sort check; a pair with room
# between the two is a gap; equal pairs (duplicates) fall through both tests.
def find_gaps(tags: List[int]) -> List[Tuple[int, int]]:
    gaps = []
    for prev, cur in zip(tags, tags[1:]):
        if cur < prev:
            raise ValueError("tags must be sorted ascending")
        if cur - prev > 1:
            gaps.append((prev + 1, cur - 1))
    return gaps


# Clever: the same walk with an explicit `prev` variable, no slicing copy. Same
# complexity; this shape also works on an iterator you cannot slice (a file, a query).
def find_gaps_prev(tags: List[int]) -> List[Tuple[int, int]]:
    gaps = []
    prev = None
    for tag in tags:
        if prev is not None:
            if tag < prev:
                raise ValueError("tags must be sorted ascending")
            if tag - prev > 1:
                gaps.append((prev + 1, tag - 1))
        prev = tag
    return gaps
