# A sliding window with deque

--- teach
### `deque(maxlen=n)` forgets the oldest on its own
A `deque` (say "deck") is a list built for adding and removing at both ends. With `maxlen`, it holds at most `n` items: appending to a full deque silently drops the oldest one. That is a sliding window in one line, with no `pop(0)` and no index maths.
```python
>>> from collections import deque
>>> window = deque(maxlen=3)
>>> for x in [1, 2, 3, 4]:
...     window.append(x)
>>> list(window), len(window)
([2, 3, 4], 3)
```

--- code
Record every kind in `events` into a deque that keeps only the last 3, then print it as a list.
```python
from collections import deque
events = ["ok", "ok", "timeout", "auth_failed", "timeout"]
```
expect: ['timeout', 'auth_failed', 'timeout']
solution: window = deque(maxlen=3)
solution: for kind in events:
solution:     window.append(kind)
solution: print(list(window))
> Five appends into a window of three: the two `"ok"` events fall off the left as the later ones arrive.

--- predict
What does this print?
```python
from collections import deque
w = deque(maxlen=3)
for kind in ["ok", "timeout", "timeout", "timeout"]:
    w.append(kind)
print(list(w))
```
answer: ['timeout', 'timeout', 'timeout']
> The fourth append pushes out `"ok"`, the oldest item. Only the last three survive.

--- teach
### `Counter` counts whatever you give it
`Counter(iterable)` is a dict of item to count. Reading a missing key gives 0 instead of `KeyError`. Wrapping in `dict()` returns a plain dict, which is what callers expect, and since the Counter was built from the items present, no zero counts appear.
```python
>>> from collections import Counter
>>> c = Counter(["ok", "timeout", "ok"])
>>> c["ok"], c["disk_full"]
(2, 0)
>>> dict(c)
{'ok': 2, 'timeout': 1}
```
Recompute `Counter(self._events)` each time: the window is small, and one source of truth cannot drift.

--- predict
What does this print?
```python
from collections import Counter
print(dict(Counter(["ok", "timeout", "ok"])))
```
answer: {'ok': 2, 'timeout': 1}
> Keys appear in first-seen order with their counts. `dict()` drops the `Counter(...)` wrapper.

--- teach
### Sort by count down, then name up
`sorted` takes a `key` function; when the key is a tuple, ties on the first element are decided by the second. Negate the count so bigger comes first while names still sort A to Z. Slice `[:n]` to take the top `n`.
```python
>>> counts = {"timeout": 2, "ok": 2, "auth_failed": 1}
>>> sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
[('ok', 2), ('timeout', 2), ('auth_failed', 1)]
```
`kv` is a `(kind, count)` pair, so `kv[1]` is the count and `kv[0]` the kind.

--- code
Set `ranked` to the items of `counts` sorted by count descending, then kind ascending.
```python
counts = {"timeout": 2, "disk_full": 1, "ok": 2, "auth_failed": 1}
```
check: ranked == [("ok", 2), ("timeout", 2), ("auth_failed", 1), ("disk_full", 1)]
solution: ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
> The key tuple `(-count, kind)` puts the 2s before the 1s, and inside each group the names sort alphabetically.

--- fill
Complete the key so items sort by count descending, then kind ascending.
```python
ranked = sorted(counts.items(), key=lambda kv: (___, kv[0]))
```
answer: -kv[1]
> Sorting ascending on `-count` puts the largest count first. `kv[0]` breaks ties alphabetically.

--- teach
### Ratios, and the full-window rule
`ratio(kind)` is count divided by window length; guard the empty window so you never divide by zero. `is_alerting` needs **two** things: the window is full (`len == maxlen`) and the ratio meets the threshold. Three timeouts out of three is not evidence when the window wants ten. Defining `__len__` on the class makes `len(window)` work.
```python
def ratio(self, kind):
    if not self._events:
        return 0.0
    return self.counts().get(kind, 0) / len(self._events)

def is_alerting(self, kind, threshold):
    return len(self._events) == self.maxlen and self.ratio(kind) >= threshold
```

--- quiz
A window with `maxlen=4` holds three events, all `"timeout"`. What is `is_alerting("timeout", 0.5)`?
- [ ] `True`, the ratio is 1.0
- [x] `False`, the window is not full yet
- [ ] It raises `ValueError`
> The ratio passes, but a partially filled window is not enough evidence. Both conditions must hold.

--- exercise 10.5

--- recap
- `deque(maxlen=n)` keeps the last `n` items and drops the oldest automatically.
- `Counter(items)` counts; missing keys read as 0; `dict(...)` freezes it.
- `sorted(..., key=lambda kv: (-kv[1], kv[0]))` orders by count down, name up.
- Guard division by zero; alert only when the window is full.
