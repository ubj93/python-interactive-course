# Counting with a dict

--- teach
### `d[k]` raises, `d.get(k)` does not
A dict maps keys to values. `d[k]` returns the value and raises `KeyError` when the key is missing. `d.get(k)` returns `None` instead, and `d.get(k, default)` returns your default. Pick the one you mean: raise when a missing key is a bug, `get` when it is normal.
```python
>>> device = {"hostname": "mbp-1"}
>>> device["os"]
KeyError: 'os'
>>> device.get("os")
None
>>> device.get("os", "unknown")
'unknown'
```

--- predict
What does this print?
```python
d = {"os": "macOS"}
print(d.get("serial", "unknown"))
```
answer: unknown
> There is no `serial` key, so `get` returns the default. With `d["serial"]` the program would stop with a `KeyError`.

--- teach
### `or` supplies a fallback for empty values
`get` only helps when the key is *missing*. A record can also carry `None` or `""` as the value. `x or "unknown"` returns `x` when it is truthy and `"unknown"` otherwise, and `None` and `""` are both falsy, so one expression handles all three cases.
```python
os_name = device.get("os") or "unknown"
```
Missing key: `get` gives `None`, `or` gives `"unknown"`. Empty string: `or` gives `"unknown"`. Real value: kept as is, no normalising.

--- predict
What does this print?
```python
print({"os": ""}.get("os") or "unknown")
```
answer: unknown
> The key exists, so `get` returns `""`. An empty string is falsy, so `or` moves on to `"unknown"`.

--- code
Set `os_name` to the OS of `device`, or `"unknown"` when it is missing, `None` or empty.
```python
device = {"hostname": "mbp-1", "os": ""}
```
check: os_name == "unknown"
solution: os_name = device.get("os") or "unknown"
> `get` returns the empty string, which is falsy, so `or` supplies the fallback. The same line gives `"unknown"` for a missing key and for `None`, and keeps a real value untouched.

--- teach
### The counting idiom
To count, look up the current count with a default of 0, add one, and store it back. The first time a key is seen `get` returns 0 and the entry is created with 1; every later time the existing count grows.
```python
counts = {}
for device in devices:
    os_name = device.get("os") or "unknown"
    counts[os_name] = counts.get(os_name, 0) + 1
```
Interviewers ask for this by hand. `collections.Counter` wraps the same loop; you meet it in Part 10.

--- fill
Complete the counting line.
```python
counts[os_name] = counts.___(os_name, 0) + 1
```
answer: get
> `get(os_name, 0)` gives 0 for a new key and the current count for a known one. Adding 1 and assigning covers both cases without an `if`.

--- code
Count how often each name appears in `names`, into a dict called `counts`.
```python
names = ["macOS", "Windows", "macOS"]
```
check: counts == {"macOS": 2, "Windows": 1}
solution: counts = {}
solution: for name in names:
solution:     counts[name] = counts.get(name, 0) + 1
> Start empty. The first `macOS` becomes 1, `Windows` becomes 1, and the second `macOS` reads the existing 1 and stores 2. The keys come out in first-seen order.

--- teach
### Dicts remember insertion order
Since Python 3.7 a dict keeps its keys in the order they were first inserted. Updating a value does not move the key. So the counting loop gives "keys in first-seen order" with no extra work, and `list(counts)` shows that order.
```python
>>> d = {}
>>> d["b"] = 1
>>> d["a"] = 1
>>> d["b"] = 2
>>> list(d)
['b', 'a']
```

--- quiz
After `d = {}; d["Windows"] = 1; d["macOS"] = 1; d["Windows"] = 2`, what is `list(d)`?
- [x] `['Windows', 'macOS']`
- [ ] `['macOS', 'Windows']`
- [ ] `['Windows', 'macOS', 'Windows']`
> `Windows` was inserted first, so it stays first; updating its value keeps its place. A dict has one entry per key, so it cannot appear twice.

--- exercise 5.1

--- recap
- `d[k]` raises on a missing key; `d.get(k, default)` returns the default.
- `device.get("os") or "unknown"` handles missing, `None` and `""` at once.
- Count with `counts[k] = counts.get(k, 0) + 1`.
- Dict keys keep first-insertion order; updates do not move them.
