"""Reference solutions for word_frequency_top_k."""
import heapq
import re
from collections import Counter
from typing import List, Tuple

WORD = re.compile(r"\w+")


# Best practice: Counter for the counting, then a heap over (-count, word) so the
# "smallest" k entries are the biggest counts with alphabetical ties.
# Time O(n + d log k) for n words and d distinct words, space O(d).
def word_frequency_top_k(text: str, k: int) -> List[Tuple[str, int]]:
    if k <= 0:
        return []
    counts = Counter(WORD.findall(text.lower()))
    return heapq.nsmallest(k, counts.items(), key=lambda kv: (-kv[1], kv[0]))


# Alternative: a full sort with the same key. O(d log d) instead of O(d log k), which
# only matters when d is huge and k is tiny, but it is one line and easy to defend.
def word_frequency_top_k_sorted(text: str, k: int) -> List[Tuple[str, int]]:
    if k <= 0:
        return []
    counts = Counter(WORD.findall(text.lower()))
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:k]
