"""Reference solutions for LRUCache."""
from collections import OrderedDict
from typing import Any, Dict, Hashable, Optional


# Best practice: OrderedDict keeps keys in usage order. move_to_end marks a key as most
# recently used, popitem(last=False) removes the least recently used. Every operation
# is a hash lookup plus a constant-time link update.
# Time O(1) per get/put, space O(capacity).
class LRUCache:
    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError(f"capacity must be at least 1, got {capacity}")
        self.capacity = capacity
        self._entries: "OrderedDict[Hashable, Any]" = OrderedDict()

    def get(self, key: Hashable) -> Optional[Any]:
        if key not in self._entries:
            return None
        self._entries.move_to_end(key)
        return self._entries[key]

    def put(self, key: Hashable, value: Any) -> None:
        self._entries[key] = value
        self._entries.move_to_end(key)
        if len(self._entries) > self.capacity:
            self._entries.popitem(last=False)

    def __len__(self) -> int:
        return len(self._entries)


# Alternative: a plain dict. Since 3.7 dicts keep insertion order, so deleting and
# re-inserting a key moves it to the end and next(iter(d)) is the oldest key.
# Same O(1) costs; fewer imports, slightly less self-explanatory.
class LRUCacheDict:
    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError(f"capacity must be at least 1, got {capacity}")
        self.capacity = capacity
        self._entries: Dict[Hashable, Any] = {}

    def get(self, key: Hashable) -> Optional[Any]:
        if key not in self._entries:
            return None
        value = self._entries.pop(key)
        self._entries[key] = value
        return value

    def put(self, key: Hashable, value: Any) -> None:
        self._entries.pop(key, None)
        self._entries[key] = value
        if len(self._entries) > self.capacity:
            del self._entries[next(iter(self._entries))]

    def __len__(self) -> int:
        return len(self._entries)
