"""Reference solutions for two_sum."""
from typing import Dict, List, Optional, Tuple


# Best practice: one pass with a dict of value -> first index. Check for the partner
# *before* storing the current value so an element can never pair with itself.
# Time O(n), space O(n).
def two_sum(sizes: List[int], target: int) -> Optional[Tuple[int, int]]:
    seen: Dict[int, int] = {}
    for j, size in enumerate(sizes):
        need = target - size
        if need in seen:
            return (seen[need], j)
        seen.setdefault(size, j)
    return None


# Brute force, for comparison: every pair. Time O(n^2), space O(1).
# Correct, and the right thing to say first in an interview, but the large test
# takes seconds with it.
def two_sum_brute(sizes: List[int], target: int) -> Optional[Tuple[int, int]]:
    n = len(sizes)
    for i in range(n):
        for j in range(i + 1, n):
            if sizes[i] + sizes[j] == target:
                return (i, j)
    return None
