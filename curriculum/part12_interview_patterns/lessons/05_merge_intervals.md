# Sort then sweep: merging maintenance windows

--- teach #card-71da3f13771956fd
### The pattern: sort, then walk once
"Three teams filed maintenance windows. What are the combined blackout periods?" The brute force looks for any two overlapping windows, merges them, and starts again until nothing overlaps.
```python
def merge_slow(windows):
    windows = list(windows)
    changed = True
    while changed:
        changed = False
        for a in windows:
            for b in windows:
                if a is not b and a[0] <= b[1] and b[0] <= a[1]:
                    windows.remove(a); windows.remove(b)
                    windows.append((min(a[0], b[0]), max(a[1], b[1])))
                    changed = True
                    break
            if changed:
                break
    return sorted(windows)
```
It compares every pair and may repeat that for every merge. Intervals, bookings, on-call shifts: the pattern is **sort by start, then sweep once**.

--- quiz #card-d5c1f07c35e1577a
What does the sort step cost, and why is it worth it?
- [ ] O(n), and it makes the sweep O(1)
- [x] O(n log n), and afterwards overlaps can only be with the previous merged window
- [ ] O(n²), the same as the brute force
> Sorting is n log n. Once windows are in start order, a window can only overlap the one just before it, so one linear pass finishes the job.

--- teach #card-1eb8471266165d54
### The insight: only look at the last merged window
After sorting, walk the windows and compare each with the *last* entry in the result. If it starts before that entry ends, extend the entry; otherwise start a new one.
```python
merged = []
for start, end in sorted(windows):
    if merged and start <= merged[-1][1]:
        merged[-1] = (merged[-1][0], max(merged[-1][1], end))
    else:
        merged.append((start, end))
return merged
```
`sorted` on a list of tuples orders by the first item, the start, and returns a new list, so the caller's list is untouched.

--- code #card-73d0a5b4348357fa
A new window `(start, end)` arrives in sorted order. If it overlaps or touches `merged[-1]`, extend that entry with `max`; otherwise append it. Then print `merged`.
```python
merged = [(540, 600)]
start, end = 590, 660
```
expect: [(540, 660)]
solution: if merged and start <= merged[-1][1]:
solution:     merged[-1] = (merged[-1][0], max(merged[-1][1], end))
solution: else:
solution:     merged.append((start, end))
solution: print(merged)
> 590 is not past 600, so the windows overlap and the last entry is extended to 660. The start stays 540 because the input is sorted, so the earlier start is always the smaller one.

--- predict #card-2dfce386f4265058
What does this print?
```python
merged = [(0, 100)]
start, end = 10, 20
if start <= merged[-1][1]:
    merged[-1] = (merged[-1][0], max(merged[-1][1], end))
print(merged)
```
answer: [(0, 100)]
> `(10, 20)` sits inside `(0, 100)`. The `max` keeps the end at 100; without it the end would shrink to 20 and the window would be wrong.

--- teach #card-60d36870cb735827
### Two decisions to make out loud before coding
1. Do touching windows merge? `(60, 120)` and `(120, 180)`: here yes, so the test is `start <= previous_end`. With `<` they would stay apart. Ask, then write the answer in a comment.
2. Can the input be unsorted? Here yes, so sort first.

Also decide what bad input does. A window with `start > end` makes no sense; check every window and `raise ValueError` before sorting. A zero-length window `(5, 5)` is fine: it merges into a neighbour it touches or stands alone.

--- code #card-7388a21d0ab959a0
Set `ok` to `True` when every window has `start <= end`, and `False` otherwise.
```python
windows = [(0, 10), (30, 20), (40, 40)]
```
check: ok is False
solution: ok = all(start <= end for start, end in windows)
> `(30, 20)` starts after it ends, so `all` returns `False`. In the exercise this is the check you run before sorting, raising `ValueError` when it fails.

--- fill #card-b4e12d2bd08752c4
Complete the test so touching windows merge as well as overlapping ones.
```python
if merged and start ___ merged[-1][1]:
```
answer: <=
> `<=` treats a window that starts exactly where the last one ends as overlapping. `<` would leave `(60, 120)` and `(120, 180)` separate.

--- quiz #card-8e200c19f9c051ee
Why is `max(merged[-1][1], end)` needed instead of just `end`?
- [ ] Because `end` might be a float
- [x] Because a window fully inside the previous one would otherwise shorten it
- [ ] Because the input is unsorted
> After sorting by start, `(0, 100)` comes before `(10, 20)`. Replacing the end with 20 would cut the merged window short. `max` keeps the further end.

--- teach #card-9bf7780cc0c15c30
### The cost, and how to say it
O(n log n) for the sort, O(n) for the sweep, O(n) space for the new list. The sort dominates.

Say it out loud: "Sort then sweep. Once intervals are ordered by start, each one can only overlap the last merged one, so a single pass with `max` on the end does it. Touching windows merge, and I validate start <= end first."

Test by hand: an empty list gives `[]`; a contained window disappears; unsorted input comes out sorted.

--- exercise 12.5 #card-256cf22f528f5ac8

--- recap #card-9e328533090c50ab
- Interval problems are "sort by start, then sweep once": O(n log n) + O(n).
- Compare each window only with `merged[-1]`; extend it or append a new one.
- `<=` merges touching windows; `max` on the end handles contained windows.
- Validate `start <= end` first; `sorted()` leaves the input list alone.
