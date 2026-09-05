# Finding the best one

--- teach #card-59b5b7e682a75a69
### ISO dates compare as text
An ISO date is `"YYYY-MM-DD"`: year, then month, then day, each a fixed width. Because the biggest part comes first, plain string comparison puts dates in the right order. No datetime module needed.
```python
>>> "2021-06-30" < "2022-01-05"
True
>>> "2023-02-14" < "2023-02-09"
False
```
This is the reason the format exists. It does not work for version strings like `"10.2"`, where the widths vary.

--- predict #card-3cccbd6250395adb
What does this print?
```python
print("2022-11-01" < "2021-12-31")
```
answer: False
> Strings compare character by character. The first difference is the fourth character: "2" versus "1", so "2022..." is the greater string.

--- teach #card-13403ae378c25628
### The running-best pattern
To find the smallest (or largest) item, keep one "best so far" and replace it whenever you see something better. Start with `None`, which means "nothing seen yet".
```python
oldest = None
for d in devices:
    if oldest is None or d["enrolled"] < oldest["enrolled"]:
        oldest = d
```
Starting with `None` handles the empty list for free: the loop never runs, `oldest` stays `None`, and that is what you return. Starting with `devices[0]` crashes on `[]`.

--- code #card-f3b99b0d2c325a82
Set `oldest` to the record with the earliest `"enrolled"` date, using a running best that starts from `None`. Then print its hostname.
```python
fleet = [{"hostname": "a", "enrolled": "2023-02-14"}, {"hostname": "b", "enrolled": "2021-06-30"}, {"hostname": "c", "enrolled": "2022-11-01"}]
```
expect: b
check: oldest["hostname"] == "b"
solution: oldest = None
solution: for d in fleet:
solution:     if oldest is None or d["enrolled"] < oldest["enrolled"]:
solution:         oldest = d
solution: print(oldest["hostname"])
> `oldest is None` accepts the first record; after that a record only replaces it when its date is strictly smaller. "2021-06-30" is the smallest string.

--- quiz #card-677083ddcc155106
Why start the running best with `None` rather than `devices[0]`?
- [x] `devices[0]` raises `IndexError` on an empty list
- [ ] `None` compares smaller than any string
- [ ] `devices[0]` would be skipped by the loop
> An empty list has no `[0]`. With `None`, the loop simply never replaces it and you return `None`, exactly what the exercise asks for.

--- teach #card-4976d275d1165822
### Ties: `<` keeps the first, `<=` keeps the last
Replace only when the new value is strictly smaller. If two records share the earliest date, the first one seen stays the winner. With `<=` the later one would take over. Ask "who wins a tie?" out loud in an interview; it is always specified somewhere.
```python
if oldest is None or d["enrolled"] < oldest["enrolled"]:   # first wins ties
```

--- predict #card-8eae362daa39512c
What does this print?
```python
best = None
for d in [{"h": "x", "on": "2020-05-05"}, {"h": "y", "on": "2020-05-05"}]:
    if best is None or d["on"] < best["on"]:
        best = d
print(best["h"])
```
answer: x
> `"2020-05-05" < "2020-05-05"` is False, so `y` never replaces `x`. Strict `<` keeps the first of equals.

--- teach #card-9933d7dff9cc5568
### Skip what you cannot compare
Records with no date, or `None`, must not take part; `None < "2021-01-01"` raises `TypeError`. Use `continue` to jump to the next record. At the end return the hostname, not the whole record, and `None` when nothing qualified.
```python
for d in devices:
    if d.get("enrolled") is None:
        continue
    ...
if oldest is None:
    return None
return oldest["hostname"]
```
`continue` says "skip the rest of this pass, go to the next item".

--- code #card-94852d64040f5421
Set `earliest` to the smallest date in `dates`, skipping the `None` entries with `continue`.
```python
dates = ["2023-01-01", None, "2022-01-01", None]
```
check: earliest == "2022-01-01"
solution: earliest = None
solution: for d in dates:
solution:     if d is None:
solution:         continue
solution:     if earliest is None or d < earliest:
solution:         earliest = d
> The `continue` guard means the comparison below never sees `None`, so `None < "2022-01-01"` can never crash the loop.

--- fill #card-4b780800066a58da
Complete the line so records without a date are skipped.
```python
if d.get("enrolled") is None:
    ___
```
answer: continue
> `continue` moves straight to the next record. `break` would stop the whole loop, and `return` would end the function early.

--- exercise 2.2 #card-a30f73f8714e52ff

--- recap #card-28ded9cc24585c44
- ISO dates `"YYYY-MM-DD"` compare correctly as strings.
- Running best: start with `None`, replace when you see better.
- Strict `<` means the first of equals wins.
- `continue` skips a record; return `None` when nothing qualified.
