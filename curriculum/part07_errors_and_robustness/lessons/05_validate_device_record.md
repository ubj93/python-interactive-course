# Collect every error

--- teach
### Append, do not return
A validator for user input should report everything wrong at once. The shape: an `errors` list, one `if` per rule that appends a message, no early `return`, and the list returned at the end. An empty list means valid.
```python
errors = []
for name in REQUIRED:
    if name not in record:
        errors.append(f"missing field: {name}")
...
return errors
```
`REQUIRED` is a tuple, so this loop reports missing fields in the fixed order the spec wants.

--- predict
What does this print?
```python
REQUIRED = ("serial", "hostname", "os")
record = {"hostname": "mbp-j-doe"}
errors = []
for name in REQUIRED:
    if name not in record:
        errors.append(f"missing field: {name}")
print(errors)
```
answer: ['missing field: serial', 'missing field: os']
> Every missing name is reported, in `REQUIRED` order, because the loop never stops early.

--- teach
### One predicate per field, never raising
Write a small function per field that returns `True` or `False` for any input, including `None` and wrong types. Check `isinstance(v, str)` before calling string methods, because `None.upper()` would crash. A regex from Part 4 keeps the format rules short.
```python
SERIAL_RE = re.compile(r"^[A-Z0-9]{7,12}$")

def _is_serial(v):
    return isinstance(v, str) and SERIAL_RE.match(v) is not None
```
`and` stops at the first false part, so `SERIAL_RE.match` only runs on strings.

--- predict
What does this print?
```python
import re
SERIAL_RE = re.compile(r"^[A-Z0-9]{7,12}$")
print(SERIAL_RE.match("c02") is not None, SERIAL_RE.match("7GH2K3Q") is not None)
```
answer: False True
> `c02` is lowercase and too short, so no match. `7GH2K3Q` is seven uppercase letters and digits, which fits `{7,12}`.

--- teach
### `bool` is an `int`; dates need `try`
`ram_gb` must be a positive `int`, and `True` is an `int`, so exclude bools explicitly. For `last_seen`, `date.fromisoformat` raises `ValueError` on `"2024-13-01"`; a predicate must turn that into `False`. Check the length first: `fromisoformat` accepts other shapes on newer Pythons, but the spec wants `YYYY-MM-DD`.
```python
def _is_ram(v):
    return isinstance(v, int) and not isinstance(v, bool) and v > 0

def _is_iso_date(v):
    if not isinstance(v, str) or len(v) != 10:
        return False
    try:
        date.fromisoformat(v)
    except ValueError:
        return False
    return True
```

--- code
Complete `_is_iso_date`: return `True` only for a 10-character string that `date.fromisoformat` accepts; never raise.
```python
from datetime import date
def _is_iso_date(v):
```
check: _is_iso_date("2024-05-01") is True
check: _is_iso_date("2024-13-01") is False
check: _is_iso_date(None) is False
solution:     if not isinstance(v, str) or len(v) != 10:
solution:         return False
solution:     try:
solution:         date.fromisoformat(v)
solution:     except ValueError:
solution:         return False
solution:     return True
> The type and length guard runs first so `None` never reaches `fromisoformat`. Month 13 makes `fromisoformat` raise `ValueError`, which the predicate turns into `False`.

--- quiz
What does `_is_ram(True)` return with the definition above?
- [ ] `True`, because `True` is an `int` greater than 0
- [x] `False`, because bools are excluded explicitly
- [ ] It raises `TypeError`
> `isinstance(True, int)` is `True`, which is why the `not isinstance(v, bool)` clause is there. Without it, `True` would pass as `1`.

--- teach
### A table of checks, one message format
Put the field name, its predicate and its message in a list, in the required order. One loop runs them all for fields that are present and appends `"<message>, got <value!r>"`.
```python
CHECKS = [
    ("serial", _is_serial, "serial: must be 7-12 uppercase letters or digits"),
    ("ram_gb", _is_ram, "ram_gb: must be a positive integer"),
]
for name, ok, message in CHECKS:
    if name in record and not ok(record[name]):
        errors.append(f"{message}, got {record[name]!r}")
```
Adding a rule is one line of data, not a new block of code.

--- teach
### Unknown fields, sorted, last
Keys that are not required are reported after everything else, in sorted order. Set difference finds them; `sorted` orders them.
```python
for name in sorted(set(record) - set(REQUIRED)):
    errors.append(f"unknown field: {name}")
```

--- fill
Complete the loop so unknown fields are reported in alphabetical order.
```python
for name in ___(set(record) - set(REQUIRED)):
    errors.append(f"unknown field: {name}")
```
answer: sorted
> `set(record) - set(REQUIRED)` is the keys that are not required. A set has no order, so `sorted` gives the deterministic list the tests expect.

--- exercise 7.5

--- recap
- Collect: one `errors` list, one `if` per rule, no early return.
- Predicates return a bool for any input; test `isinstance` before methods.
- Exclude `bool` from `int` checks; wrap `date.fromisoformat` in `try`.
- A table of `(field, predicate, message)` keeps the order and format fixed.
- `sorted(set(record) - set(REQUIRED))` lists unknown fields last.
