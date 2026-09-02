# Part 2 · Loops and lists

> **What you will be able to do:** walk through a collection of devices, records, or
> samples, keep a running answer as you go, and slice, sort, and de-duplicate lists
> without reaching for a hand-rolled index loop. Budget about ninety minutes including
> the exercises.

## Why this part matters

Almost every CPE script is "for each device in the fleet, do something and remember
the result." The MDM gives you a list, osquery gives you a list of rows, a log file is
a list of lines. This part is about the list itself and the loop that walks it. If
Part 1 was *a value in, a value out*, Part 2 is *many values in, one answer out*.

## 1. Lists

A list is an ordered, mutable sequence. It can hold anything, but keep one type per
list: a list of strings, a list of ints, a list of dicts.

```python
>>> hosts = ["mbp-j-doe", "win-lab-01", "mbp-a-kim"]
>>> hosts[0]              # 'mbp-j-doe'
>>> hosts[-1]             # 'mbp-a-kim'
>>> len(hosts)            # 3
>>> hosts.append("nuc-01")
>>> hosts                 # ['mbp-j-doe', 'win-lab-01', 'mbp-a-kim', 'nuc-01']
>>> "nuc-01" in hosts     # True
```

### Methods that change the list in place

| Method | Effect | Returns |
|---|---|---|
| `append(x)` | add one item at the end | `None` |
| `extend(xs)` | add every item of `xs` | `None` |
| `insert(i, x)` | put `x` at index `i` | `None` |
| `pop()` / `pop(i)` | remove and return the last (or i-th) item | the item |
| `remove(x)` | remove the first `x`, `ValueError` if absent | `None` |
| `sort()` | sort in place | `None` |
| `reverse()` | reverse in place | `None` |
| `clear()` | empty the list | `None` |

**Gotcha:** in-place methods return `None`. `hosts = hosts.sort()` throws your list
away. Interviewers see this one weekly. Use `sorted(hosts)` when you want a new list.

### Methods and functions that leave the list alone

| Call | Example | Result |
|---|---|---|
| `sorted(xs)` | `sorted([3, 1, 2])` | `[1, 2, 3]` (new list) |
| `reversed(xs)` | `list(reversed([1, 2]))` | `[2, 1]` |
| `xs.index(x)` | `["a", "b"].index("b")` | `1` (`ValueError` if absent) |
| `xs.count(x)` | `[1, 1, 2].count(1)` | `2` |
| `sum` / `min` / `max` | `max([3, 9, 1])` | `9` |
| `len` | `len([])` | `0` |
| `xs + ys` | `[1] + [2, 3]` | `[1, 2, 3]` (new list) |

### Aliasing

```python
>>> a = [1, 2, 3]
>>> b = a              # b is another name for the SAME list
>>> b.append(4)
>>> a                  # [1, 2, 3, 4]   surprise, if you expected a copy
>>> c = a[:]           # a shallow copy; list(a) and a.copy() do the same
```

Assignment never copies. If you want a copy, ask for one. The same applies to lists
you receive as function arguments: mutate them only if the caller expects it.

## 2. The for loop

Python's `for` walks the items of anything iterable. You almost never need an index.

```python
>>> for host in hosts:
...     print(host.upper())
```

The non-idiomatic version you will see in interviews:

```python
for i in range(len(hosts)):      # C-style, avoid unless you need i AND you can't enumerate
    print(hosts[i].upper())
```

It works, but it says "I think in indexes" and it breaks the moment `hosts` is a
generator or a set. When you *do* need the index, use `enumerate`:

```python
>>> for i, host in enumerate(hosts, start=1):
...     print(f"{i}. {host}")
1. mbp-j-doe
2. win-lab-01
```

### range

```python
>>> list(range(5))          # [0, 1, 2, 3, 4]         stop is exclusive
>>> list(range(2, 5))       # [2, 3, 4]
>>> list(range(0, 10, 3))   # [0, 3, 6, 9]            step
>>> list(range(10, 0, -3))  # [10, 7, 4, 1]           negative step counts down
```

`range(0, len(xs), size)` gives you the start of every batch of `size` items; you
will use it in `chunk_serials`.

### zip: walk two lists together

```python
>>> names = ["mbp-j-doe", "win-lab-01"]
>>> cpu = [12.5, 87.0]
>>> for name, load in zip(names, cpu):
...     print(f"{name}: {load}%")
```

`zip` stops at the shortest input silently. `zip(xs, xs[1:])` pairs each item with
its neighbour, which is how you find gaps between consecutive asset tags.

### break, continue, else

```python
for line in lines:
    if not line.strip():
        continue                 # skip this one, go to the next
    if line.startswith("END"):
        break                    # leave the loop entirely
else:
    print("no END marker")       # runs only if the loop was NOT broken out of
```

`for ... else` is rare and confuses readers; a flag variable or a helper function
that `return`s is clearer in an interview.

## 3. The while loop

Use `while` when you do not know how many iterations you need up front: reading
until a sentinel, retrying until success, draining a queue.

```python
attempts = 0
while attempts < 3 and not check_in(device):
    attempts += 1
```

Every `while` loop needs something inside it that moves toward the exit condition.
If you cannot point to that line, you have written an infinite loop. `while True:`
with an explicit `break` is fine when the exit test sits naturally in the middle of
the body.

## 4. Slicing lists

Slicing works on lists exactly as it does on strings, and always returns a new list.

```python
>>> tags = [100, 101, 102, 103, 104, 105]
>>> tags[:2]        # [100, 101]
>>> tags[2:4]       # [102, 103]
>>> tags[-2:]       # [104, 105]
>>> tags[::2]       # [100, 102, 104]
>>> tags[10:]       # []           out-of-range slices are empty, never an error
>>> tags[1:]        # everything except the first: pairs with zip(tags, tags[1:])
```

Batching a list is one slice per batch:

```python
>>> [tags[i:i + 4] for i in range(0, len(tags), 4)]
[[100, 101, 102, 103], [104, 105]]
```

The last batch is shorter, and that is what callers expect.

## 5. Accumulator patterns

Most loops fall into one of four shapes. Name the shape before you write it.

**Count / sum:** start at zero, add as you go.

```python
online = 0
for d in devices:
    if d["status"] == "online":
        online += 1
```

**Collect:** start with an empty list, append what qualifies.

```python
stale = []
for d in devices:
    if d["days_since_checkin"] > 30:
        stale.append(d["hostname"])
```

**Running best:** start with `None` (or the first item), replace when you see better.

```python
oldest = None
for d in devices:
    if oldest is None or d["enrolled"] < oldest["enrolled"]:
        oldest = d
```

Starting with `None` handles the empty list for free. Starting with `devices[0]`
crashes on an empty list; starting with `0` or `""` gives wrong answers when every
real value is smaller than your fake starting point.

**Seen:** a set of what you have already handled, checked before you act.

```python
seen = set()
unique = []
for h in hosts:
    if h not in seen:
        seen.add(h)
        unique.append(h)
```

Built-ins cover the simple cases: `sum(...)`, `min(...)`, `max(...)`, `any(...)`,
`all(...)`. `max(devices, key=lambda d: d["ram_gb"])` returns the whole record with
the largest RAM; `max([], default=None)` avoids the `ValueError` on empty input. Say
in an interview: "I could write the loop, but `max` with a key is the same thing and
the reviewer can read it in one line."

## 6. Sorting

```python
>>> sorted([3, 1, 2])                   # [1, 2, 3]
>>> sorted([3, 1, 2], reverse=True)     # [3, 2, 1]
>>> sorted(["b", "A", "c"])             # ['A', 'b', 'c']    uppercase sorts first
>>> sorted(["b", "A", "c"], key=str.lower)   # ['A', 'b', 'c'] case-insensitively
```

`key` is a function called once per item; the items are sorted by what it returns.
For records that is nearly always a `lambda`:

```python
>>> devices = [{"hostname": "b", "ram": 16}, {"hostname": "a", "ram": 32}]
>>> sorted(devices, key=lambda d: d["ram"], reverse=True)[0]["hostname"]
'a'
```

### Several keys, mixed directions

Return a tuple from the key. Tuples compare element by element, so the first field
is the primary key and later fields break ties:

```python
>>> sorted(devices, key=lambda d: (-d["ram"], d["hostname"]))
```

Negating a number reverses its order without `reverse=True`, so you can sort RAM
descending and hostname ascending in one call. Strings cannot be negated; for a
descending string with an ascending number, sort twice and rely on stability:

```python
>>> devs = sorted(devices, key=lambda d: d["hostname"])              # secondary first
>>> devs = sorted(devs, key=lambda d: d["ram"], reverse=True)        # primary last
```

Python's sort is **stable**: items that compare equal keep their previous order. That
is what makes the two-pass trick work, and it is a fact interviewers like to hear you
state. `list.sort()` takes the same `key` and `reverse` arguments but sorts in place.

## 7. Membership: `in` on lists versus sets

`x in some_list` scans the list from the start; on a fleet of fifty thousand devices
inside a loop that is fifty thousand times fifty thousand comparisons. `x in some_set`
is a hash lookup and effectively constant time.

```python
>>> managed = {"C02XG1234ABC", "FVFXC1234A"}     # a set literal
>>> "FVFXC1234A" in managed
True
```

Rule of thumb: if you test membership more than once, build a set first. The
`seen`-set pattern above is exactly this.

## 8. Lists of dicts as records

Inventory data arrives as a list of dicts, one dict per device, keys for columns.

```python
>>> devices = [
...     {"hostname": "mbp-j-doe", "os": "macOS", "memory_gb": 16, "status": "online"},
...     {"hostname": "win-lab-01", "os": "Windows", "memory_gb": 8, "status": "offline"},
... ]
>>> [d["hostname"] for d in devices if d["status"] == "online"]
['mbp-j-doe']
```

Use `d.get("memory_gb", 0)` when a key might be missing; `d["memory_gb"]` raises
`KeyError`. Decide up front which you want: a missing key that silently becomes 0
can hide a broken export, while a crash on the first bad row can block a report.
Say which you chose and why.

That `[... for d in devices if ...]` is a list comprehension: a loop that builds a
list, written on one line. Part 9 covers comprehensions properly; for now, use them
for one-condition filters and maps, and write a full loop for anything else.

## 9. Nested loops

A loop inside a loop compares every item against every other item, or walks a table
of rows and columns.

```python
for device in devices:
    for app in device["apps"]:
        if app["name"] == "Zoom" and app["version"] < "5.0":
            outdated.append(device["hostname"])
            break            # one hit per device is enough
```

Each level multiplies the work. Two nested loops over the same list is O(n²); for
a few hundred items nobody cares, for a fleet it matters. When you find yourself
looking things up in the inner loop, precompute a set or dict outside and look up
instead. Interviewers who ask "how would this scale?" want that sentence.

## Gotchas interviewers probe

- **Mutating a list while iterating over it** skips elements. Build a new list, or
  iterate over a copy (`for x in xs[:]`).
- **`[[]] * 3`** makes three references to *one* inner list. Use `[[] for _ in range(3)]`.
- **`xs.sort()` returns `None`**; `sorted(xs)` returns the new list.
- **Off-by-one:** `range(n)` stops at `n - 1`; a slice `[a:b]` excludes `b`. Say
  "half-open interval" out loud and you will get it right.
- **Empty input.** Every loop-based function should be tested with `[]`. Running-best
  with `None` and `max(..., default=None)` are the tools.
- **Version strings are not numbers.** `"10.2" < "9.1"` is `True` because it compares
  character by character. Part 4 and Part 8 fix this; for now, notice it.
- **ISO dates *are* comparable as strings.** `"2024-03-01" < "2024-11-15"` works
  because the fields go from most to least significant with fixed widths. That is
  why the format exists.

## Interview notes for this part

- **Name the pattern before you type.** "This is a running best, starting from
  `None`." "This is a seen-set dedupe." Interviewers relax when they hear the shape;
  they know what bug classes to stop worrying about.
- **Ask what to do with ties and empties.** "If two devices have the same memory, does
  order matter?" "What should I return for an empty list: `None`, an empty list, or
  raise?" Every exercise in this part has an answer to both; real tickets often do not.
- **Reach for `sorted` with a `key` tuple** rather than writing comparison logic by
  hand. If the interviewer wants you to implement sorting, they will say so.
- **The trap:** writing `for i in range(len(xs))` and then indexing `xs[i]` and
  `xs[i + 1]` without guarding the last element. Use `zip(xs, xs[1:])` or `enumerate`
  and you cannot go past the end.

## Exercises

Run `course list 2`, then `course show 2.1`. Edit, run `course run 2.1`, repeat.

1. `count_online` · a for loop with a condition over a list of dicts
2. `oldest_device` · running best; the empty list returns `None`
3. `chunk_serials` · slicing a list into fixed-size batches
4. `dedupe_preserve_order` · the seen-set pattern
5. `rolling_average` · windows over a list; short windows at the start
6. `find_gaps` · neighbours with `zip(xs, xs[1:])`; ranges as tuples
7. `top_n_by_memory` · `sorted` with a key tuple, `reverse`, and ties by name
