"""A sliding window of recent events.

An agent reports one outcome per check-in: "ok", "auth_failed", "timeout", ...
We want to alert when most of the *last N* check-ins failed, not the last hour
and not all time. Implement `RecentEvents(maxlen)` on top of
`collections.deque(maxlen=...)`, which drops the oldest item automatically once
it is full.

- `RecentEvents(maxlen)`: maxlen must be a positive int, otherwise ValueError.
- `record(kind)`: append one event; once the window holds maxlen events the
  oldest one is discarded.
- `len(window)`: number of events currently in the window, never above maxlen.
- `counts()`: dict of kind -> count for the events currently in the window.
  Only kinds with a count above zero appear (an evicted kind disappears).
- `most_common(n=None)`: list of (kind, count) sorted by count descending,
  then kind ascending so ties are deterministic. All kinds when n is None.
- `ratio(kind)`: fraction of the window that is `kind`; 0.0 for an empty window.
- `is_alerting(kind, threshold)`: True only when the window is full AND
  ratio(kind) >= threshold. A partially filled window is not enough evidence
  and never alerts.

Examples:
    >>> w = RecentEvents(3)
    >>> for k in ["ok", "timeout", "timeout", "timeout"]:
    ...     w.record(k)
    >>> w.counts()
    {'timeout': 3}
    >>> len(w), w.ratio("timeout"), w.is_alerting("timeout", 0.66)
    (3, 1.0, True)
"""
from collections import Counter, deque
from typing import Dict, List, Optional, Tuple


class RecentEvents:
    def __init__(self, maxlen: int):
        raise NotImplementedError("write RecentEvents.__init__")

    def record(self, kind: str) -> None:
        raise NotImplementedError("write RecentEvents.record")

    def __len__(self) -> int:
        raise NotImplementedError("write RecentEvents.__len__")

    def counts(self) -> Dict[str, int]:
        raise NotImplementedError("write RecentEvents.counts")

    def most_common(self, n: Optional[int] = None) -> List[Tuple[str, int]]:
        raise NotImplementedError("write RecentEvents.most_common")

    def ratio(self, kind: str) -> float:
        raise NotImplementedError("write RecentEvents.ratio")

    def is_alerting(self, kind: str, threshold: float) -> bool:
        raise NotImplementedError("write RecentEvents.is_alerting")
