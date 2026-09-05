# Binary search: the first bad build

--- teach #card-b38b3ab013205222
### The pattern: halve a monotone range
"Build 1 works, build 5,000 is broken, each test takes ten minutes. Which build broke it?" The brute force tests builds in order until one fails.
```python
def first_bad_slow(n_builds, is_bad):
    for build in range(1, n_builds + 1):
        if is_bad(build):
            return build
    return None
```
That is O(n) calls to `is_bad`: up to 5,000 lab installs. The property that saves you is that the answers are **monotone**: good, good, good, bad, bad, bad. Once a build is bad, every later one is bad. Whenever a yes/no answer flips exactly once along a range, the pattern is **binary search**.

--- quiz #card-e32e9f865dca5128
With halving, roughly how many `is_bad` calls does it take to find the first bad build among 1,000?
- [x] About 10
- [ ] About 100
- [ ] About 500
> Each call halves the range: 1000, 500, 250, 125, 63, 32, 16, 8, 4, 2, 1. That is about log2(1000), ten steps. A billion builds take about thirty.

--- teach #card-95ea28a49d775106
### The insight: keep the answer inside `[lo, hi]`
Write the invariant before the loop: "the first bad build is somewhere in `[lo, hi]`." Test the middle. If it is bad, the answer is `mid` or earlier, so `hi = mid`. If it is good, the answer is strictly later, so `lo = mid + 1`. Stop when the range is one build wide.
```python
lo, hi = 1, n_builds
while lo < hi:
    mid = (lo + hi) // 2
    if is_bad(mid):
        hi = mid              # mid might be the answer; keep it
    else:
        lo = mid + 1          # mid is good; the answer is after it
```
When the loop ends `lo == hi`, and that is the first bad build, if any build is bad at all.

--- code #card-67837ae5401655c9
Write the halving loop: while `lo < hi`, test the middle build; a bad one keeps `hi = mid`, a good one moves `lo = mid + 1`. Then print `lo`.
```python
def is_bad(build):
    return build >= 6
lo, hi = 1, 8
```
expect: 6
solution: while lo < hi:
solution:     mid = (lo + hi) // 2
solution:     if is_bad(mid):
solution:         hi = mid
solution:     else:
solution:         lo = mid + 1
solution: print(lo)
> The range goes `[1, 8]`, mid 4 good, `[5, 8]`, mid 6 bad, `[5, 6]`, mid 5 good, `[6, 6]`. Three calls instead of six, and `lo` lands on the first bad build.

--- predict #card-fc9fe4394fe65463
What does this print?
```python
lo, hi = 1, 5
mid = (lo + hi) // 2
print(mid)
```
answer: 3
> `(1 + 5) // 2` is 3, the middle build. `//` keeps the whole part, so the middle of `[1, 4]` would be 2, never a fraction.

--- teach #card-01ed311467f9533b
### The two ends: nothing bad, and nothing at all
If no build is bad, the loop still narrows to `lo == n_builds` without ever testing it, because the last good `mid` pushed `lo` past everything. So after the loop, call `is_bad(lo)` one final time and return `None` when it is good. That final call is the `+ 1` in the budget of `ceil(log2(n)) + 1` calls.

`n_builds == 0` has no builds to test: return `None` before touching the predicate. And never call `is_bad` outside `1..n_builds`; the tests raise if you do.

--- fill #card-71105478aa1250c9
Complete the branch that keeps a bad `mid` inside the range.
```python
if is_bad(mid):
    hi = ___
else:
    lo = mid + 1
```
answer: mid
> A bad `mid` might itself be the first bad build, so it must stay in `[lo, hi]`. `hi = mid - 1` would throw the answer away and the loop could return a good build.

--- quiz #card-563b1e2dc3fa51c0
Why is it `lo = mid + 1` but `hi = mid`, not symmetric?
- [ ] Because `//` rounds down
- [x] Because a good `mid` cannot be the answer, but a bad `mid` can
- [ ] Because builds are numbered from 1
> Good means the first bad build is strictly after `mid`, so `mid` can be excluded. Bad means `mid` may be the answer, so it stays. Test n = 1 and n = 2 by hand; off-by-one errors live there.

--- teach #card-fe46c349864856a1
### The cost, and how to say it
O(log n) calls to the predicate, O(1) space. With the final check it is at most `ceil(log2(n)) + 1` calls: 11 for a thousand builds, 31 for a billion.

Say it out loud: "The predicate is monotone, so this is binary search. My invariant is that the answer is in `[lo, hi]`; a bad mid keeps `hi = mid`, a good mid moves `lo = mid + 1`, and I test the survivor once at the end to tell 'last build' from 'nothing bad'."

The stdlib `bisect` module does this over a sorted list, but here the "list" is an expensive function, so you drive the loop yourself.

--- code #card-2ff5ce384df3524f
`results[i]` is whether build `i + 1` is bad. Use `bisect.bisect_left` to find the index of the first `True`, add 1 to turn it into a build number, and print it.
```python
import bisect
results = [False, False, False, True, True]
```
expect: 4
solution: print(bisect.bisect_left(results, True) + 1)
> `False < True`, so the list is sorted and `bisect_left` finds the first position where `True` fits: index 3, build 4. Use the module when the data is a list; drive the loop yourself when each answer costs a lab install.

--- exercise 12.7 #card-65b41c5166ee52bc

--- recap #card-f5b0b06f02215188
- A yes/no answer that flips once along a range means binary search: O(log n).
- Say the invariant first: "the answer is in `[lo, hi]`", then keep it true.
- `hi = mid` when mid could be the answer; `lo = mid + 1` when it cannot.
- One final `is_bad(lo)` separates "all good" from "last build bad"; n = 0 returns `None` first.
