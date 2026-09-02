"""Reference solutions for RecentEvents."""
from collections import Counter, deque
from typing import Dict, List, Optional, Tuple


# Best practice: the deque is the single source of truth and counts are recomputed on
# demand. The window is small (maxlen), so Counter(self._events) is cheap and there is no
# second data structure that can drift out of sync.
class RecentEvents:
    def __init__(self, maxlen: int):
        if not isinstance(maxlen, int) or maxlen <= 0:
            raise ValueError("maxlen must be a positive int")
        self.maxlen = maxlen
        self._events = deque(maxlen=maxlen)

    def record(self, kind: str) -> None:
        self._events.append(kind)  # deque drops the oldest when full

    def __len__(self) -> int:
        return len(self._events)

    def counts(self) -> Dict[str, int]:
        return dict(Counter(self._events))

    def most_common(self, n: Optional[int] = None) -> List[Tuple[str, int]]:
        ranked = sorted(self.counts().items(), key=lambda kv: (-kv[1], kv[0]))
        return ranked if n is None else ranked[:n]

    def ratio(self, kind: str) -> float:
        if not self._events:
            return 0.0
        return self.counts().get(kind, 0) / len(self._events)

    def is_alerting(self, kind: str, threshold: float) -> bool:
        return len(self._events) == self.maxlen and self.ratio(kind) >= threshold


# Clever: keep a Counter in step with the deque so counts() is O(1). Before appending to a
# full deque, peek at [0] (the item about to fall off) and decrement it. More state, more
# ways to be wrong; worth it only when the window is huge or counts() is called constantly.
class RecentEventsIncremental:
    def __init__(self, maxlen: int):
        if not isinstance(maxlen, int) or maxlen <= 0:
            raise ValueError("maxlen must be a positive int")
        self.maxlen = maxlen
        self._events = deque(maxlen=maxlen)
        self._counts: Counter = Counter()

    def record(self, kind: str) -> None:
        if len(self._events) == self.maxlen:
            oldest = self._events[0]
            self._counts[oldest] -= 1
            if self._counts[oldest] == 0:
                del self._counts[oldest]
        self._events.append(kind)
        self._counts[kind] += 1

    def __len__(self) -> int:
        return len(self._events)

    def counts(self) -> Dict[str, int]:
        return dict(self._counts)

    def most_common(self, n: Optional[int] = None) -> List[Tuple[str, int]]:
        ranked = sorted(self._counts.items(), key=lambda kv: (-kv[1], kv[0]))
        return ranked if n is None else ranked[:n]

    def ratio(self, kind: str) -> float:
        return self._counts.get(kind, 0) / len(self._events) if self._events else 0.0

    def is_alerting(self, kind: str, threshold: float) -> bool:
        return len(self._events) == self.maxlen and self.ratio(kind) >= threshold
