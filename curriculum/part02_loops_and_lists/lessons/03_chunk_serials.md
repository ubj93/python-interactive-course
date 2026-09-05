# Slicing into batches

--- teach #bash-aliasing-worked
### A second name can share the same list
You already know lists, functions and `append`. In Bash, expanding a scalar value into another variable copies its text. In Python, assigning an existing list or dict to another name points both names at the same object. Assignment does not copy the collection.

```python
labels = ["draft"]
alias = labels
alias.append("checked")
print(labels)                 # ['draft', 'checked']

separate = labels.copy()
separate.append("sent")
print(labels)                 # ['draft', 'checked']
print(separate)               # ['draft', 'checked', 'sent']
```

Appending through `alias` changes the shared list. `.copy()` creates a different outer list, so appending through `separate` leaves `labels` alone. A dict also has `.copy()`.

These are **shallow** copies: nested lists or dicts would still be shared. The next tasks use only flat lists of strings, so copying the outer list is enough for their changes.

--- code #bash-aliasing-modify
`add_label(labels, extra)` must return a new list containing all the original strings followed by `extra`, leaving its input list unchanged. Fix the assignment that currently shares the input. Empty input is allowed.

Browser: edit the function. Terminal: type the complete corrected function below the starter.
```python
def add_label(labels, extra):
    updated = labels
    updated.append(extra)
    return updated

queued = ["queued"]
empty = []
reviewed = ["reviewed", "signed"]
```
check: add_label(queued, "packed") == ["queued", "packed"] and queued == ["queued"]
check: add_label(empty, "ready") == ["ready"] and empty == []
check: add_label(reviewed, "filed") == ["reviewed", "signed", "filed"] and reviewed == ["reviewed", "signed"]
solution: def add_label(labels, extra):
solution:     updated = labels.copy()
solution:     updated.append(extra)
solution:     return updated
> Copy the list before appending. Each check examines both the returned list and the original input after the call.

--- code #bash-aliasing-check
Write `upper_first(labels)`. Return a new list of strings with only its first string changed to uppercase, leaving the input unchanged. Preserve the other strings and their order. For an empty input, return a new empty list. You can replace an item with `items[0] = value`; use `.upper()` for uppercase text.

Browser: replace the function body. Terminal: type the complete function below the starter.
```python
def upper_first(labels):
    raise NotImplementedError("write upper_first")

river = ["river map", "hill path"]
moon = ["moon chart", "star guide", "sky notes"]
empty = []
```
check: upper_first(river) == ["RIVER MAP", "hill path"] and river == ["river map", "hill path"]
check: upper_first(moon) == ["MOON CHART", "star guide", "sky notes"] and moon == ["moon chart", "star guide", "sky notes"]
check: upper_first(empty) == [] and upper_first(empty) is not empty
solution: def upper_first(labels):
solution:     updated = labels.copy()
solution:     if updated:
solution:         updated[0] = updated[0].upper()
solution:     return updated
> Make the copy first, then replace its first item only when an item exists. The original list keeps every original string. The bridge is complete; continue this lesson or return to the diagnostic.

--- teach #card-f1372a4458d153ad
### A slice is a piece of a list
`xs[a:b]` gives the items from index `a` up to but not including `b`. Leave out `a` to start at the beginning, `b` to go to the end. The result is always a new list; the original is untouched.
```python
>>> tags = [100, 101, 102, 103, 104]
>>> tags[:2]
[100, 101]
>>> tags[2:4]
[102, 103]
>>> tags[3:]
[103, 104]
```
Say "half-open" to yourself: the start is in, the end is out.

--- code #card-b407bc8958ad503a
Set `middle` to the two middle serials, `"C"` and `"D"`, using one slice.
```python
serials = ["A", "B", "C", "D", "E", "F"]
```
check: middle == ["C", "D"]
solution: middle = serials[2:4]
> "C" is at index 2 and "D" at index 3. The slice end is exclusive, so `[2:4]` stops before "E".

--- predict #card-2c738be0e4a35f87
What does this print?
```python
serials = ["A", "B", "C", "D", "E"]
print(serials[1:3])
```
answer: ['B', 'C']|["B", "C"]|['B','C']
> Index 1 is "B" and the slice stops before index 3, so "D" is not included. Two items: positions 1 and 2.

--- teach #card-ace9f6963cb55fa4
### Slices past the end are safe
Asking for more than there is gives you what exists, never an error. That is what makes the last, shorter batch free: `tags[4:8]` on a five-item list is just `[104]`, and `tags[10:]` is `[]`.
```python
>>> tags[4:8]
[104]
>>> tags[10:]
[]
```
Indexing past the end (`tags[10]`) does raise `IndexError`; slicing does not.

--- teach #card-22bf942909fa59a1
### `range` with a step gives batch starts
`range(start, stop, step)` counts from `start` by `step`, stopping before `stop`. `range(0, len(xs), size)` is 0, size, 2·size, ... exactly the first index of each batch.
```python
>>> list(range(0, 5, 2))
[0, 2, 4]
>>> list(range(0, 4, 2))
[0, 2]
```
When the length divides evenly, the last start is the last full batch, so no empty batch appears.

--- predict #card-9bb9b6c81f485192
What does this print?
```python
print(list(range(0, 7, 3)))
```
answer: [0, 3, 6]|[0,3,6]
> Start at 0, add 3 each time, stop before 7. Those are the starts of three batches of size 3 for seven items: [0..2], [3..5], [6].

--- teach #card-66c0aff8edc45be0
### The collect pattern
Start with an empty list and `append` each batch as you build it. Slicing `serials[i:i + size]` from each start gives the batch; each slice is a fresh list, so callers can change a batch without touching your input.
```python
batches = []
for i in range(0, len(serials), size):
    batches.append(serials[i:i + size])
return batches
```
An empty input has `range(0, 0, size)`, which is empty, so you return `[]` without a special case.

--- code #card-56e8d1b2fbd05ef8
Build `batches`: a list of consecutive slices of `serials`, each `size` long, the last one shorter.
```python
serials = ["A", "B", "C", "D", "E", "F", "G"]
size = 3
batches = []
```
check: batches == [["A", "B", "C"], ["D", "E", "F"], ["G"]]
solution: for i in range(0, len(serials), size):
solution:     batches.append(serials[i:i + size])
> `range(0, 7, 3)` gives the starts 0, 3, 6. Each slice takes up to `size` items from there; the last one, `serials[6:9]`, is just `["G"]`.

--- fill #card-abecbc05ebed52af
Complete the slice so each batch holds `size` items starting at `i`.
```python
batches.append(serials[i:___])
```
answer: i + size|i+size
> The end of a slice is exclusive, so `i:i + size` gives exactly `size` items (fewer only at the very end of the list).

--- quiz #card-b2785038a9055d5d
`size` is 0 or negative. What should `chunk_serials` do?
- [ ] Return `[]`
- [x] `raise ValueError("size must be at least 1")`
- [ ] Return the whole list as one batch
> `range(0, n, 0)` itself raises a confusing `ValueError: range() arg 3 must not be zero`, and a negative step silently returns nothing. Check the input up front and raise a clear error, as in Part 1.

--- exercise 2.3 #card-f1e2282f01c454bb

--- recap #card-45b351264e34511e
- `xs[a:b]` is a new list from `a` up to, not including, `b`.
- Slicing past the end gives a shorter list, never an error.
- `range(0, len(xs), size)` is the start of every batch.
- Collect pattern: start with `[]`, `append` as you go.
