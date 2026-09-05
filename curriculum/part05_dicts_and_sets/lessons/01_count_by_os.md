# Counting with a dict

--- teach #bash-collections-worked
### Keep records structured between steps
You already know functions, loops and lists. A dict adds named fields: `row["units"]` reads one field.

Bash has arrays, but a pipeline between commands carries bytes, often text that the next command parses. Python functions can pass lists and dicts directly; you do not need to join fields into text and split them again.

```python
stock = [
    {"label": "blue pen", "units": 3},
    {"label": "red pad", "units": 2},
]
total = 0
for row in stock:
    total += row["units"]
print(total)                  # 5
print(stock[0]["label"])      # blue pen
```

`stock` remains a list of dicts in memory. Each label stays one string, including its space, and each unit count stays an integer. Printing displays a value; it does not turn the stored records into text.

--- code #bash-collections-modify
`total_units(rows)` currently counts records. Change one line so it adds their integer `"units"` values instead. Every record has that field; an empty list totals zero.

Browser: edit the function. Terminal: type the complete corrected function below the starter.
```python
def total_units(rows):
    total = 0
    for row in rows:
        total += 1
    return total
```
check: total_units([{"label": "amber folder", "units": 4}, {"label": "white eraser", "units": 2}]) == 6
check: total_units([{"label": "teal marker", "units": 0}, {"label": "black binder", "units": 7}]) == 7
check: total_units([]) == 0
solution: def total_units(rows):
solution:     total = 0
solution:     for row in rows:
solution:         total += row["units"]
solution:     return total
> Read the integer from each dict and add it. The records remain structured; no text conversion or splitting is needed.

--- code #bash-collections-check
Write `available_labels(rows)`. Return a list of the `"label"` strings whose integer `"units"` value is greater than zero, in input order. Every record has both fields. Keep spaces within each label; an empty input returns an empty list. Use the loop, `if` and `append` patterns you already know.

Browser: replace the function body. Terminal: type the complete function below the starter.
```python
def available_labels(rows):
    raise NotImplementedError("write available_labels")
```
check: available_labels([{"label": "green notebook", "units": 0}, {"label": "silver clip", "units": 4}, {"label": "cream envelope", "units": 2}]) == ["silver clip", "cream envelope"]
check: available_labels([{"label": "violet ribbon", "units": 3}, {"label": "orange card", "units": 0}, {"label": "gold sticker", "units": 1}]) == ["violet ribbon", "gold sticker"]
check: available_labels([]) == []
solution: def available_labels(rows):
solution:     labels = []
solution:     for row in rows:
solution:         if row["units"] > 0:
solution:             labels.append(row["label"])
solution:     return labels
> Selecting fields from dicts preserves complete labels and their order. A record with zero units is left out. The bridge is complete; continue this lesson or return to the diagnostic.

--- teach #card-0989e01b10375ae5
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

--- predict #card-ef0258bd1dbe5c46
What does this print?
```python
d = {"os": "macOS"}
print(d.get("serial", "unknown"))
```
answer: unknown
> There is no `serial` key, so `get` returns the default. With `d["serial"]` the program would stop with a `KeyError`.

--- teach #card-d07f1074c7905196
### `or` supplies a fallback for empty values
`get` only helps when the key is *missing*. A record can also carry `None` or `""` as the value. `x or "unknown"` returns `x` when it is truthy and `"unknown"` otherwise, and `None` and `""` are both falsy, so one expression handles all three cases.
```python
os_name = device.get("os") or "unknown"
```
Missing key: `get` gives `None`, `or` gives `"unknown"`. Empty string: `or` gives `"unknown"`. Real value: kept as is, no normalising.

--- predict #card-aa43efa9d9065a3d
What does this print?
```python
print({"os": ""}.get("os") or "unknown")
```
answer: unknown
> The key exists, so `get` returns `""`. An empty string is falsy, so `or` moves on to `"unknown"`.

--- code #card-f4c12ce9c656505a
Set `os_name` to the OS of `device`, or `"unknown"` when it is missing, `None` or empty.
```python
device = {"hostname": "mbp-1", "os": ""}
```
check: os_name == "unknown"
solution: os_name = device.get("os") or "unknown"
> `get` returns the empty string, which is falsy, so `or` supplies the fallback. The same line gives `"unknown"` for a missing key and for `None`, and keeps a real value untouched.

--- teach #card-6d1dfa148ff75f05
### The counting idiom
To count, look up the current count with a default of 0, add one, and store it back. The first time a key is seen `get` returns 0 and the entry is created with 1; every later time the existing count grows.
```python
counts = {}
for device in devices:
    os_name = device.get("os") or "unknown"
    counts[os_name] = counts.get(os_name, 0) + 1
```
Interviewers ask for this by hand. `collections.Counter` wraps the same loop; you meet it in Part 10.

--- fill #card-4b864d1b1e925ee1
Complete the counting line.
```python
counts[os_name] = counts.___(os_name, 0) + 1
```
answer: get
> `get(os_name, 0)` gives 0 for a new key and the current count for a known one. Adding 1 and assigning covers both cases without an `if`.

--- code #card-136249c9231d5142
Count how often each name appears in `names`, into a dict called `counts`.
```python
names = ["macOS", "Windows", "macOS"]
```
check: counts == {"macOS": 2, "Windows": 1}
solution: counts = {}
solution: for name in names:
solution:     counts[name] = counts.get(name, 0) + 1
> Start empty. The first `macOS` becomes 1, `Windows` becomes 1, and the second `macOS` reads the existing 1 and stores 2. The keys come out in first-seen order.

--- teach #card-16e6e448909859c8
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

--- quiz #card-8c8189ca39955d6b
After `d = {}; d["Windows"] = 1; d["macOS"] = 1; d["Windows"] = 2`, what is `list(d)`?
- [x] `['Windows', 'macOS']`
- [ ] `['macOS', 'Windows']`
- [ ] `['Windows', 'macOS', 'Windows']`
> `Windows` was inserted first, so it stays first; updating its value keeps its place. A dict has one entry per key, so it cannot appear twice.

--- exercise 5.1 #card-c365dd1dc64955d9

--- recap #card-4665a21b2e545b78
- `d[k]` raises on a missing key; `d.get(k, default)` returns the default.
- `device.get("os") or "unknown"` handles missing, `None` and `""` at once.
- Count with `counts[k] = counts.get(k, 0) + 1`.
- Dict keys keep first-insertion order; updates do not move them.
