"""Reference solutions for merge_intervals."""
from typing import List, Tuple


# Best practice: validate, sort by start, then sweep once carrying the last merged
# window. max() on the end handles a window nested inside the previous one.
# Time O(n log n), space O(n) for the sorted copy and the result.
def merge_intervals(windows: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    for start, end in windows:
        if start > end:
            raise ValueError(f"window start {start} is after its end {end}")
    merged: List[Tuple[int, int]] = []
    for start, end in sorted(windows):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


# Alternative: track the current window in two variables and only append when a gap
# appears. Same complexity; some people find the "flush on gap" shape easier to read.
def merge_intervals_flush(windows: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    if any(s > e for s, e in windows):
        raise ValueError("a window has start > end")
    ordered = sorted(windows)
    if not ordered:
        return []
    merged: List[Tuple[int, int]] = []
    cur_start, cur_end = ordered[0]
    for start, end in ordered[1:]:
        if start <= cur_end:
            cur_end = max(cur_end, end)
        else:
            merged.append((cur_start, cur_end))
            cur_start, cur_end = start, end
    merged.append((cur_start, cur_end))
    return merged
