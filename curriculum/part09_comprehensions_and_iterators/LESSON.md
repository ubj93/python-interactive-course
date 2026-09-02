# Part 9 · Comprehensions, iterators, and functional tools

> **What you will be able to do:** express "filter this, transform that, group these,
> take the top few" in one or two idiomatic lines instead of a ten-line loop, stream
> through data that does not fit in memory, and sort by several keys at once. About
> ninety minutes, plus the exercises.

## Why this part matters in interviews

Interviewers form an opinion in the first thirty seconds of watching you code. A
candidate who writes `[d["hostname"] for d in devices if d["online"]]` reads as
fluent; one who builds the same list with `result = []` and `append` does not. The
second version is not wrong. It is just slower to write, longer to read, and it
signals that you have not internalised the language. This part fixes that, and it
introduces the lazy tools (`yield`, `itertools`) that keep log-processing scripts from
eating all the RAM on a build machine.

## 1. List comprehensions

A comprehension is a `for` loop that builds a list, turned inside out:

```python
>>> devices = [
...     {"hostname": "mbp-j-doe", "os": "mac", "online": True},
...     {"hostname": "win-lab-01", "os": "windows", "online": False},
...     {"hostname": "mbp-a-lee", "os": "mac", "online": True},
... ]
>>> [d["hostname"] for d in devices]                        # map
['mbp-j-doe', 'win-lab-01', 'mbp-a-lee']
>>> [d["hostname"] for d in devices if d["online"]]         # filter + map
['mbp-j-doe', 'mbp-a-lee']
>>> [d["hostname"].upper() if d["online"] else "-" for d in devices]   # conditional expression
['MBP-J-DOE', '-', 'MBP-A-LEE']
```

Read it as: *expression* for *item* in *iterable* if *condition*. Two `for`s nest,
outer first:

```python
>>> [(h, p) for h in ["a", "b"] for p in [22, 443]]
[('a', 22), ('a', 443), ('b', 22), ('b', 443)]
>>> [x for row in [[1, 2], [3]] for x in row]                # flatten one level
[1, 2, 3]
```

**Gotchas**

- A comprehension is for *building a value*. `[print(x) for x in xs]` builds a list of
  `None`s to throw away. Use a plain loop for side effects.
- If it needs more than one `if` and two `for`s, or you have to squint, write the
  loop. Readability wins.
- The loop variable does not leak (unlike Python 2), so `[x for x in xs]` leaves `x`
  untouched outside.

## 2. Dict and set comprehensions

Same shape, different brackets:

```python
>>> {d["hostname"]: d["os"] for d in devices}                 # dict
{'mbp-j-doe': 'mac', 'win-lab-01': 'windows', 'mbp-a-lee': 'mac'}
>>> {d["os"] for d in devices}                                # set (order not guaranteed)
{'mac', 'windows'}
>>> {v: k for k, v in {"a": 1, "b": 2}.items()}               # invert a dict
{1: 'a', 2: 'b'}
```

Duplicate keys in a dict comprehension: the last one wins, silently. If duplicates
matter, detect them first (Part 5's `invert_index` did exactly that).

## 3. Generator expressions and laziness

Parentheses instead of brackets give you a **generator**: it produces values one at a
time when asked, and stores none of them.

```python
>>> gen = (d["hostname"] for d in devices if d["online"])
>>> gen
<generator object <genexpr> at 0x...>
>>> next(gen)
'mbp-j-doe'
>>> list(gen)                 # the rest
['mbp-a-lee']
>>> list(gen)                 # exhausted: a generator is one-shot
[]
```

Pass a generator straight into a function that consumes an iterable; the extra
parentheses are optional when it is the only argument:

```python
>>> sum(d["ram_gb"] for d in devices)
>>> any(d["online"] for d in devices)
>>> ", ".join(d["hostname"] for d in devices)
>>> max((d["disk_pct"] for d in devices), default=0)
```

Why it matters: `sum(len(line) for line in f)` over a 40 GB log uses a few kilobytes.
`sum([len(line) for line in f])` first materialises a list of forty billion ints.

**Gotcha:** `len(gen)` is a `TypeError`; a generator has no length until it is consumed.

## 4. Generator functions: `yield`

A function containing `yield` returns a generator when called. Its body does not run
until something asks for the first value, then it runs to the next `yield`, pauses,
and resumes from there on the next request.

```python
>>> def clean_lines(lines):
...     for line in lines:
...         line = line.split("#", 1)[0].strip()      # drop comments
...         if line:
...             yield line
...
>>> list(clean_lines(["mbp-j-doe  # jane", "", "# all of it", "win-lab-01"]))
['mbp-j-doe', 'win-lab-01']
```

- `return` in a generator ends the stream (`StopIteration` for the consumer).
- `yield from other_iterable` hands off to another iterator; it saves a loop.
- Generators compose: `clean_lines(open(path))` reads, cleans and streams in one line.

**Gotcha, and it is a favourite interview probe:** because the body is delayed,
*argument validation is delayed too.*

```python
>>> def batched(items, n):
...     if n < 1:
...         raise ValueError("n must be >= 1")
...     ...yield...
>>> b = batched([1, 2], 0)      # no error here!
>>> next(b)                     # ValueError only now
```

If callers should get the error at call time, split the function: a normal function
that validates and *returns* a generator built by an inner generator function.

## 5. The iterator protocol: `iter` and `next`

A `for` loop is sugar for:

```python
>>> it = iter([10, 20])         # ask the iterable for an iterator
>>> next(it)
10
>>> next(it)
20
>>> next(it)
StopIteration
>>> next(it, None)              # a default instead of the exception
```

- An **iterable** is anything `iter()` accepts: lists, dicts, files, generators.
- An **iterator** is what `iter()` returns: it has `__next__` and is its own iterable.
  Lists are iterable but not iterators; generators are both.
- `iter(callable, sentinel)` calls `callable()` until it returns `sentinel`:
  `iter(lambda: f.read(4096), "")` reads a file in chunks.

Pulling manually with `next` is how you write "take the first two, then process the
rest" without indexing, and it works on any iterable, not just lists.

## 6. `itertools`

| Function | What it does | Example |
|---|---|---|
| `chain(a, b)` | one stream from several | `chain(macs, wins)` |
| `islice(it, n)` / `islice(it, start, stop)` | slice any iterable lazily | first 10 lines of a stream |
| `count(start)` | infinite counter | `zip(count(1), names)` |
| `groupby(it, key)` | runs of equal keys, **adjacent only** | streaks of failing builds |
| `accumulate(it)` | running totals | cumulative bytes |
| `product(a, b)` | cartesian product | every (host, port) pair |
| `zip(xs, xs[1:])` | adjacent pairs of a sequence | deltas between check-ins |

`groupby` is the one people misuse:

```python
>>> from itertools import groupby
>>> statuses = ["pass", "fail", "fail", "pass", "fail"]
>>> [(k, len(list(g))) for k, g in groupby(statuses)]
[('pass', 1), ('fail', 2), ('pass', 1), ('fail', 1)]
```

It groups *consecutive* equal keys. That is exactly what you want for "runs" and
exactly wrong for "count by category" (use `Counter` or sort first). Also, each group
`g` is an iterator that is invalidated when you advance to the next key, so
materialise it (`list(g)`) before moving on.

`zip` with an offset slice gives adjacent pairs; `itertools.pairwise` does the same
lazily but only exists from Python 3.10, so the slice idiom is what you write in
interviews:

```python
>>> ts = [0, 30, 45, 120]
>>> [b - a for a, b in zip(ts, ts[1:])]
[30, 15, 75]
```

## 7. `functools`

```python
>>> from functools import partial, reduce, lru_cache
>>> hex_to_int = partial(int, base=16)          # freeze an argument
>>> hex_to_int("ff")
255
>>> reduce(lambda acc, x: acc + x, [1, 2, 3], 0)   # fold; prefer sum/max/etc when they exist
6
>>> @lru_cache(maxsize=None)
... def fib(n): return n if n < 2 else fib(n - 1) + fib(n - 2)
```

`lru_cache` memoises pure functions with hashable arguments; you will build an LRU
cache by hand in Part 12, so know what the decorator is doing for you. `reduce` is
rarely the clearest tool; if you reach for it in an interview, say why `sum`, `max`,
`any` or a loop would not do.

## 8. Sorting with keys

`sorted` and `list.sort` take a `key` function that maps each item to something
comparable. The trick to multi-key sorts is returning a **tuple**:

```python
>>> rows = [("mac", "mbp-a-lee", 3), ("windows", "win-lab-01", 9), ("mac", "mbp-j-doe", 3)]
>>> sorted(rows, key=lambda r: (r[0], r[1]))            # os, then name
>>> sorted(rows, key=lambda r: (r[0], -r[2], r[1]))     # os asc, count desc, name asc
```

Ways to get "descending" for one key while the rest stay ascending:

| Key type | Trick |
|---|---|
| number | negate it: `-count` |
| date / datetime | negate an ordinal or timestamp: `-d.toordinal()`, `-dt.timestamp()` |
| string | no negation; sort twice (see below) or use `reverse=True` and flip the others |
| anything | sort by the secondary keys first, then `sort(key=primary, reverse=True)`: sorts are **stable** |

`None` cannot be compared with anything. Put a boolean in the tuple so it sorts to one
end: `(d["last_seen"] is None, ...)` puts `None` last.

`operator.itemgetter("os", "name")` and `attrgetter("os")` are ready-made key
functions; `itemgetter("a", "b")` returns a tuple, so it is a multi-key sort in one
call. `reverse=True` reverses the whole comparison, which keeps stability intact.

## 9. `any`, `all`, `min`, `max`

```python
>>> any(d["online"] for d in devices)                    # short-circuits on the first True
>>> all(d["os"] == "mac" for d in devices)               # True for an empty iterable
>>> max(devices, key=lambda d: d["ram_gb"])              # the *item*, not the key
>>> min(devices, key=lambda d: d["last_seen"], default=None)   # default for empty input
```

`all([])` is `True` and `any([])` is `False`. `max` of an empty iterable raises
`ValueError` unless you pass `default`.

## 10. `heapq.nlargest` versus sorting

"Top k by disk usage" has two honest answers:

```python
>>> sorted(devices, key=lambda d: d["disk_pct"], reverse=True)[:k]   # O(n log n), simple
>>> heapq.nlargest(k, devices, key=lambda d: d["disk_pct"])          # O(n log k), streaming
```

- For small `k` on a huge or streaming input, `nlargest` never holds more than `k`
  items and never builds the full sorted list.
- For `k` close to `n`, sorting is as fast and clearer.
- Both preserve the original order among equal keys, so their answers are identical.
- `k == 1` is just `max(..., key=...)`; `nlargest` special-cases it internally.

Say the trade-off out loud; that is what the interviewer is listening for.

## 11. Unpacking and star expressions

```python
>>> first, *rest = [1, 2, 3, 4]         # first=1, rest=[2, 3, 4]
>>> *init, last = [1, 2, 3, 4]          # last=4
>>> head, *_ = "mbp-j-doe.corp.example.com".split(".")
>>> a, b = b, a                         # swap
>>> for i, (host, pct) in enumerate(pairs, start=1): ...   # nested unpacking
>>> print(*["a", "b"], sep=", ")        # splat a list into positional args
>>> merged = {**defaults, **overrides}   # later wins
```

`zip(*rows)` transposes a list of rows into columns. It is the standard interview
one-liner for "turn columns into rows".

## 12. Date arithmetic without a clock

`datetime.date` and `datetime.datetime` subtract to a `timedelta`:

```python
>>> from datetime import date, datetime, timedelta
>>> (date(2024, 6, 1) - date(2024, 5, 1)).days
31
>>> (datetime(2024, 5, 1, 9, 30) - datetime(2024, 5, 1, 9, 0)).total_seconds()
1800.0
>>> date(2024, 5, 1) + timedelta(days=30)
datetime.date(2024, 5, 31)
```

Never call `date.today()` inside the function you are testing. Take `today` as a
parameter (or an injected `now` callable, as in Part 8) and pass a fixed date from
the test. The staleness rule then reads `(today - last_seen).days > max_days`, and the
boundary case (exactly `max_days`) is decided in one place.

## Interview notes for this part

- **Narrate the shape.** "Filter then map, so a comprehension with an `if`." "This is
  runs of adjacent equal values, so `groupby`." Naming the pattern tells the
  interviewer you have seen it before.
- **Say "lazy" when you mean it.** If the input could be a file or a stream, write a
  generator and say so. If it is a list of twenty dicts, a list comprehension is fine
  and a generator is showing off.
- **Ask how ties should break and where `None` goes** before writing a sort key. Then
  write the key as a tuple and explain each element.
- **The trap:** `groupby` on unsorted data, `len()` on a generator, and validating
  arguments inside a generator body. All three look right and fail later.

## Exercises

Run `course list 9`, then `course show 9.1`.

1. `stale_devices` · list comprehension with a condition and a cutoff date
2. `batched` · a generator function; eager validation, lazy production
3. `read_lines_lazy` · a generator over a file object that strips and skips comments
4. `sort_devices` · multi-key sort with tuples, negation and a `None` guard
5. `pairwise_deltas` · adjacent pairs with `zip`, time between check-ins
6. `group_consecutive` · `itertools.groupby` for runs of failing builds
7. `top_k` · `heapq.nlargest` versus a full sort, and when to prefer each
