# Keyword overrides

--- teach
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

--- code
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

--- predict
What does this print?
```python
def collect(**opts):
    return len(opts)

print(collect(a=1, b=2, c=3))
```
answer: 3
> Three keyword arguments become a three-key dict. `len` of a dict is the number of keys.

--- teach
### Start from a copy of the defaults
`dict(DEFAULTS)` makes a new dict with the same keys and values. Change the copy, return the copy: the module-level `DEFAULTS` stays untouched, and each call hands out an independent dict. `policy.update(overrides)` writes every key of `overrides` into `policy`.
```python
policy = dict(DEFAULTS)         # a fresh copy
policy.update(overrides)        # apply the caller's changes
return policy
```
`policy = DEFAULTS` would be a second name for the same dict: the aliasing trap from Part 2, now with a dict.

--- code
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

--- quiz
A caller does `p = retry_policy(); p["max_attempts"] = 99`. Which line in `retry_policy` keeps the next call's defaults intact?
- [ ] `policy = DEFAULTS`
- [x] `policy = dict(DEFAULTS)`
- [ ] `policy = DEFAULTS.keys()`
> `dict(DEFAULTS)` (or `DEFAULTS.copy()`) is a new dict. `policy = DEFAULTS` just aliases the shared one, so the caller's change would leak into every later call.

--- teach
### `**kwargs` swallows typos, so check the keys
With a normal parameter, `retry_policy(max_attemps=5)` fails immediately: Python raises `TypeError` for an unexpected keyword. With `**overrides` nothing happens unless you check. Do it first, and raise the same `TypeError` Python would.
```python
for name in overrides:
    if name not in DEFAULTS:
        raise TypeError(f"unexpected keyword argument {name!r}")
```
`TypeError` is for "wrong kind of thing" (an unknown option); `ValueError` is for "right kind, bad value" (`max_attempts=0`).

--- quiz
`retry_policy(max_attempts=0)` and `retry_policy(max_attemps=5)` both must fail. Which errors?
- [ ] Both `ValueError`
- [x] `ValueError` for `0`, `TypeError` for the misspelled name
- [ ] Both `TypeError`
> A bad value of a known option is a `ValueError`. An unknown option name is a `TypeError`, matching what Python raises for an unexpected keyword.

--- teach
### `isinstance` checks a type; `sorted(set(...))` normalises
`isinstance(x, int)` is True only when `x` is an int, so `2.5` fails and `max_attempts` can be checked properly. For `retry_on`, any iterable is allowed: `set(...)` drops duplicates, `sorted(...)` orders them into a list, `tuple(...)` makes the final unchangeable value.
```python
>>> isinstance(2.5, int)
False
>>> tuple(sorted(set([503, 429, 503])))
(429, 503)
```
Read the chain inside out: set, then sorted, then tuple.

--- fill
Complete the line so `retry_on` becomes a sorted tuple without duplicates.
```python
policy["retry_on"] = tuple(sorted(___(policy["retry_on"])))
```
answer: set
> `set` removes duplicates, `sorted` gives an ascending list, and `tuple` fixes the result. Works for a list, a set, a tuple or a `range`.

--- exercise 3.2

--- recap
- `**overrides` gathers keyword arguments into a dict.
- Copy the defaults with `dict(DEFAULTS)`, then `.update(overrides)`.
- Unknown option name: `TypeError`; bad value: `ValueError`.
- `isinstance(x, int)` checks type; `tuple(sorted(set(xs)))` normalises.
