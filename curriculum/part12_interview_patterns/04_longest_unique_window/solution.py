"""Reference solutions for longest_unique_window."""
from typing import Dict, Hashable, Sequence


# Best practice: sliding window with a dict of last-seen index. `start` only ever
# moves forward, and only when the repeat is inside the current window.
# Time O(n), space O(d) for d distinct items.
def longest_unique_window(hosts: Sequence[Hashable]) -> int:
    last_seen: Dict[Hashable, int] = {}
    start = best = 0
    for i, host in enumerate(hosts):
        if host in last_seen and last_seen[host] >= start:
            start = last_seen[host] + 1
        last_seen[host] = i
        best = max(best, i - start + 1)
    return best


# Brute force, for comparison: from every start position extend until a repeat.
# Time O(n * w) where w is the longest window, so O(n^2) when items rarely repeat;
# this is what makes the large test take seconds.
def longest_unique_window_brute(hosts: Sequence[Hashable]) -> int:
    best = 0
    n = len(hosts)
    for start in range(n):
        seen = set()
        end = start
        while end < n and hosts[end] not in seen:
            seen.add(hosts[end])
            end += 1
        best = max(best, end - start)
    return best
