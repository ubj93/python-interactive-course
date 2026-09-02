# List comprehensions

--- teach
### A loop that builds a list
You have written this shape many times: start with an empty list, loop, `append`. It works, but it is four lines for one idea.
```python
hostnames = []
for d in devices:
    hostnames.append(d["hostname"])
```

--- teach
### The same thing as a comprehension
A list comprehension is that loop turned inside out, in one expression: the thing to collect first, then the `for`. Read it as "hostname for each device in devices".
```python
hostnames = [d["hostname"] for d in devices]
```
The brackets say "build a list". Interviewers read this as fluent Python; the four-line version reads as translated from another language.

--- predict
What does this print?
```python
print([n * 2 for n in [1, 2, 3]])
```
answer: [2, 4, 6]
> For each `n`, the expression `n * 2` is evaluated and collected into a new list. The original list is unchanged.

--- teach
### Add `if` to keep only some items
The loop version filters with an `if` around the `append`. The comprehension puts the same condition at the end. Items that fail the test are skipped; order is preserved.
```python
online = []
for d in devices:
    if d["online"]:
        online.append(d["hostname"])

online = [d["hostname"] for d in devices if d["online"]]
```
Read: *expression* for *item* in *iterable* if *condition*.

--- predict
What does this print?
```python
hosts = ["mbp-j-doe", "win-lab-01", "mbp-a-lee"]
print([h for h in hosts if h.startswith("mbp")])
```
answer: ['mbp-j-doe', 'mbp-a-lee']
> Only the hosts where the condition is true are collected, in their original order. `win-lab-01` is skipped.

--- teach
### Days between two dates
Subtracting one `date` from another gives a `timedelta`, and `.days` is the whole number of days. The function takes `today` as a parameter; it never calls `date.today()` itself, so the tests can pin the date.
```python
>>> from datetime import date
>>> (date(2024, 6, 1) - date(2024, 5, 1)).days
31
```

--- predict
What does this print?
```python
from datetime import date
print((date(2024, 6, 1) - date(2024, 5, 30)).days)
```
answer: 2
> May 30 to June 1 is two days. The result is an `int`, ready to compare against `max_days`.

--- teach
### Guard `None` with `or`
A device that never checked in has `last_seen` of `None`, and `today - None` would crash. Put the `None` test first, joined with `or`. `or` stops at the first true operand, so the subtraction only runs when there is a real date.
```python
d["last_seen"] is None or (today - d["last_seen"]).days > max_days
```
That whole expression is the comprehension's `if` condition.

--- quiz
Exactly `max_days` days ago must still count as fresh. Which comparison is right?
- [ ] `(today - last_seen).days >= max_days`
- [x] `(today - last_seen).days > max_days`
- [ ] `(today - last_seen).days == max_days`
> "More than `max_days`" is strictly greater. `>=` would flag the boundary day as stale, and the tests check that boundary.

--- exercise 9.1

--- recap
- `[expr for item in iterable]` replaces the empty-list-and-append loop.
- `[expr for item in iterable if cond]` filters; order is preserved.
- `(date_a - date_b).days` gives whole days; take `today` as a parameter.
- `x is None or ...` short-circuits, so the right side never sees `None`.
