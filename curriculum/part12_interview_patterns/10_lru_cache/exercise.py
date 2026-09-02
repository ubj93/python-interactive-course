"""A bounded cache of device lookups.

Every MDM API call to look up a device is slow, so we keep the most recent
lookups in memory. Memory is limited, so when the cache is full we throw out
the entry that was used longest ago (least recently used). Write the class
`LRUCache(capacity)` with:

- `get(key)`: return the cached value, or None when the key is absent. A hit
  counts as a use and makes that key the most recently used.
- `put(key, value)`: insert or update the value. Either way the key becomes
  the most recently used. When inserting a new key into a full cache, evict
  the least recently used key first.
- `len(cache)`: the number of entries currently held.

Rules:
- `capacity` must be at least 1; anything smaller raises ValueError in
  `__init__`
- keys are any hashable value; values are never None (so None from `get`
  always means a miss)
- updating an existing key does not evict anything
- get/put must both be O(1): no scanning of lists

Complexity target: O(1) for get and put, O(capacity) space. Use
collections.OrderedDict (move_to_end / popitem(last=False)) or a plain dict,
which also keeps insertion order. The last test runs 11,000 operations on a
cache of 1,000 entries.

Examples:
    >>> cache = LRUCache(2)
    >>> cache.put("C02XG1", {"name": "mbp-jdoe"})
    >>> cache.put("C02XG2", {"name": "mbp-asmith"})
    >>> cache.get("C02XG1")["name"]
    'mbp-jdoe'
    >>> cache.put("C02XG3", {"name": "mbp-new"})   # evicts C02XG2, used longest ago
    >>> cache.get("C02XG2") is None
    True
"""
from collections import OrderedDict
from typing import Any, Hashable, Optional


class LRUCache:
    def __init__(self, capacity: int) -> None:
        raise NotImplementedError("write LRUCache.__init__")

    def get(self, key: Hashable) -> Optional[Any]:
        raise NotImplementedError("write LRUCache.get")

    def put(self, key: Hashable, value: Any) -> None:
        raise NotImplementedError("write LRUCache.put")

    def __len__(self) -> int:
        raise NotImplementedError("write LRUCache.__len__")
