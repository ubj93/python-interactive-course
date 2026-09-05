# Sorting with keys

--- teach #card-b24d908e3f735d41
### `sorted` with a `key` function
`sorted(items)` returns a new sorted list and leaves the input alone. `key=` names a function that turns each item into the value to sort by. `lambda` writes a small function inline.
```python
>>> sorted(devices, key=lambda d: d["name"])
```
Each device is passed to the lambda, which returns its name; the devices are ordered by those names, but the returned list still holds the devices themselves.

--- code #card-075e2f6968685d25
Set `by_name` to `devices` sorted by their `"name"`, without changing `devices`.
```python
devices = [{"name": "win-lab-01"}, {"name": "mbp-a-lee"}, {"name": "mbp-j-doe"}]
```
check: [d["name"] for d in by_name] == ["mbp-a-lee", "mbp-j-doe", "win-lab-01"]
check: devices[0]["name"] == "win-lab-01"
solution: by_name = sorted(devices, key=lambda d: d["name"])
> The lambda tells `sorted` what to compare; the result is a new list of the same dicts. `devices.sort(...)` would have reordered the input in place instead.

--- predict #card-e25a566a3c2b569e
What does this print?
```python
print(sorted([3, -5, 1], key=abs))
```
answer: [1, 3, -5]
> The key of each number is its absolute value (1, 3, 5), so the order is 1, 3, -5. The original values appear in the result, not the keys.

--- teach #card-fa8ef4a3f0de53a7
### Several keys: return a tuple
Tuples compare element by element, first difference wins. So a key that returns `(os, name)` sorts by OS and breaks ties by name. Add elements to the tuple for each extra tie-breaker, in priority order.
```python
sorted(devices, key=lambda d: (d["os"], d["name"]))
```

--- predict #card-943648d0362b580c
What does this print?
```python
rows = [("mac", 2), ("linux", 9), ("mac", 1)]
print(sorted(rows, key=lambda r: (r[0], r[1])))
```
answer: [('linux', 9), ('mac', 1), ('mac', 2)]
> "linux" sorts before "mac". The two macs tie on the first element, so the second element decides: 1 before 2.

--- teach #card-6cdfd020362c5ad2
### Descending for one key: negate a number
`reverse=True` flips the whole sort. To flip only the middle key, make that element of the tuple a number and negate it. A `date` cannot be negated, but `d.toordinal()` gives an int (days since year 1) that can.
```python
sorted(devices, key=lambda d: (d["os"], -d["last_seen"].toordinal(), d["name"]))
```
A bigger ordinal means a newer date; negating it puts newest first while `os` and `name` stay ascending.

--- code #card-d054f605a36753ca
Set `result` to `rows` sorted by OS ascending, then by count descending.
```python
rows = [("mac", 3), ("mac", 9), ("linux", 1), ("windows", 5)]
```
check: result == [("linux", 1), ("mac", 9), ("mac", 3), ("windows", 5)]
solution: result = sorted(rows, key=lambda r: (r[0], -r[1]))
> The tuple key sorts by OS first. Negating the count makes 9 come before 3 within "mac" while the OS order stays ascending, which `reverse=True` could not do on its own.

--- teach #card-7569464350b951fd
### `None` cannot be compared; put a boolean in the tuple
`None < date` raises `TypeError`. Add `d["last_seen"] is None` to the tuple before the date: `False` sorts before `True`, so real dates come first and `None` goes last. For the `None` rows, use a placeholder such as `0` in the date slot so the tuple is still comparable.
```python
def key(d):
    seen = d["last_seen"]
    return (d["os"], seen is None, -seen.toordinal() if seen else 0, d["name"])
```
`x if cond else y` is a conditional expression: one value or the other, in one line.

--- quiz #card-75dd1147946f5ee9
What does the `seen is None` element in the key tuple do?
- [ ] Removes devices with no `last_seen`
- [x] Sorts devices with a real date (`False`) before those with `None` (`True`)
- [ ] Raises `TypeError` for `None`
> Booleans compare as 0 and 1. Every real date gets `False`, every `None` gets `True`, so within one OS the `None` rows sink to the end and the date element never has to compare `None` with a date.

--- exercise 9.4 #card-ad2c255203155d42

--- recap #card-c01c397799895e1c
- `sorted(items, key=f)` returns a new list ordered by `f(item)`.
- A tuple key sorts by several fields; the first difference wins.
- Negate a number (or `date.toordinal()`) to make one key descending.
- `(x is None, ...)` puts `None` last and avoids comparing it.
