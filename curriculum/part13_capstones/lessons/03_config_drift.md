# Capstone: config drift

--- teach
### The ticket
A compliance job compares the expected baseline config with what an endpoint actually has. Both are nested dicts of dicts, lists and scalars. Produce a flat list of drift records, each with a dotted `path` such as `security.firewall.stealth`, a `kind` of `missing`, `extra` or `changed`, and the `expected` and `actual` values. Some paths are noise (`uuid`, `dock.apps`) and are filtered by prefix. Output is sorted by path.

Rules in your own words:
```
- dicts: key only in expected -> missing; only in actual -> extra; both -> recurse
- lists: by position; index on one side only -> missing/extra; both -> recurse
- anything else: changed when the type differs OR the value differs
- ignore: path == prefix, or path startswith prefix + "."
- sort: by the tuple of dotted segments
```

--- teach
### Three functions
```python
def config_drift(expected, actual, ignore=()):
    prefixes = list(ignore)
    records = [r for r in diff_values(expected, actual) if not is_ignored(r["path"], prefixes)]
    return sorted(records, key=lambda r: tuple(r["path"].split(".")))
```
- `is_ignored(path, ignore)`: one `any(...)` over the prefixes.
- `diff_values(expected, actual, path="")`: the recursive walk. It returns records in any order and knows nothing about ignoring.
- `config_drift`: filter, then sort. All the policy lives here.

Keeping ignore and sort out of the walk is the point: the walk stays three branches long, and the tests grade it on its own.

--- teach
### Recurse with the path as a parameter
The path string is built on the way down; records are collected on the way up. A small helper joins segments so the root (`""`) does not produce a leading dot.
```python
def _join(path, key):
    return f"{path}.{key}" if path else str(key)

def diff_values(expected, actual, path=""):
    out = []
    if isinstance(expected, dict) and isinstance(actual, dict):
        ...   # expected keys: missing or recurse; then actual-only keys: extra
    elif isinstance(expected, list) and isinstance(actual, list):
        ...   # for i in range(max(len(expected), len(actual)))
    elif type(expected) is not type(actual) or expected != actual:
        out.append({"path": path, "kind": "changed", "expected": expected, "actual": actual})
    return out
```
The last branch catches scalars and every mismatched shape (a dict against a list, a list against a string) as one `changed` record. Plain `==` is not enough there: `True == 1` and `1 == 1.0` are true, and the spec calls both drift.

--- predict
What does this print?
```python
def _join(path, key):
    return f"{path}.{key}" if path else str(key)

print(_join(_join("", "apps"), 1))
```
answer: apps.1
> At the root `path` is `""`, which is falsy, so the first call returns `"apps"` with no leading dot. The second call has a path, so it appends `.1`. List indexes go through `str(key)` and become numeric segments.

--- quiz
What does `diff_values(True, 1, "x")` return?
- [ ] `[]`, because `True == 1`
- [x] One record: `{"path": "x", "kind": "changed", "expected": True, "actual": 1}`
- [ ] One record with kind `"extra"`
> Values are equal only when they have the same type AND compare equal. `bool` and `int` are different types, so `type(expected) is not type(actual)` is true and the record is `changed`. `missing` and `extra` are only for keys or positions that exist on one side.

--- code
Write the body of `diff_scalar`, the "everything else" branch: return a one-record list of kind `changed` when the values differ in type or value, otherwise an empty list.
```python
def diff_scalar(expected, actual, path):
```
check: diff_scalar(True, 1, "x") == [{"path": "x", "kind": "changed", "expected": True, "actual": 1}]
check: diff_scalar("a", "a", "x") == []
check: diff_scalar({"b": 1}, [1], "a") == [{"path": "a", "kind": "changed", "expected": {"b": 1}, "actual": [1]}]
solution:     if type(expected) is not type(actual) or expected != actual:
solution:         return [{"path": path, "kind": "changed", "expected": expected, "actual": actual}]
solution:     return []
> The type test comes first and short-circuits, so `True` versus `1` never reaches `!=`. A dict against a list lands here too, because the dict/dict and list/list branches did not claim it, and the whole containers become the record's values.

--- teach
### Prefixes and segment order
An ignore prefix matches its own path and every dotted child, but not a sibling that merely starts with the same letters: `dock.apps` must drop `dock.apps.1.name` and keep `dock.apps_extra`. The `+ "."` is what makes that distinction.

Sorting is by path, compared segment by segment: split on the dot and sort on the tuple. Each segment is compared as plain text, so `apps.10` comes before `apps.2` (`"10"` sorts before `"2"`), exactly as the spec says.
```python
sorted(records, key=lambda r: tuple(r["path"].split(".")))
```
The key documents the rule; a reviewer reads it and knows the ordering without a comment.

--- code
Set `paths` to the record paths in report order: sorted by the tuple of dotted segments.
```python
records = [{"path": "apps.2"}, {"path": "z"}, {"path": "apps.10"}, {"path": "b.x"}]
```
check: paths == ["apps.10", "apps.2", "b.x", "z"]
solution: ordered = sorted(records, key=lambda r: tuple(r["path"].split(".")))
solution: paths = [r["path"] for r in ordered]
> `split(".")` turns `"apps.10"` into `("apps", "10")`; tuples compare element by element, and `"10"` is less than `"2"` as text. Sort the records, then pull out the paths.

--- fill
Complete `is_ignored` so `dock.apps` matches `dock.apps.1` but not `dock.apps_extra`.
```python
def is_ignored(path, ignore):
    return any(path == p or path.startswith(p + ___) for p in ignore)
```
answer: "."
> Appending the dot turns "starts with these letters" into "is a dotted child of". Without it `dock.apps_extra` would be silently dropped from the report.

--- teach
### Budget: 30 minutes
- 0–4: read twice, write the rules; say out loud that `1` versus `1.0` is drift.
- 4–7: `is_ignored` and `_join`; test each with two calls.
- 7–20: `diff_values`, one branch at a time: scalars first (the `changed` branch), then dicts, then lists. Try `diff_values({"a": 1}, {"a": 2})` after each branch.
- 20–25: `config_drift`: filter, sort, run the ignore tests.
- 25–30: the realistic-profile test; it exercises every branch at once.

Write the scalar branch first even though it is last in the `if` chain: every recursive call ends there, so it is the branch you can test without any nesting.

--- exercise 13.3

--- recap
- The walk is one recursive function with three shapes: dict/dict, list/list, everything else.
- Build the path on the way down with a `_join` helper; the root is `""`.
- Equal means same type AND `==`; `True` versus `1` is drift.
- Ignore with `path == p or path.startswith(p + ".")`; sort on `tuple(path.split("."))`.
