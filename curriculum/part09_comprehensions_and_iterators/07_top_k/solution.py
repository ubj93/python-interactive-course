"""Reference solutions for top_k."""
import heapq
from typing import Any, Callable, Iterable, List, TypeVar

T = TypeVar("T")


# Best practice: heapq.nlargest keeps a heap of at most k items while streaming through the
# input once: O(n log k) time, O(k) memory, and it accepts any iterable. It also keeps ties
# in input order, matching sorted(..., reverse=True)[:k]. It returns [] for k <= 0 itself.
# Prefer it when k is small relative to n or when the input does not fit in memory.
def top_k(items: Iterable[T], k: int, key: Callable[[T], Any]) -> List[T]:
    if k <= 0:
        return []
    return heapq.nlargest(k, items, key=key)


# Clever (the "simple" answer): a full sort. O(n log n) and it materialises the whole input,
# but it is one obvious line and, when k is close to n, it is no slower in practice.
# Say this trade-off out loud in an interview; both answers are correct, the reasoning is
# what is being graded.
def top_k_sorted(items: Iterable[T], k: int, key: Callable[[T], Any]) -> List[T]:
    if k <= 0:
        return []
    return sorted(items, key=key, reverse=True)[:k]
