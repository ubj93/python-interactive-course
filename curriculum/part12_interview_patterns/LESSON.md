# Part 12 · Interview patterns

> **What you will be able to do:** recognise the ten shapes that almost every CPE
> coding question reduces to, say their cost out loud, and code the standard answer
> from memory in a few minutes. This part is drill, not new language: everything
> here is built from dicts, lists, sorting and recursion you already know. Budget two
> to three hours across a few sittings, and come back to it the week before an
> on-site.

## Why a pattern chapter

A CPE interviewer is not testing whether you know the name "Kahn's algorithm". They
are testing whether, given "these packages depend on each other, in what order do I
install them?", you reach for the right data structure without flailing. Almost every
question maps to one of a small set of patterns. Learn to spot the pattern in the
first minute, and the rest of the interview is typing.

The patterns, and the fleet problem each one hides behind:

| Pattern | Sounds like |
|---|---|
| Hash map | "find the pair", "have I seen this before", "group by" |
| Stack | "matching", "nested", "most recent open thing" |
| Two pointers | "sorted input, compare from both ends" |
| Sliding window | "longest run of log lines where ...", "last N events" |
| Sort then sweep | "merge the maintenance windows", "overlapping bookings" |
| Counter + heap | "top 10 offenders", "most common error" |
| Binary search | "which build broke it", "smallest version that ..." |
| Recursion | "folder sizes", "nested config", "tree of dependencies" |
| Graph search | "install order", "who is reachable", "detect the cycle" |
| LRU cache | "keep the last N lookups", "bounded memoisation" |

## 1. Big-O in plain words

Big-O is a rough count of how the work grows with the input. You need five shapes and
the vocabulary to say them:

| Notation | Say | Feels like |
|---|---|---|
| O(1) | constant | a dict lookup; does not care how big the dict is |
| O(log n) | logarithmic | halving: 1,000,000 items in ~20 steps |
| O(n) | linear | one pass over the list |
| O(n log n) | "n log n" | sorting |
| O(n²) | quadratic | a loop inside a loop; 20,000 items = 200,000,000 steps |

The rule of thumb that matters in Python: **about 10 million simple operations per
second.** So O(n²) with n = 20,000 is a few seconds; with n = 200,000 it is a coffee
break. O(n log n) with n = 200,000 is instant.

Costs of the operations you actually use:

| Operation | Cost | Note |
|---|---|---|
| `lst[i]`, `lst.append(x)`, `lst.pop()` | O(1) | pop from the *end* |
| `lst.pop(0)`, `lst.insert(0, x)` | O(n) | shifts everything; use `collections.deque` |
| `x in lst`, `lst.index(x)` | O(n) | scans; this is the hidden quadratic in most slow code |
| `x in a_set`, `a_set.add(x)` | O(1) | average; hashing |
| `d[k]`, `d.get(k)`, `d[k] = v`, `k in d` | O(1) | average; hashing |
| `sorted(lst)`, `lst.sort()` | O(n log n) | Timsort; already-sorted input is O(n) |
| `min(lst)`, `max(lst)`, `sum(lst)` | O(n) | one pass each; three calls = three passes |
| `heapq.heappush` / `heappop` | O(log n) | `nlargest(k, ...)` is O(n log k) |
| `"".join(parts)` | O(total length) | `s += piece` in a loop is O(n²) in principle |
| slicing `lst[a:b]` | O(b − a) | copies; `for x in lst[1:]` copies the whole list |

**Gotcha:** `x in lst` inside a `for` loop over the same list is O(n²). It is the
single most common reason a candidate's "linear" solution times out. If you write
`in` on a list, ask yourself whether it should be a set.

**Gotcha:** space counts too. "O(n) extra space" means you built a dict or list as big
as the input. Say it out loud; interviewers notice when you do not.

## 2. The hash-map pattern

*"Find two cached packages whose sizes add up exactly to the free space."*

The brute force compares every pair: O(n²). The pattern: **remember what you have
seen, in a dict, and look up what you need.**

```python
def two_sum(sizes, target):
    seen = {}                      # value -> index of its first occurrence
    for j, size in enumerate(sizes):
        need = target - size
        if need in seen:           # O(1) instead of scanning the list
            return (seen[need], j)
        seen.setdefault(size, j)   # keep the earliest index
    return None
```

One pass, O(n) time, O(n) space. Note the order inside the loop: *check first, then
store.* Storing first would let a value pair with itself.

The same idea, with a **canonical key**, groups things: anagrams share
`"".join(sorted(word))`, devices share `os_family(os_string)`, files share a checksum.

```python
>>> groups = {}
>>> for name in ["listen", "silent", "enlist", "google"]:
...     groups.setdefault("".join(sorted(name)), []).append(name)
>>> list(groups.values())
[['listen', 'silent', 'enlist'], ['google']]
```

`dict.setdefault(key, [])` or `collections.defaultdict(list)`: either is fine; say which
you are using and why (defaultdict creates keys on *read*, which surprises people).

## 3. Stack: the most recent open thing

*"Is this shell one-liner's bracket nesting valid?"*

A stack is a list you only `append` to and `pop` from the end. Use it whenever the
rule is "the most recently opened thing must be closed first".

```python
PAIRS = {")": "(", "]": "[", "}": "{"}

def balanced_brackets(text):
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in PAIRS:
            if not stack or stack.pop() != PAIRS[ch]:
                return False
    return not stack           # leftovers mean something was never closed
```

Three things to test out loud: a closer with nothing open (`")("`), the wrong kind of
closer (`"([)]"`), and leftovers at the end (`"(("`). Candidates who forget the last
`return not stack` pass most examples and fail the interview.

## 4. Two pointers

*"Given two sorted lists of serial numbers, which are in both?"*

When the inputs are **sorted**, two indexes walking towards each other or in step
replace a nested loop:

```python
def common_sorted(a, b):
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            out.append(a[i]); i += 1; j += 1
        elif a[i] < b[j]:
            i += 1
        else:
            j += 1
    return out
```

O(len(a) + len(b)). If the inputs are *not* sorted, sorting first costs O(n log n),
which is still far better than O(n²) — but a set intersection (`set(a) & set(b)`) is
O(n) and one line. Say that: "if order does not matter I would use sets; two pointers
is for when I must keep the sorted order or cannot afford the extra memory."

## 5. Sliding window

*"What is the longest stretch of consecutive check-ins from all-different hosts?"*

A window is a pair of indexes `[start, i]` that only ever move forward. Grow the right
edge one step at a time; when the window breaks a rule, move the left edge just far
enough to fix it. Every index enters and leaves once, so the total is O(n).

```python
def longest_unique_window(items):
    last_seen = {}          # item -> most recent index
    start = best = 0
    for i, item in enumerate(items):
        if item in last_seen and last_seen[item] >= start:
            start = last_seen[item] + 1        # jump past the earlier copy
        last_seen[item] = i
        best = max(best, i - start + 1)
    return best
```

**Gotcha:** the `last_seen[item] >= start` guard. Without it a repeat that is already
*outside* the window drags `start` backwards and the window grows past a duplicate.
`"abbac"` is the smallest input that catches it.

A fixed-size window (last 60 seconds of events, the last N samples) is
`collections.deque(maxlen=N)` — Part 10 covered it.

## 6. Sort then sweep

*"Three teams filed maintenance windows. What are the combined blackout periods?"*

Intervals, bookings, on-call shifts: sort by start, then walk once, carrying the
current merged interval and extending it while the next one overlaps.

```python
def merge_intervals(windows):
    merged = []
    for start, end in sorted(windows):
        if merged and start <= merged[-1][1]:            # overlaps or touches
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged
```

O(n log n) for the sort, O(n) for the sweep. Two decisions to make explicit before you
code: do touching intervals (`(1, 5)` and `(5, 8)`) merge, and is the input allowed to
be unsorted? Ask; then write the answer in a comment.

`max(...)` on the end matters: `(1, 10)` followed by `(2, 3)` must stay `(1, 10)`.

## 7. Counting and top-k

*"Which ten error messages dominate the last hour of logs?"*

```python
>>> from collections import Counter
>>> import heapq
>>> counts = Counter(words)
>>> counts.most_common(3)                        # ties in insertion order, not alphabetical
>>> heapq.nsmallest(3, counts.items(), key=lambda kv: (-kv[1], kv[0]))   # ties A-Z
```

`Counter` is a dict subclass; `most_common(k)` is O(n log k). When the spec says "ties
broken alphabetically", `most_common` is not enough: sort or heap on the tuple
`(-count, word)` so that bigger counts come first and equal counts fall back to the
word. Say the cost: O(n) to count, O(d log k) to pick the top k of d distinct words.

## 8. Binary search: bisecting a broken build

*"Build 1 is good, build 5,000 is bad, and each build takes ten minutes to test.
Find the first bad one."*

If the answer is *monotone* — good, good, good, bad, bad, bad — you can halve the
range with every check. 5,000 builds take 13 checks, not 5,000.

```python
def bisect_first_bad(n_builds, is_bad):
    lo, hi = 1, n_builds
    while lo < hi:
        mid = (lo + hi) // 2
        if is_bad(mid):
            hi = mid              # mid could be the answer; keep it
        else:
            lo = mid + 1          # mid is good; answer is strictly after it
    return lo
```

Three habits that separate a correct binary search from a nearly-correct one:

- Decide what `lo` and `hi` *mean* before you write the loop ("the answer is in
  `[lo, hi]`"), and keep that true at every step.
- `hi = mid`, not `mid - 1`, when `mid` might itself be the answer.
- Test on n = 1 and n = 2 by hand. Off-by-one errors live there.

The stdlib `bisect` module does this over a sorted list (`bisect_left`,
`bisect_right`), but an interviewer wants to see you drive the loop yourself when
the "list" is a predicate that is expensive to call.

## 9. Recursion vs iteration

*"Given a folder tree, report the total size of every folder."*

A tree of nested dicts is the natural home for recursion: the size of a folder is the
sum of its files plus the sizes of its subfolders.

```python
def dir_sizes(tree, path="/", out=None):
    out = {} if out is None else out
    total = 0
    for name, node in tree.items():
        if isinstance(node, dict):
            child = path.rstrip("/") + "/" + name
            dir_sizes(node, child, out)
            total += out[child]
        else:
            total += node
    out[path] = total
    return out
```

Every node is visited once: O(number of files and folders). Recursion is the clearest
way to write it. Two things an interviewer may probe:

- **Depth.** CPython's default recursion limit is 1,000 frames. A file system nested
  a thousand deep is unusual; a linked structure of 100,000 nodes is not. Know the
  iterative rewrite: an explicit stack of `(node, path)` pairs, processed in post-order
  so children are summed before parents.
- **Mutable default arguments.** `out={}` in the signature is a shared dict across
  calls; `out=None` and create inside. Interviewers love this one.

## 10. Graphs: BFS, DFS and topological sort

*"Package A needs B and C, C needs B, and D needs A. In what order do I install?"*

A graph is a dict of adjacency: `{"A": ["B", "C"], "C": ["B"], "D": ["A"]}`. Two
searches cover almost every question:

- **BFS** (breadth-first) uses a `deque`; visits by distance; answers "shortest path"
  and "what is reachable".
- **DFS** (depth-first) uses recursion or an explicit stack; answers "is there a
  cycle" and produces orderings.

```python
from collections import deque

def reachable(graph, start):
    seen = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for nxt in graph.get(node, []):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen
```

Mark nodes seen **when you enqueue them**, not when you pop them; otherwise the same
node enters the queue many times.

**Topological sort** orders a dependency graph so every package comes after the things
it needs. Kahn's algorithm: count incoming edges, repeatedly take a node with zero
remaining, and decrement its dependants. A heap instead of a plain queue gives a
deterministic (alphabetical) order among the ready nodes. If nodes are left over at
the end, there is a cycle — and a good answer *names* the cycle rather than just
raising.

```python
import heapq

def install_order(deps):
    nodes = set(deps) | {d for ds in deps.values() for d in ds}
    remaining = {n: set(deps.get(n, [])) for n in nodes}
    dependants = {n: set() for n in nodes}
    for n, ds in remaining.items():
        for d in ds:
            dependants[d].add(n)
    ready = [n for n in nodes if not remaining[n]]
    heapq.heapify(ready)
    order = []
    while ready:
        n = heapq.heappop(ready)
        order.append(n)
        for m in dependants[n]:
            remaining[m].discard(n)
            if not remaining[m]:
                heapq.heappush(ready, m)
    if len(order) != len(nodes):
        raise ValueError("dependency cycle among: " + ", ".join(sorted(nodes - set(order))))
    return order
```

O(V + E) with a queue; O(V log V + E) with a heap. To find the *exact* cycle, run a DFS
with three colours (unvisited, in progress, done): meeting an in-progress node means
you have walked in a loop, and the recursion path from that node back to itself is
the cycle.

## 11. LRU cache

*"Cache the last 1,000 device lookups; evict the one used longest ago."*

The trick is that both `get` and `put` must be O(1), which rules out searching a
list. Python dicts remember insertion order, and `OrderedDict` adds `move_to_end` and
`popitem(last=False)`:

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self._data = OrderedDict()

    def get(self, key):
        if key not in self._data:
            return None
        self._data.move_to_end(key)          # now most recently used
        return self._data[key]

    def put(self, key, value):
        self._data[key] = value
        self._data.move_to_end(key)
        if len(self._data) > self.capacity:
            self._data.popitem(last=False)   # evict the least recently used
```

With a plain dict: `del d[key]; d[key] = value` moves a key to the end, and
`next(iter(d))` is the oldest key. Both work; `OrderedDict` reads better and says
"I know the standard library". `functools.lru_cache` is the decorator form for pure
functions — mention it, then explain why an interviewer still wants the class.

## 12. How to run a 45-minute interview

The question is usually solvable in 15 minutes of typing. The other 30 are where the
hiring decision happens. A script that works:

1. **Restate** the problem in one sentence, in your words. "So: given a list of
   package sizes, find two that add to the target."
2. **Clarify** before coding. Sorted? Duplicates? Empty input? What do I return when
   there is no answer — `None`, an empty list, an exception? How big is n? Write the
   answers as comments at the top.
3. **Brute force first, out loud.** "Nested loop over pairs, O(n²). That works; let me
   see if I can do better." You have now demonstrated a correct baseline and shown you
   know what "better" means.
4. **Name the pattern and its cost.** "This is a hash-map lookup; O(n) time and O(n)
   extra space." Then code that one.
5. **Talk while coding.** Narrate decisions, not keystrokes: "I check before I store so
   an element can't pair with itself."
6. **Test with the tiniest cases.** Empty input. One element. Two elements that match.
   Two that do not. The example from the question. Walk through them by hand, index by
   index, before you claim it works.
7. **Then improve.** Only after it is correct: tidy names, drop a redundant check,
   mention what you would do with 10 million items or with the input arriving as a
   stream.

Silence is the enemy. If you are stuck, say what you are stuck on ("I'm not sure
whether touching intervals should merge") — the interviewer will usually answer, and
you have turned a stall into a clarification.

## Interview notes for this part

- **Say the cost of every data structure operation you use.** "`in` on a set is
  O(1); on a list it would be O(n) and make this quadratic."
- **Ask about size.** n = 100 and n = 10,000,000 have different right answers, and
  asking shows you know that.
- **Write the invariant before the loop.** "The answer is in `[lo, hi]`." "`stack` holds
  the brackets that are still open." "`start` is the first index of the current
  window." Most bugs in these patterns are broken invariants.
- **The trap:** optimising before it works. A correct O(n²) beats a broken O(n). Get
  green, then get fast.
- **The other trap:** hand-rolling what the stdlib does. `Counter`, `heapq`, `deque`,
  `OrderedDict`, `bisect`, `sorted(key=...)` are expected knowledge, not cheating.

## Exercises

Run `course list 12`, then `course show 12.1`. Each exercise carries a "Complexity
target" line; the last test in every file is large enough that the wrong approach is
noticeably slow, so watch the run time as well as the colour.

1. `two_sum` · the hash-map pattern: check first, then store
2. `balanced_brackets` · a stack for "most recently opened"
3. `anagram_groups` · grouping by a canonical key
4. `longest_unique_window` · sliding window with a last-seen dict
5. `merge_intervals` · sort then sweep over maintenance windows
6. `word_frequency_top_k` · Counter plus a heap with alphabetical ties
7. `bisect_first_bad` · binary search over an expensive predicate
8. `dir_sizes` · recursion over a nested tree, with the iterative rewrite
9. `install_order` · topological sort of packages, naming the cycle
10. `LRUCache` · O(1) get/put with `OrderedDict`
