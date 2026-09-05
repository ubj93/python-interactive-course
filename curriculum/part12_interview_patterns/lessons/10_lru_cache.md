# LRU cache: O(1) get and put

--- teach #card-b9cf2b1c3b575dc0
### The pattern: a bounded cache that forgets the oldest use
"Cache the last 1,000 device lookups; when full, evict the one used longest ago." A brute force keeps a dict for values and a list of keys in order of use. Every hit moves the key to the end of the list.
```python
class LRUSlow:
    def __init__(self, capacity):
        self.capacity, self.data, self.order = capacity, {}, []
    def get(self, key):
        if key not in self.data:
            return None
        self.order.remove(key)          # scans the list
        self.order.append(key)
        return self.data[key]
```
`list.remove` walks the list to find the key. The pattern: keep the order *inside* the dict, so nothing is ever scanned.

--- quiz #card-03b9edb8c5635a05
What does `self.order.remove(key)` cost on a cache holding n keys?
- [ ] O(1): the list knows where every key is
- [x] O(n): it scans until it finds the key, then shifts the rest
- [ ] O(log n): the list is kept sorted
> A list has no index of its contents; `remove` compares from the front and then shifts everything after the gap. The spec demands O(1) for get and put, so a list of keys cannot be the answer.

--- teach #card-01dd8fc2c79456be
### The insight: `OrderedDict` remembers order and can move a key
Python dicts keep insertion order. `collections.OrderedDict` adds two O(1) moves: `move_to_end(key)` makes a key the newest, and `popitem(last=False)` removes the oldest.
```python
>>> from collections import OrderedDict
>>> d = OrderedDict(a=1, b=2, c=3)
>>> d.move_to_end("a")
>>> list(d)
['b', 'c', 'a']
>>> d.popitem(last=False)
('b', 2)
```
So "most recently used" is simply "last in the dict", and "least recently used" is "first in the dict".

--- code #card-5251292a17805a79
Make `"a"` the most recently used key, then print the *oldest* key using `next(iter(d))`.
```python
from collections import OrderedDict
d = OrderedDict(a=1, b=2, c=3)
```
expect: b
solution: d.move_to_end("a")
solution: print(next(iter(d)))
> After the move the order is b, c, a. `iter(d)` walks keys from the front, so `next` gives `b`, the least recently used. This is the same trick that works on a plain dict.

--- predict #card-31afe79efb4d510d
What does this print?
```python
from collections import OrderedDict
d = OrderedDict(a=1, b=2, c=3)
d.move_to_end("b")
d.popitem(last=False)
print(list(d))
```
answer: ['c', 'b']
> `move_to_end("b")` makes the order a, c, b. `popitem(last=False)` removes the first key, `a`. What remains is `['c', 'b']`.

--- teach #card-85dde37ccb6a5333
### get and put in a few lines
A `get` miss returns `None` and touches nothing. A hit moves the key to the end and returns the value. A `put` stores the value, moves the key to the end, and evicts the first key only if the cache has grown past its capacity.
```python
def get(self, key):
    if key not in self._data:
        return None
    self._data.move_to_end(key)
    return self._data[key]

def put(self, key, value):
    self._data[key] = value
    self._data.move_to_end(key)
    if len(self._data) > self.capacity:
        self._data.popitem(last=False)
```
Updating an existing key does not change `len`, so it never evicts.

--- code #card-04ebd15a87825fc1
Write the body of `put`: store the value, move the key to the end, and evict the oldest entry when the cache has grown past its capacity. Then put `a`, `b`, `c` into a cache of capacity 2 and print `list(cache._data)`.
```python
from collections import OrderedDict
class LRU:
    def __init__(self, capacity):
        self.capacity, self._data = capacity, OrderedDict()
    def put(self, key, value):
```
expect: ['b', 'c']
solution:         self._data[key] = value
solution:         self._data.move_to_end(key)
solution:         if len(self._data) > self.capacity:
solution:             self._data.popitem(last=False)
solution: cache = LRU(2)
solution: cache.put("a", 1)
solution: cache.put("b", 2)
solution: cache.put("c", 3)
solution: print(list(cache._data))
> Inserting `c` makes three entries, one over capacity, so `popitem(last=False)` removes `a`, the front. The method body is indented eight spaces because it sits inside the class.

--- fill #card-583535f80ea75116
Complete the eviction so it removes the least recently used entry.
```python
if len(self._data) > self.capacity:
    self._data.popitem(last=___)
```
answer: False
> `popitem()` defaults to `last=True`, the newest entry, which would evict what you just stored. `last=False` removes the oldest, at the front of the order.

--- quiz #card-36664eae5c9158a3
Capacity 2. `put("a", 1)`, `put("b", 2)`, `get("a")`, `put("c", 3)`. Which key is evicted?
- [ ] `a`
- [x] `b`
- [ ] `c`
> `get("a")` moved `a` to the end, so the order is b, a. Inserting `c` makes three entries; the oldest, `b`, goes. A miss on a key that is absent must not move anything.

--- teach #card-0eb916489d7b5feb
### The cost, and how to say it
Every operation is a dict lookup plus an O(1) move at the end of the order: O(1) for get and put, O(capacity) space.

Say it out loud: "An LRU cache is an ordered dict where the front is the oldest use. A hit moves the key to the back, an insert that overflows pops the front. `OrderedDict` gives me `move_to_end` and `popitem(last=False)`; with a plain dict I would delete and reinsert the key and use `next(iter(d))` for the oldest."

Finish the class: `__init__` raises `ValueError` when `capacity < 1`, and `__len__` returns `len(self._data)`. Mention `functools.lru_cache` for pure functions, then explain why the interviewer still wants the class.

--- exercise 12.10 #card-c3140bcd2fe05bc4

--- recap #card-396ba4ee392c5ea3
- "Keep the last N, evict the least recently used" is the LRU pattern; get and put must be O(1).
- `OrderedDict`: front is oldest, back is newest; `move_to_end` and `popitem(last=False)` are O(1).
- A hit moves the key to the end; a miss touches nothing; an update never evicts.
- Validate `capacity >= 1` in `__init__`; `__len__` reports entries held.
