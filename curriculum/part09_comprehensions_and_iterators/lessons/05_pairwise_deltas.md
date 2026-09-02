# Adjacent pairs with zip

--- teach
### `zip` walks two sequences together
`zip(a, b)` pairs the first of `a` with the first of `b`, the second with the second, and stops when the shorter one runs out. Unpack each pair in the loop header.
```python
>>> list(zip(["a", "b", "c"], [1, 2]))
[('a', 1), ('b', 2)]
>>> for host, port in zip(hosts, ports):
...     ...
```

--- predict
What does this print?
```python
print(list(zip([1, 2, 3], ["x", "y"])))
```
answer: [(1, 'x'), (2, 'y')]
> `zip` stops at the shortest input, so the `3` has no partner and is dropped.

--- teach
### Zip a list with itself, shifted by one
`xs[1:]` is the list without its first item. Zipping `xs` with `xs[1:]` pairs every item with the one after it: exactly "each check-in and the next". The result has one pair fewer than the input, and fewer than two items gives no pairs at all, which is what the exercise wants.
```python
>>> ts = [0, 30, 45, 120]
>>> list(zip(ts, ts[1:]))
[(0, 30), (30, 45), (45, 120)]
>>> [b - a for a, b in zip(ts, ts[1:])]
[30, 15, 75]
```

--- predict
What does this print?
```python
ts = [0, 30, 45]
print([b - a for a, b in zip(ts, ts[1:])])
```
answer: [30, 15]
> The pairs are `(0, 30)` and `(30, 45)`; each pair is unpacked into `a` and `b` and the difference is collected.

--- teach
### Subtracting datetimes gives seconds
`datetime - datetime` is a `timedelta`. Its `.total_seconds()` returns a float, including fractions for milliseconds and full seconds for gaps that span days.
```python
>>> from datetime import datetime
>>> a = datetime(2024, 5, 1, 9, 0, 0)
>>> b = datetime(2024, 5, 1, 9, 0, 30)
>>> (b - a).total_seconds()
30.0
```
`.seconds` is not the same: it ignores the days part. Always use `total_seconds()`.

--- predict
What does this print?
```python
from datetime import datetime
a = datetime(2024, 5, 1, 9, 0)
b = datetime(2024, 5, 1, 9, 15)
print((b - a).total_seconds())
```
answer: 900.0
> Fifteen minutes is 900 seconds, and `total_seconds()` always returns a float.

--- teach
### Know the index so you can report it
A negative delta means the log is out of order and you must raise `ValueError` naming the offending index. A comprehension cannot raise, so use a loop, and `enumerate(..., start=1)` gives the index of the later item in each pair.
```python
deltas = []
for i, (a, b) in enumerate(zip(checkins, checkins[1:]), start=1):
    seconds = (b - a).total_seconds()
    if seconds < 0:
        raise ValueError(f"check-in {i} is earlier than check-in {i - 1}")
    deltas.append(seconds)
```
`for i, (a, b) in ...` unpacks the index and the pair in one header.

--- fill
Complete the loop header so `i` is the index of the later check-in in each pair.
```python
for i, (a, b) in ___(zip(checkins, checkins[1:]), start=1):
```
answer: enumerate
> `enumerate` adds a counter to any iterable. Starting at 1 makes `i` the position of `b`, so the error message points at the entry that went backwards.

--- exercise 9.5

--- recap
- `zip(a, b)` pairs items up and stops at the shortest.
- `zip(xs, xs[1:])` gives adjacent pairs; unpack them as `for a, b in ...`.
- `(later - earlier).total_seconds()` is a float, days included.
- When you need to raise on a bad item, use a loop with `enumerate`, not a comprehension.
