# JSON in and out

--- teach
### `dumps` and `loads` work on strings
`json.dumps(obj)` turns Python data into JSON text; `json.loads(text)` turns it back. The `s` means string. Python `True`, `None` and `dict` become JSON `true`, `null` and `{}`.
```python
>>> import json
>>> json.dumps({"ok": True, "issues": None})
'{"ok": true, "issues": null}'
>>> json.loads('{"n": 1}')
{'n': 1}
```
Without the `s`, `json.dump(obj, f)` and `json.load(f)` do the same with an open file.

--- predict
What does this print?
```python
import json
print(json.dumps({"ok": True, "n": None}))
```
answer: {"ok": true, "n": null}
> JSON spells booleans in lowercase and has `null` instead of `None`. Keys and strings always get double quotes.

--- teach
### Pretty, sorted, and not escaped
Three keyword arguments shape the output:
- `indent=2` puts one key per line, indented by two spaces.
- `sort_keys=True` writes keys in alphabetical order, so two runs give the same file and `diff` is clean.
- `ensure_ascii=False` keeps `Zürich` as it is instead of writing `Zürich`.
```python
json.dump(report, f, indent=2, sort_keys=True, ensure_ascii=False)
```

--- code
Print `site` as JSON so that the umlaut is kept as-is rather than escaped.
```python
import json
site = {"site": "Zürich"}
```
expect: {"site": "Zürich"}
solution: print(json.dumps(site, ensure_ascii=False))
> Without `ensure_ascii=False` the output would be `{"site": "Z\u00fcrich"}`, which is valid JSON but unreadable for humans.

--- predict
What does this print?
```python
import json
print(json.dumps({"b": 1, "a": 2}, sort_keys=True))
```
answer: {"a": 2, "b": 1}
> `sort_keys=True` orders keys alphabetically no matter what order the dict was built in.

--- teach
### `default=` handles what JSON cannot
JSON has no dates, sets or paths. `json.dump` raises `TypeError` on them unless you pass `default=fn`: a function called with each value JSON does not know, which returns something JSON does know. For anything you do not expect, raise `TypeError` yourself.
```python
def to_json(o):
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    if isinstance(o, set):
        return sorted(o)
    if isinstance(o, Path):
        return str(o)
    raise TypeError(f"cannot serialize {type(o).__name__}")
```
Check `datetime` before `date`, or just test both in one tuple: `datetime` is a subclass of `date`, and both have `isoformat()`.

--- code
Complete `to_json`: a `date` becomes `o.isoformat()`, a `set` becomes `sorted(o)`, anything else raises `TypeError`.
```python
import json
from datetime import date
def to_json(o):
```
check: to_json(date(2024, 5, 1)) == "2024-05-01"
check: json.dumps({"day": date(2024, 5, 1), "tags": {"lab", "eu"}}, default=to_json, sort_keys=True) == '{"day": "2024-05-01", "tags": ["eu", "lab"]}'
solution:     if isinstance(o, date):
solution:         return o.isoformat()
solution:     if isinstance(o, set):
solution:         return sorted(o)
solution:     raise TypeError(f"cannot serialize {type(o).__name__}")
> `json.dumps` calls `to_json` once for the date and once for the set. Each branch returns something JSON can encode; the final `raise` keeps unknown types loud.

--- fill
Complete the call so dates and sets are converted by `to_json`.
```python
json.dump(report, f, indent=2, sort_keys=True, ensure_ascii=False, default=___)
```
answer: to_json
> Pass the function itself, not `to_json()`. `json.dump` calls it once per value it cannot encode.

--- quiz
`to_json` is called with a value it does not recognise. What should it do?
- [ ] Return `None`
- [ ] Return `str(o)`
- [x] Raise `TypeError`
> Raising `TypeError` is the contract: `json.dump` reports the problem instead of silently writing `null` or a guessed string.

--- teach
### The trailing newline is yours to write
`json.dump` writes no newline at the end. Tools like `diff` and `git` want one, so write it yourself after the dump. Reading back is `json.load(f)`; a missing file raises `FileNotFoundError` from `open`, which is what the caller wants to see.
```python
with open(path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, sort_keys=True, ensure_ascii=False, default=to_json)
    f.write("\n")
```
Mode `"w"` creates the file, or empties it if it already exists.

--- exercise 6.4

--- recap
- `dumps`/`loads` for strings, `dump`/`load` for files.
- `indent=2, sort_keys=True, ensure_ascii=False` gives pretty, stable, readable output.
- `default=fn` converts dates, sets and paths; unknown types raise `TypeError`.
- `json.dump` adds no final newline; `f.write("\n")` does.
