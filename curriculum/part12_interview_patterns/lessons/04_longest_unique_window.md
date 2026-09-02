# The sliding-window pattern

--- teach
### The pattern: a window that only moves forward
"What is the longest stretch of consecutive check-ins with no host repeated?" The brute force restarts from every position and extends until a repeat.
```python
def longest_unique_slow(hosts):
    best = 0
    for start in range(len(hosts)):
        seen = set()
        for item in hosts[start:]:
            if item in seen:
                break
            seen.add(item)
        best = max(best, len(seen))
    return best
```
Correct, and worth saying first: "Try every start, extend until a repeat: O(n squared)." The waste is that each restart re-scans hosts the previous pass already checked.

--- quiz
The log has 20,500 entries and the answer is 2,500. Roughly what does the brute force cost?
- [x] O(n²): each of n starts can scan thousands of entries
- [ ] O(n): every host is looked at once
- [ ] O(n log n): the set sorts its contents
> Every start position scans forward until a repeat, up to 2,500 entries, and there are 20,500 starts. That is tens of millions of steps: seconds, not milliseconds.

--- teach
### The insight: two edges that never go backwards
Keep a window `[start, i]` with no repeats inside it. Move `i` forward one step at a time. When the new item was already seen *inside the window*, jump `start` to just past that earlier copy. A dict of each item's last position tells you where.
```python
last_seen = {}
start = best = 0
for i, item in enumerate(hosts):
    if item in last_seen and last_seen[item] >= start:
        start = last_seen[item] + 1
    last_seen[item] = i
    best = max(best, i - start + 1)
```
Both edges only ever move right, so every index enters the window once and leaves once.

--- code
Item `b` arrives at index 3 and was last seen inside the window. Move `start` just past that earlier copy, record the new position of `b`, then print `start`.
```python
last_seen = {"a": 0, "b": 1, "c": 2}
start = 0
i, item = 3, "b"
```
expect: 2
check: last_seen["b"] == 3
solution: if item in last_seen and last_seen[item] >= start:
solution:     start = last_seen[item] + 1
solution: last_seen[item] = i
solution: print(start)
> `b` was at index 1, inside the window, so `start` jumps to 2 and the window becomes `[2, 3]`. Then the dict is updated so the next `b` measures from here.

--- predict
What does this print?
```python
last_seen = {"a": 0, "b": 1}
start = 0
i, item = 2, "a"
if item in last_seen and last_seen[item] >= start:
    start = last_seen[item] + 1
print(start, i - start + 1)
```
answer: 1 2
> `a` was last seen at index 0, which is inside the window, so `start` jumps to 1. The window is now `[1, 2]`, two items long.

--- teach
### The guard that everyone forgets
Why `last_seen[item] >= start` and not just `item in last_seen`? Take `"abbac"`. At index 3 the second `a` arrives; `last_seen["a"]` is 0, but `start` already moved to 2 because of the double `b`. Without the guard, `start` would jump *back* to 1, the window would be `"bba"`, and the function would report 4 when the true answer is 3.

A repeat that is already outside the window must not move `start`. Say the invariant before you code: "`start` is the first index of the current window, and it never decreases."

--- code
Now the repeat is *outside* the window. Apply the same guarded update, record the item, and print `start`. It must not move.
```python
last_seen = {"a": 0, "b": 2}
start = 2
i, item = 3, "a"
```
expect: 2
check: last_seen["a"] == 3
solution: if item in last_seen and last_seen[item] >= start:
solution:     start = last_seen[item] + 1
solution: last_seen[item] = i
solution: print(start)
> `a` was last seen at 0, but `start` is already 2, so the guard is false and `start` stays. Without the `>= start` test it would drop back to 1. This is the `"abbac"` bug in two lines.

--- quiz
Which input catches a solution that drops the `>= start` guard?
- [ ] `"abcabc"`: it returns 3 either way
- [x] `"abbac"`: it returns 4 instead of 3
- [ ] `"aaaa"`: it returns 1 either way
> In `"abbac"` the old `a` at index 0 is already outside the window when the second `a` arrives. Without the guard, `start` moves backwards and a window containing two `b`s is counted.

--- fill
Complete the update so `best` tracks the longest window so far.
```python
best = max(best, i - start ___ 1)
```
answer: +
> The window `[start, i]` includes both ends, so its length is `i - start + 1`. Forgetting the `+ 1` is the off-by-one that makes a single element count as 0.

--- teach
### The cost, and how to say it
One pass, and each index enters and leaves the window once: O(n) time. The dict holds one entry per distinct host: O(d) space.

Say it out loud: "Sliding window with a last-seen dict. The right edge advances every step; the left edge only jumps forward past a duplicate. Both are monotone, so it is linear."

Edge cases: an empty sequence gives 0, a single element gives 1, and the function must accept any sequence of hashable items, so a string of characters works too.

--- exercise 12.4

--- recap
- "Longest run where ..." over a sequence is the sliding-window pattern.
- Keep `[start, i]`; grow the right edge, jump the left edge just past a repeat.
- `last_seen[item] >= start` ignores repeats already outside the window (`"abbac"` is 3).
- Both edges move forward only: O(n) time, O(d) space.
