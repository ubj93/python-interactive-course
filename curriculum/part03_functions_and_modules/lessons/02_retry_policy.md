# Keyword overrides

--- teach #bash-defaults-worked
### Bash bridge: defaults and scope are explicit
Python creates a default once when `def` runs. Use `None` for an optional collection, then create a fresh one inside the function. A parameter is a local name: rebinding it does not rebind a caller's variable.
```python
prefix = "lab"
def label(host, prefix="node"):
    prefix = prefix.upper()
    return prefix + "-" + host

print(label("a"))       # NODE-a
print(prefix)           # lab
```
Pass caller values explicitly rather than relying on a shell variable to be visible in another function. This bridge uses functions, lists and `append`. Copy an explicitly supplied list too when your function promises to leave it unchanged.

--- code #bash-defaults-modify
Repair `add_tag`: omitted tags must start fresh on every call, and a supplied list must stay unchanged. Keep the local `tag` uppercase; do not change any caller variable.

Browser: edit the function. Terminal: type the complete corrected function below the starter.
```python
def add_tag(tag, tags=[]):
    tag = tag.upper()
    tags.append(tag)
    return tags

saved_tags = ["OLD"]

# Check helper: keep both outputs alive to catch shared storage.
def separate_tag_results():
    first = add_tag("qa")
    second = add_tag("ops")
    return first == ["QA"] and second == ["OPS"] and first is not second
```
check: separate_tag_results()
check: add_tag("new", saved_tags) == ["OLD", "NEW"] and saved_tags == ["OLD"]
solution: def add_tag(tag, tags=None):
solution:     tags = [] if tags is None else list(tags)
solution:     tag = tag.upper()
solution:     tags.append(tag)
solution:     return tags
> `None` avoids a shared default; `list(tags)` protects an explicitly supplied list. Rebinding local `tag` does not replace the caller's string.

--- code #bash-defaults-check
Independent check: write `with_retry(delays=None, extra=2)`. Return a fresh list containing the supplied delays followed by `extra`. With no delays, return `[extra]`. Leave the input list and module-level `extra` unchanged.

Browser: edit the function. Terminal: type the complete corrected function below the starter.
```python
extra = 99
saved_delays = [1, 3]

def with_retry(delays=None, extra=2):
    pass

# Check helper: later calls must leave the earlier result intact.
def separate_retry_results():
    first = with_retry()
    second = with_retry(extra=4)
    return first == [2] and second == [4] and first is not second
```
check: separate_retry_results()
check: with_retry(extra=0) == [0] and extra == 99
check: with_retry(saved_delays, extra=5) == [1, 3, 5] and saved_delays == [1, 3]
solution: def with_retry(delays=None, extra=2):
solution:     result = [] if delays is None else list(delays)
solution:     result.append(extra)
solution:     return result
> The parameter `extra` belongs to the call, while the module variable stays 99. Every result has its own list. The bridge is complete; continue this lesson or return to the diagnostic.

--- teach #card-624f75f602945aca
### `**kwargs` collects extra keyword arguments
Two stars before a parameter name mean "gather every keyword argument the caller passed into a dict". The names are the keys, the values the values. `kwargs` is a convention; a descriptive name like `overrides` reads better.
```python
>>> def show(**overrides):
...     return overrides
>>> show(max_attempts=5, backoff=1.5)
{'max_attempts': 5, 'backoff': 1.5}
>>> show()
{}
```

--- code #card-0811e2cc776250d0
Define `names(**opts)` that returns a sorted list of the option names it was given. Then print `names(backoff=2, max_attempts=5)`.
```python
# your code here
```
expect: ['backoff', 'max_attempts']
check: names() == []
solution: def names(**opts):
solution:     return sorted(opts)
solution: print(names(backoff=2, max_attempts=5))
> `opts` is a dict of the keyword arguments, and `sorted` on a dict gives its keys in order. With no arguments the dict is empty, so the list is too.

--- predict #card-4c098cbeb2d35385
What does this print?
```python
def collect(**opts):
    return len(opts)

print(collect(a=1, b=2, c=3))
```
answer: 3
> Three keyword arguments become a three-key dict. `len` of a dict is the number of keys.

--- teach #card-7418a2fa8aca5e59
### Start from a copy of the defaults
`dict(DEFAULTS)` makes a new dict with the same keys and values. Change the copy, return the copy: the module-level `DEFAULTS` stays untouched, and each call hands out an independent dict. `policy.update(overrides)` writes every key of `overrides` into `policy`.
```python
policy = dict(DEFAULTS)         # a fresh copy
policy.update(overrides)        # apply the caller's changes
return policy
```
`policy = DEFAULTS` would be a second name for the same dict: the aliasing trap from Part 2, now with a dict.

--- code #card-001b6bcb86f85964
Set `policy` to a fresh copy of `DEFAULTS` with `overrides` applied. `DEFAULTS` itself must stay unchanged.
```python
DEFAULTS = {"max_attempts": 3, "base_delay": 1.0}
overrides = {"max_attempts": 5}
```
check: policy == {"max_attempts": 5, "base_delay": 1.0}
check: DEFAULTS["max_attempts"] == 3
solution: policy = dict(DEFAULTS)
solution: policy.update(overrides)
> `dict(DEFAULTS)` copies; `update` writes the overrides into the copy only. Had you written `policy = DEFAULTS`, the second check would fail because both names point at one dict.

--- quiz #card-c7fb142a9a0552ac
A caller does `p = retry_policy(); p["max_attempts"] = 99`. Which line in `retry_policy` keeps the next call's defaults intact?
- [ ] `policy = DEFAULTS`
- [x] `policy = dict(DEFAULTS)`
- [ ] `policy = DEFAULTS.keys()`
> `dict(DEFAULTS)` (or `DEFAULTS.copy()`) is a new dict. `policy = DEFAULTS` just aliases the shared one, so the caller's change would leak into every later call.

--- teach #card-cebc67acc8635863
### `**kwargs` swallows typos, so check the keys
With a normal parameter, `retry_policy(max_attemps=5)` fails immediately: Python raises `TypeError` for an unexpected keyword. With `**overrides` nothing happens unless you check. Do it first, and raise the same `TypeError` Python would.
```python
for name in overrides:
    if name not in DEFAULTS:
        raise TypeError(f"unexpected keyword argument {name!r}")
```
`TypeError` is for "wrong kind of thing" (an unknown option); `ValueError` is for "right kind, bad value" (`max_attempts=0`).

--- quiz #card-5ed3baa6fa5c5aef
`retry_policy(max_attempts=0)` and `retry_policy(max_attemps=5)` both must fail. Which errors?
- [ ] Both `ValueError`
- [x] `ValueError` for `0`, `TypeError` for the misspelled name
- [ ] Both `TypeError`
> A bad value of a known option is a `ValueError`. An unknown option name is a `TypeError`, matching what Python raises for an unexpected keyword.

--- teach #card-fde61b40dd3b55b4
### `isinstance` checks a type; `sorted(set(...))` normalises
`isinstance(x, int)` is True only when `x` is an int, so `2.5` fails and `max_attempts` can be checked properly. For `retry_on`, any iterable is allowed: `set(...)` drops duplicates, `sorted(...)` orders them into a list, `tuple(...)` makes the final unchangeable value.
```python
>>> isinstance(2.5, int)
False
>>> tuple(sorted(set([503, 429, 503])))
(429, 503)
```
Read the chain inside out: set, then sorted, then tuple.

--- fill #card-eada13f3ab085ef0
Complete the line so `retry_on` becomes a sorted tuple without duplicates.
```python
policy["retry_on"] = tuple(sorted(___(policy["retry_on"])))
```
answer: set
> `set` removes duplicates, `sorted` gives an ascending list, and `tuple` fixes the result. Works for a list, a set, a tuple or a `range`.

--- exercise 3.2 #card-6d463f2a39b95f3e

--- recap #card-c9ef06498ca95b29
- `**overrides` gathers keyword arguments into a dict.
- Copy the defaults with `dict(DEFAULTS)`, then `.update(overrides)`.
- Unknown option name: `TypeError`; bad value: `ValueError`.
- `isinstance(x, int)` checks type; `tuple(sorted(set(xs)))` normalises.
