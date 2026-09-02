"""Reference solutions for most_common_apps."""
from typing import Dict, List, Tuple


# Best practice: set(apps) dedupes per device, the counting idiom builds the totals,
# and one sort with a two-part key (-count, name) does "descending count, ascending name".
def most_common_apps(installs: Dict[str, List[str]], k: int) -> List[Tuple[str, int]]:
    if k <= 0:
        return []
    counts: Dict[str, int] = {}
    for apps in installs.values():
        for app in set(apps):
            counts[app] = counts.get(app, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return ranked[:k]


# Clever: Counter does the counting and heapq.nsmallest does a partial sort, which is
# cheaper than a full sort when k is much smaller than the number of apps.
def most_common_apps_heap(installs: Dict[str, List[str]], k: int) -> List[Tuple[str, int]]:
    import heapq
    from collections import Counter

    if k <= 0:
        return []
    counts = Counter(app for apps in installs.values() for app in set(apps))
    return heapq.nsmallest(k, counts.items(), key=lambda item: (-item[1], item[0]))
