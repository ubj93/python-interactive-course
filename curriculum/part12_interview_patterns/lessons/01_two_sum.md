# The hash-map pattern: two sum

--- teach
### Name the pattern before you code
"Find two package sizes that add up to the free space." The obvious answer is the brute force: try every pair.
```python
def two_sum_slow(sizes, target):
    for i in range(len(sizes)):
        for j in range(i + 1, len(sizes)):
            if sizes[i] + sizes[j] == target:
                return (i, j)
    return None
```
It is correct, and in an interview you should say it first: "Nested loop over pairs, O(n squared). Let me see if I can do better." A correct slow answer is a baseline; a broken fast one is nothing.

--- quiz
The staging volume holds 20,000 packages. Roughly how many pair checks does the nested loop make in the worst case?
- [ ] About 20,000
- [ ] About 400,000
- [x] About 200,000,000
> Every element is compared with every later one: n * n / 2, so 20,000 * 20,000 / 2. Python does roughly ten million simple steps a second, so that is a few seconds. That is what O(n²), "quadratic", feels like.

--- teach
### The insight: remember what you have seen
The inner loop is a search: "is there an earlier value equal to `target - size`?" A dict answers that in O(1). So walk the list once, and for each size ask the dict for its partner, then store the size.
```python
def two_sum(sizes, target):
    seen = {}                     # value -> index where it first appeared
    for j, size in enumerate(sizes):
        need = target - size
        if need in seen:
            return (seen[need], j)
        seen.setdefault(size, j)
    return None
```
`in` on a dict is a hash lookup; `in` on a list would scan and bring the quadratic back.

--- code
Walk `sizes` with `enumerate`. For each size compute `need`; if it is already in `seen`, print the pair `(seen[need], j)`; otherwise store the size's index in `seen`.
```python
sizes = [3, 5, 7]
target = 10
seen = {}
```
expect: (0, 2)
check: seen[3] == 0 and seen[5] == 1
solution: for j, size in enumerate(sizes):
solution:     need = target - size
solution:     if need in seen:
solution:         print((seen[need], j))
solution:     else:
solution:         seen[size] = j
> 3 and 5 are stored under their indexes. At index 2 the size is 7, which needs 3, and 3 is in `seen` at index 0, so the pair is `(0, 2)`.

--- predict
What does this print?
```python
seen = {}
for j, size in enumerate([120, 40, 75, 60]):
    need = 100 - size
    if need in seen:
        print((seen[need], j))
        break
    seen[size] = j
```
answer: (1, 3)
> At index 3 the size is 60 and it needs 40. 40 was stored at index 1, so the pair is `(1, 3)`. Sizes 120 and 75 were stored but never matched.

--- teach
### Check first, then store
The order inside the loop matters. If you store the current size before checking, `[5]` with target 10 would find itself: `need` is 5, and 5 is already in the dict at the same index. Checking first means the dict only ever holds *earlier* indexes, so `i < j` comes for free.

`seen.setdefault(size, j)` stores only if the key is new, which keeps the earliest index. With `[4, 4]` and target 8, index 1 needs 4 and finds index 0, giving `(0, 1)`.

--- code
Store each size's *earliest* index in `seen` using `setdefault`, then print `seen`.
```python
sizes = [4, 1, 4]
seen = {}
```
expect: {4: 0, 1: 1}
solution: for j, size in enumerate(sizes):
solution:     seen.setdefault(size, j)
solution: print(seen)
> `setdefault(4, 2)` sees that 4 is already stored and leaves index 0 in place. A plain `seen[size] = j` would overwrite it with 2 and lose the earliest index.

--- fill
Complete the lookup so it finds the partner of the current size.
```python
need = target - size
if need ___ seen:
    return (seen[need], j)
```
answer: in
> `need in seen` asks the dict whether the partner was seen earlier, in O(1). `seen[need]` then gives its index.

--- quiz
A candidate writes `seen[size] = j` *before* the `if need in seen` check. What goes wrong?
- [x] `two_sum([5, 3], 10)` returns `(0, 0)` instead of `None`
- [ ] Nothing; the order does not matter
- [ ] The dict raises `KeyError` on the first size
> After storing 5 at index 0, the check finds 5 (its own entry) and pairs it with itself. Check before you store, so the dict holds only earlier indexes.

--- teach
### State the cost, then code it
One pass over the list, one dict as big as the input: O(n) time and O(n) extra space. Say it out loud: "This is the hash-map pattern: I trade O(n) memory for O(1) lookups, so the whole thing is one linear pass."

Then test the tiny cases by hand before you claim it works: an empty list, a single element, `[4, 4]` with target 8, and `[5, 3]` with target 10. Return a tuple, and `None` when nothing pairs.

--- exercise 12.1

--- recap
- Say the brute force first: nested loop over pairs, O(n²).
- Hash-map pattern: store what you have seen in a dict, look up what you need in O(1).
- Check before you store, so a value cannot pair with itself.
- `setdefault` keeps the earliest index; the result is O(n) time, O(n) space.
