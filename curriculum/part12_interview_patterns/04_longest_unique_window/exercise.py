"""Longest run of check-ins from distinct hosts.

An MDM check-in log is a sequence of host identifiers in the order they
phoned home. We want to know the longest stretch of consecutive entries in
which no host appears twice: it tells us how many machines were active in the
busiest window. Write `longest_unique_window(hosts)` that returns the length
of the longest contiguous run with no repeated element.

Rules:
- `hosts` is any sequence of hashable items (a list of strings, a string of
  characters, a list of ints)
- return an int; an empty sequence gives 0
- a single element gives 1
- a repeat that is already *outside* the current window must not shrink it
  (the classic bug: "abbac" is 3, not 4)

Complexity target: O(n) time, O(d) extra space where d is the number of
distinct hosts, using a sliding window and a dict of last-seen positions.
The last test has 20,500 entries where the answer is 2,500: restarting the
scan from every position takes seconds, one pass takes milliseconds.

Examples:
    >>> longest_unique_window(["mbp-1", "mbp-2", "mbp-1", "mbp-3"])
    3
    >>> longest_unique_window("abcabcbb")
    3
    >>> longest_unique_window([])
    0
"""
from typing import Hashable, Sequence


def longest_unique_window(hosts: Sequence[Hashable]) -> int:
    raise NotImplementedError("write longest_unique_window")
