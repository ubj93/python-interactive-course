# Runs with groupby

--- teach #card-2e06faa784645197
### The loop version: extend the last run or start a new one
"Runs" are adjacent items with the same status. By hand you keep a list of runs and, for each build, either append to the last run or open a new one.
```python
runs = []
for build_id, status in results:
    if runs and runs[-1][0] == status:
        runs[-1][1].append(build_id)
    else:
        runs.append((status, [build_id]))
```
It works, but the shape is common enough that the standard library has it.

--- teach #card-4b05fe31bc365a52
### `itertools.groupby` groups adjacent equal keys
`groupby(items, key=f)` yields `(key, group)` pairs, one per run of *adjacent* items with the same key. It does not sort first, so `"pass, fail, pass"` gives three groups. That is wrong for "count by category" and exactly right for runs.
```python
>>> from itertools import groupby
>>> [k for k, g in groupby(["pass", "fail", "fail", "pass"])]
['pass', 'fail', 'pass']
```
With no `key`, items are compared directly. Here the key is the status: `lambda r: r[1]`, or `operator.itemgetter(1)`.

--- code #card-879cf14451905594
Set `runs` to a list of `(status, count)` tuples, one per run of adjacent equal statuses, using `groupby`.
```python
from itertools import groupby
statuses = ["pass", "fail", "fail", "pass", "fail"]
```
check: runs == [("pass", 1), ("fail", 2), ("pass", 1), ("fail", 1)]
solution: runs = [(k, len(list(g))) for k, g in groupby(statuses)]
> Each `g` is the run's items; `list(g)` materialises it and `len` counts. The same status that appears again later starts a fresh group, because only adjacent items are grouped.

--- predict #card-0319503c29215634
What does this print?
```python
from itertools import groupby
print([k for k, g in groupby("aabbba")])
```
answer: ['a', 'b', 'a']
> Only adjacent equal characters form a group. The final `a` is not next to the first two, so it starts a new group.

--- teach #card-f663f0b04991580e
### Each group is an iterator: materialise it now
`g` holds the original items of the run, but it is a one-shot iterator that becomes invalid as soon as you move on to the next key. Turn it into a list while you are on it. To keep just the build ids, unpack each `(build_id, status)` pair and drop the status with `_`.
```python
[(status, [build_id for build_id, _ in run])
 for status, run in groupby(results, key=lambda r: r[1])]
```
A comprehension inside a comprehension: the inner one builds each run's ids, the outer one builds the list of runs.

--- quiz #card-3b527deda19d59cc
Why must you consume `g` before advancing to the next `(key, g)` pair?
- [ ] `groupby` raises if a group is left unread
- [x] The group iterator shares the underlying stream and is emptied when groupby moves on
- [ ] Groups are tuples and cannot be iterated twice
> `groupby` reads from one stream. When you ask for the next key, it skips the rest of the current group, so a `g` you saved for later yields nothing.

--- fill #card-aa4eb97b80c753f9
Complete the inner comprehension so it keeps only the build ids from a run of `(build_id, status)` pairs.
```python
ids = [build_id for build_id, ___ in run]
```
answer: _ | status
> Each item is a two-tuple, so it unpacks into two names. `_` is the convention for a value you do not use; naming it `status` works too.

--- teach #card-c4506759271b59f0
### The longest failing run
Filter the runs to the failing ones, then take the longest with `max(..., key=len)`. `max` returns the *first* item among equal keys, which gives the earliest streak on a tie, and `default=[]` covers the case with no failures at all.
```python
failing = [ids for status, ids in group_consecutive(results) if status == "fail"]
return max(failing, key=len, default=[])
```

--- code #card-d6a07cefc08756f8
Set `longest` to the longest list in `runs` (the earliest one on a tie), and `none` to the same thing computed over an empty list, which should give `[]`.
```python
runs = [["b1"], ["b3", "b4"], ["b6", "b7"]]
```
check: longest == ["b3", "b4"]
check: none == []
solution: longest = max(runs, key=len)
solution: none = max([], key=len, default=[])
> `key=len` compares lists by length and `max` keeps the first of the two that tie, so the earlier `["b3", "b4"]` wins. Without `default`, `max([])` raises `ValueError`.

--- exercise 9.6 #card-1aa68814683457f8

--- recap #card-6135b45959ff5db7
- `groupby` groups adjacent equal keys only; that is what "runs" means.
- Pass `key=lambda r: r[1]` to group on a field; `_` discards the unused half of a pair.
- Materialise each group with a list before moving to the next.
- `max(runs, key=len, default=[])` picks the longest, earliest on ties.
