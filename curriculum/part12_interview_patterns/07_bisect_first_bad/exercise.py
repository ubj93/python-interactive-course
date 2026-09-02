"""Bisect the first bad build.

Nightly builds of the agent are numbered 1..n_builds. At some point a change
broke enrollment, and every build from that one onwards is bad. Testing a
build means installing it on a lab machine, which takes ten minutes, so we
must test as few builds as possible. Write `bisect_first_bad(n_builds,
is_bad)` that returns the number of the first bad build, or None when no
build is bad.

`is_bad(build)` is an injected predicate that returns True when the build is
broken. It is monotone: once a build is bad, every later build is bad too.

Rules:
- builds are numbered from 1 to n_builds inclusive
- never call `is_bad` with a number outside 1..n_builds (the tests raise)
- n_builds == 0 gives None without calling the predicate
- when every build is bad return 1; when none is bad return None
- do not cache or precompute; the tests count real calls

Complexity target: O(log n) predicate calls, and specifically at most
ceil(log2(n_builds)) + 1 calls for n_builds >= 1. For 1,000 builds that is
11 calls; for a billion it is 31. A linear scan fails the call budget.

Examples:
    >>> bisect_first_bad(5, lambda b: b >= 4)
    4
    >>> bisect_first_bad(5, lambda b: False)
    None
    >>> bisect_first_bad(5, lambda b: True)
    1
"""
from typing import Callable, Optional


def bisect_first_bad(n_builds: int, is_bad: Callable[[int], bool]) -> Optional[int]:
    raise NotImplementedError("write bisect_first_bad")
