"""Reference solutions for bisect_first_bad."""
from typing import Callable, Optional


# Best practice: keep the invariant "the first bad build, if any, is in [lo, hi]".
# A bad mid stays in range (hi = mid); a good mid is excluded (lo = mid + 1). The
# loop uses ceil(log2 n) calls and one final call confirms that lo is really bad.
# Time O(log n) predicate calls, space O(1).
def bisect_first_bad(n_builds: int, is_bad: Callable[[int], bool]) -> Optional[int]:
    if n_builds <= 0:
        return None
    lo, hi = 1, n_builds
    while lo < hi:
        mid = (lo + hi) // 2
        if is_bad(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo if is_bad(lo) else None


# Alternative: the half-open form "[lo, hi) may contain the answer, hi is known bad or
# one past the end". Equivalent call count; some people find the exit condition clearer
# because hi == n_builds + 1 at the end means "no bad build".
def bisect_first_bad_half_open(n_builds: int, is_bad: Callable[[int], bool]) -> Optional[int]:
    lo, hi = 1, n_builds + 1
    while lo < hi:
        mid = (lo + hi) // 2
        if is_bad(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo if lo <= n_builds else None
