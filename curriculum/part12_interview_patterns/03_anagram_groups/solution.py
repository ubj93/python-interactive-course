"""Reference solutions for anagram_groups."""
from collections import Counter
from typing import Dict, List, Tuple


# Best practice: a canonical key (the sorted characters) and a dict that remembers
# insertion order, so the groups come out in first-appearance order for free.
# Time O(n * k log k) for n names of length k, space O(n * k).
def anagram_groups(names: List[str]) -> List[List[str]]:
    groups: Dict[str, List[str]] = {}
    for name in names:
        groups.setdefault("".join(sorted(name)), []).append(name)
    return list(groups.values())


# Alternative: a character-count key avoids the sort, giving O(n * k). The key must be
# hashable, so the Counter is frozen into a sorted tuple of (char, count) pairs.
def anagram_groups_counts(names: List[str]) -> List[List[str]]:
    groups: Dict[Tuple[Tuple[str, int], ...], List[str]] = {}
    for name in names:
        key = tuple(sorted(Counter(name).items()))
        groups.setdefault(key, []).append(name)
    return list(groups.values())
