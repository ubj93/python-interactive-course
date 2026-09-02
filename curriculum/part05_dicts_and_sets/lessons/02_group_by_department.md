# Grouping with setdefault

--- teach
### A dict of lists
Grouping means one key per group and a list of members as the value. Appending to `groups[dept]` extends that group's list. The catch is the first member: the key does not exist yet, so `groups[dept]` would raise `KeyError`.
```python
groups = {"Finance": ["mbp-1"]}
groups["Finance"].append("mbp-3")     # fine, the list exists
groups["IT"].append("mbp-2")          # KeyError: 'IT'
```

--- teach
### `setdefault` creates the group on first sight
`d.setdefault(key, default)` returns the existing value if the key is there; otherwise it inserts the default and returns *that*. Either way you get the list back, so you can append to it in the same line.
```python
groups = {}
for device in devices:
    groups.setdefault(dept, []).append(hostname)
```
First time for a department: an empty list is inserted and the hostname appended. Later: the existing list is returned and grows. Groups appear in first-seen order because the dict keeps insertion order.

--- predict
What does this print?
```python
g = {}
g.setdefault("IT", []).append("a")
g.setdefault("IT", []).append("b")
print(g)
```
answer: {'IT': ['a', 'b']}
> The first call inserts `[]` and appends `a`. The second finds the key, returns the same list, and appends `b`. The default `[]` on the second call is created but never used.

--- code
Group the hostnames in `pairs` by department into a dict called `groups`.
```python
pairs = [("IT", "a"), ("Finance", "b"), ("IT", "c")]
```
check: groups == {"IT": ["a", "c"], "Finance": ["b"]}
check: list(groups) == ["IT", "Finance"]
solution: groups = {}
solution: for dept, host in pairs:
solution:     groups.setdefault(dept, []).append(host)
> Unpack each pair in the loop header. `setdefault` creates `IT` and `Finance` the first time each is seen, and the second `IT` reuses the existing list.

--- quiz
How does `d.setdefault(k, [])` differ from `d.get(k, [])`?
- [x] `setdefault` inserts the default into the dict when the key is missing; `get` never changes the dict
- [ ] `get` raises `KeyError` when the key is missing
- [ ] They are the same
> `get(k, [])` hands you a new list that is not stored anywhere, so appending to it is lost. `setdefault` stores it, which is what grouping needs.

--- teach
### Normalise the key before grouping
The department may be missing, `None`, or padded with spaces. `(x or "")` turns `None` into `""`, `strip()` removes the spaces, and a final `or "unassigned"` catches anything that is empty after stripping. Case is left alone: `"IT"` and `"it"` are different groups.
```python
department = (device.get("department") or "").strip() or "unassigned"
```
Read it left to right: value or empty, stripped, or the fallback.

--- predict
What does this print?
```python
print(("   " or "").strip() or "unassigned")
```
answer: unassigned
> `"   "` is truthy (it has characters), so the first `or` keeps it. `strip()` makes it `""`, which is falsy, so the second `or` gives `"unassigned"`.

--- code
Set `dept` to the department of `device`: stripped of surrounding spaces, or `"unassigned"` when missing, `None` or blank.
```python
device = {"hostname": "mbp-1", "department": " Finance "}
```
check: dept == "Finance"
solution: dept = (device.get("department") or "").strip() or "unassigned"
> `get` returns `" Finance "`, the `or ""` leaves it alone, `strip()` trims it, and the final `or` is not needed because the result is truthy. Swap in `"   "` or drop the key and the same line gives `"unassigned"`.

--- teach
### Skip what the spec says to skip
A device with no hostname, or `None` as its hostname, must not appear anywhere, and must not create an empty group. So test the hostname and `continue` *before* the `setdefault` line runs.
```python
hostname = device.get("hostname")
if hostname is None:
    continue
department = ...
groups.setdefault(department, []).append(hostname)
```
Order matters: a `setdefault` before the check would leave an empty list behind.

--- fill
Complete the guard so devices without a hostname are skipped.
```python
if device.get("hostname") ___ None:
    continue
```
answer: is
> `get` returns `None` for a missing key and the stored `None` for an explicit one; `is None` catches both. Test for `None` with `is`, not `==`.

--- exercise 5.2

--- recap
- Grouping is a dict whose values are lists.
- `groups.setdefault(key, []).append(item)` creates the list on first sight and reuses it after.
- `(x or "").strip() or "unassigned"` normalises a messy key.
- Skip bad records before touching the dict, so no empty groups appear.
