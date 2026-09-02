# Missing, empty, or broken

--- teach
### Three situations, three answers
A state file can be missing (normal on a fresh machine), empty (created, never written), or broken (someone edited it by hand). The first two return the default; the third must fail loudly, because starting over would lose data. Good error handling starts by naming the cases.
```python
def read_json_or_default(path, default):
    # missing  -> default
    # empty    -> default
    # broken   -> ValueError naming the file
    # anything else the OS refuses -> let it propagate
```

--- teach
### Catch `FileNotFoundError`, and only that
Wrap just the `open` in `try`. `except FileNotFoundError` covers the missing file. Do **not** write `except OSError` or `except Exception`: a permission problem or a directory in place of the file is a real fault that should surface, and the last test checks it does.
```python
try:
    with open(path, encoding="utf-8") as f:
        text = f.read()
except FileNotFoundError:
    return copy.deepcopy(default)
```

--- fill
Complete the clause so only a missing file returns the default.
```python
try:
    with open(path, encoding="utf-8") as f:
        text = f.read()
except ___:
    return copy.deepcopy(default)
```
answer: FileNotFoundError
> `FileNotFoundError` is the one exception that means "no state yet". Its parent `OSError` would also swallow permission errors, which the spec says to let through.

--- quiz
The path points at a directory, so `open` raises `IsADirectoryError`. What should `read_json_or_default` do?
- [ ] Return the default
- [x] Let the exception propagate
- [ ] Raise `ValueError` naming the path
> Only a missing file means "no state". A directory in the way is a real problem; because you caught `FileNotFoundError` and nothing wider, it propagates on its own.

--- teach
### Empty means "no state yet"
After reading, `text.strip()` is `""` for an empty or whitespace-only file. Return the default rather than letting `json.loads("")` fail.
```python
if not text.strip():
    return copy.deepcopy(default)
```

--- code
Set `state` to a deep copy of `default` when `text` is blank, otherwise to the parsed JSON.
```python
import copy, json
text = " \n\t"
default = {"devices": []}
```
check: state == {"devices": []}
check: state is not default
solution: if not text.strip():
solution:     state = copy.deepcopy(default)
solution: else:
solution:     state = json.loads(text)
> `text.strip()` is empty, so the default branch runs. `deepcopy` makes `state` a separate object; `state is not default` proves it.

--- teach
### Broken JSON: re-raise with the file name
`json.loads` on bad text raises `json.JSONDecodeError`, which is a subclass of `ValueError`. Catch it and raise a new `ValueError` whose message contains the path, chained with `from e`, so the reader knows which file to fix and still sees the original position information.
```python
try:
    return json.loads(text)
except json.JSONDecodeError as e:
    raise ValueError(f"{path}: invalid JSON ({e})") from e
```

--- predict
What does this print?
```python
import json
try:
    json.loads('{"n": ')
except ValueError as e:
    print(type(e).__name__)
```
answer: JSONDecodeError
> `JSONDecodeError` inherits from `ValueError`, so `except ValueError` catches it, and the object's own class name is still `JSONDecodeError`.

--- teach
### Return a deep copy of the default
If you return `default` itself, the caller who does `state["devices"].append(...)` changes the default for the next caller. `copy.deepcopy(default)` returns a fresh copy, including nested lists and dicts.
```python
>>> import copy
>>> default = {"devices": []}
>>> mine = copy.deepcopy(default)
>>> mine["devices"].append("C02XG1234ABC")
>>> default
{'devices': []}
```

--- predict
What does this print?
```python
import copy
default = {"seen": {"count": 0}}
first = copy.deepcopy(default)
first["seen"]["count"] = 99
print(default)
```
answer: {'seen': {'count': 0}}
> `deepcopy` copies the nested dict too, so writing into the copy leaves the original untouched. A plain `dict(default)` would share the inner dict.

--- exercise 7.4

--- recap
- Name the cases first: missing, empty, broken, and "everything else".
- `except FileNotFoundError:` only; wider clauses hide real faults.
- Empty text returns the default without calling `json.loads`.
- `json.JSONDecodeError` is a `ValueError`; re-raise with the path, `from e`.
- Return `copy.deepcopy(default)` so callers cannot corrupt it.
