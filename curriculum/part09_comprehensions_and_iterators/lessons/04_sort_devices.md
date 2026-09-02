# Sorting with keys

--- teach
### `sorted` with a `key` function
`sorted(items)` returns a new sorted list and leaves the input alone. `key=` names a function that turns each item into the value to sort by. `lambda` writes a small function inline.
```python
>>> sorted(devices, key=lambda d: d["name"])
```
Each device is passed to the lambda, which returns its name; the devices are ordered by those names, but the returned list still holds the devices themselves.

--- predict
What does this print?
```python
print(sorted([3, -5, 1], key=abs))
```
answer: [1, 3, -5]
> The key of each number is its absolute value (1, 3, 5), so the order is 1, 3, -5. The original values appear in the result, not the keys.

--- teach
### Several keys: return a tuple
Tuples compare element by element, first difference wins. So a key that returns `(os, name)` sorts by OS and breaks ties by name. Add elements to the tuple for each extra tie-breaker, in priority order.
```python
sorted(devices, key=lambda d: (d["os"], d["name"]))
```

--- predict
What does this print?
```python
rows = [("mac", 2), ("linux", 9), ("mac", 1)]
print(sorted(rows, key=lambda r: (r[0], r[1])))
```
answer: [('linux', 9), ('mac', 1), ('mac', 2)]
> "linux" sorts before "mac". The two macs tie on the first element, so the second element decides: 1 before 2.

--- teach
### Descending for one key: negate a number
`reverse=True` flips the whole sort. To flip only the middle key, make that element of the tuple a number and negate it. A `date` cannot be negated, but `d.toordinal()` gives an int (days since year 1) that can.
```python
sorted(devices, key=lambda d: (d["os"], -d["last_seen"].toordinal(), d["name"]))
```
A bigger ordinal means a newer date; negating it puts newest first while `os` and `name` stay ascending.

--- fill
Complete the key so the newest `last_seen` comes first within each OS.
```python
key=lambda d: (d["os"], ___d["last_seen"].toordinal(), d["name"])
```
answer: -
> Negating the ordinal turns "largest first" into "smallest first", which is what an ascending sort does. Only this element is flipped.

--- teach
### `None` cannot be compared; put a boolean in the tuple
`None < date` raises `TypeError`. Add `d["last_seen"] is None` to the tuple before the date: `False` sorts before `True`, so real dates come first and `None` goes last. For the `None` rows, use a placeholder such as `0` in the date slot so the tuple is still comparable.
```python
def key(d):
    seen = d["last_seen"]
    return (d["os"], seen is None, -seen.toordinal() if seen else 0, d["name"])
```
`x if cond else y` is a conditional expression: one value or the other, in one line.

--- quiz
What does the `seen is None` element in the key tuple do?
- [ ] Removes devices with no `last_seen`
- [x] Sorts devices with a real date (`False`) before those with `None` (`True`)
- [ ] Raises `TypeError` for `None`
> Booleans compare as 0 and 1. Every real date gets `False`, every `None` gets `True`, so within one OS the `None` rows sink to the end and the date element never has to compare `None` with a date.

--- exercise 9.4

--- recap
- `sorted(items, key=f)` returns a new list ordered by `f(item)`.
- A tuple key sorts by several fields; the first difference wins.
- Negate a number (or `date.toordinal()`) to make one key descending.
- `(x is None, ...)` puts `None` last and avoids comparing it.
