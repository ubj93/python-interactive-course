# Counting records

--- teach #card-48f68a92f31b5f4c
### A list of dicts is a table
Inventory arrives as a list where each item is a dict (a dictionary): named fields, like one row of a spreadsheet. Square brackets with the field name read a field.
```python
fleet = [
    {"hostname": "mbp-j-doe", "status": "online"},
    {"hostname": "win-lab-01", "status": "offline"},
]
>>> fleet[0]["hostname"]
'mbp-j-doe'
>>> len(fleet)
2
```
`fleet[0]` is the first record; `["hostname"]` is its hostname field.

--- predict #card-fda31a891d365c58
What does this print?
```python
fleet = [{"hostname": "a", "status": "online"}, {"hostname": "b", "status": "offline"}]
print(fleet[1]["status"])
```
answer: offline
> `fleet[1]` is the second dict (indexes start at 0), and `["status"]` reads its status field.

--- teach #card-1f71b9f0d71a5cf1
### `for` walks the records
`for d in devices` hands you one dict at a time; you never need an index. Inside the block, `d` is the current record.
```python
for d in fleet:
    print(d["hostname"])
```
The `for i in range(len(devices))` version you see in interviews works, but it says "I think in indexes". Walk the items directly.

--- code #card-f2fc24d73f105840
Print each hostname in `fleet`, one per line.
```python
fleet = [{"hostname": "mbp-j-doe", "status": "online"}, {"hostname": "nuc-01", "status": "offline"}]
```
expect: mbp-j-doe\nnuc-01
solution: for d in fleet:
solution:     print(d["hostname"])
> The loop gives you one dict at a time as `d`; `d["hostname"]` reads the field to print.

--- teach #card-5a2c878d5e375f35
### Missing keys: `[]` crashes, `.get()` does not
`d["status"]` raises `KeyError` when the key is not there. `d.get("status")` returns `None` instead, and `d.get("status", "")` returns `""`. Use `.get` when a field is optional, `[]` when its absence is a bug you want to hear about.
```python
>>> d = {"hostname": "a"}
>>> print(d.get("status"))
None
>>> d.get("status", "unknown")
'unknown'
```

--- quiz #card-3f8fd816a0995043
A record may have no `"status"` key. Which expression reads it without crashing?
- [ ] `d["status"]`
- [x] `d.get("status")`
- [ ] `d.status`
> `.get` returns `None` for a missing key. `d["status"]` raises `KeyError`, and dicts do not support dot access.

--- teach #card-2d151c1fc9185717
### The count pattern
Start at zero, walk the list, add one when the record qualifies. Normalise the status first with the Part 1 idiom, so `None`, odd casing and stray spaces all get the same treatment.
```python
online = 0
for d in devices:
    status = (d.get("status") or "").strip().lower()
    if status == "online":
        online += 1
return online
```
`online += 1` is short for `online = online + 1`. Nothing is written back into `d`, so the records stay untouched.

--- code #card-59031eb675e15314
Set `online` to the number of records whose status is online, ignoring case and surrounding whitespace. A record with no status does not count.
```python
fleet = [{"hostname": "a", "status": " Online "}, {"hostname": "b"}, {"hostname": "c", "status": "offline"}, {"hostname": "d", "status": "ONLINE"}]
```
check: online == 2
solution: online = 0
solution: for d in fleet:
solution:     status = (d.get("status") or "").strip().lower()
solution:     if status == "online":
solution:         online += 1
> Start at 0, normalise each status with `(d.get("status") or "").strip().lower()`, and add one for each match. Records a and d qualify; b has no status and c is offline.

--- predict #card-b0a9e3b302fa5e86
What does this print?
```python
count = 0
for s in ["Online", " online ", "on line"]:
    if s.strip().lower() == "online":
        count += 1
print(count)
```
answer: 2
> "Online" and " online " both become "online" after `strip().lower()`. "on line" keeps its inner space and does not match.

--- fill #card-159a49037c3a5696
Complete the line so a missing status becomes an empty string instead of crashing.
```python
status = (d.___("status") or "").strip().lower()
```
answer: get
> `d.get("status")` gives `None` when the key is absent; `or ""` turns that `None` into `""`, which `strip()` and `lower()` handle happily.

--- exercise 2.1 #card-2df8e9f650125640

--- recap #card-46b0f1462a1a5e17
- A list of dicts is a table; `d["key"]` reads a field.
- `for d in devices:` walks the records; no index needed.
- `d.get("key")` returns `None` for a missing key instead of raising.
- Count pattern: start at 0, `+= 1` for each match.
