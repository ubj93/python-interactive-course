"""Reference solutions for most_common_with_ties."""
import heapq
from collections import Counter
from typing import Iterable, List, Tuple


# Best practice: Counter does the counting, one sorted() with a composite key does the
# ordering (negate the count to get descending while the name stays ascending). The tie
# extension is a while loop that walks past n as long as the count matches.
def most_common_with_ties(items: Iterable[str], n: int, include_ties: bool = False) -> List[Tuple[str, int]]:
    if n <= 0:
        return []
    ranked = sorted(Counter(items).items(), key=lambda kv: (-kv[1], kv[0]))
    if not ranked:
        return []
    if not include_ties or n >= len(ranked):
        return ranked[:n]
    cutoff = ranked[n - 1][1]
    end = n
    while end < len(ranked) and ranked[end][1] == cutoff:
        end += 1
    return ranked[:end]


# Clever: heapq.nsmallest with the same key is O(N log n) instead of O(N log N) when n is
# small and there are many distinct items. It cannot do include_ties on its own, so fall
# back to the full sort in that case.
def most_common_with_ties_heap(items: Iterable[str], n: int, include_ties: bool = False) -> List[Tuple[str, int]]:
    if n <= 0:
        return []
    counts = Counter(items)
    if include_ties:
        return most_common_with_ties(counts.elements(), n, include_ties=True)
    return heapq.nsmallest(n, counts.items(), key=lambda kv: (-kv[1], kv[0]))
