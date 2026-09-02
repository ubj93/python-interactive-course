# Capstone: log triage

--- teach
### The ticket
Two agents write to one log bucket in two formats, and the collector adds junk. A syslog line looks like `Jun  1 12:00:01 host01 munki[123]: Could not resolve repo.example.com`; the `[123]` pid is optional. A JSON line is an object with string keys `host` and `message`, plus an optional `process`. Everything else (blank lines, banners, broken JSON) is junk to skip, never to crash on. Classify each message with a rules table of `(error_class, needle)` pairs, count `(host, error_class)` pairs, and report the top `n` with deterministic tie-breaking.

Rules in your own words:
```
- parse: strip; empty is junk; "{" means JSON, else the syslog regex; host lower
- JSON: must be a dict with str host and str message, else junk
- classify: first needle found (case-insensitive) wins; None otherwise
- count: (host, class) -> n, skipping None
- top n: count desc, then host, then class
```

--- teach
### Five functions in a pipeline
```python
def log_triage(text, n=3, rules=RULES):
    records = [rec for rec in map(parse_line, text.splitlines()) if rec is not None]
    return top_offenders(count_offenders(records, rules), n)
```
- `parse_line(line)` returns a dict or `None`. It never raises.
- `classify(message, rules)` returns the class of the first matching needle, or `None`.
- `count_offenders(records, rules)` builds `{(host, error_class): count}`.
- `top_offenders(counts, n)` sorts and slices.
- `log_triage` composes them over `text.splitlines()`, which also handles CRLF.

`count_offenders` calls `classify` for you, so an unclassified record simply never becomes a key.

--- teach
### parse_line: cheap check first, regex second, None for the rest
Strip the line. Empty means junk. If it starts with `{`, try `json.loads` inside `try/except ValueError`, then check the shape with `isinstance`. Otherwise run one anchored regex with named groups; the pid group is optional.
```python
SYSLOG = re.compile(
    r"^[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+"
    r"(?P<host>\S+)\s+(?P<process>[^\s\[:]+)(?:\[\d+\])?:\s*(?P<message>.*)$"
)
m = SYSLOG.match(line)
if not m:
    return None
return {"host": m["host"].lower(), "process": m["process"], "message": m["message"].strip()}
```
`(?:\[\d+\])?` matches `[123]` when present and nothing when absent. `^` and `$` stop a partial line such as `Jun  1 12:00:01 host01` from half-matching.

--- code
Match `line` with `SYSLOG` and set `rec` to a dict with keys `host` (lowercased), `process` and `message` taken from the named groups.
```python
import re
SYSLOG = re.compile(r"^[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+(?P<host>\S+)\s+(?P<process>[^\s\[:]+)(?:\[\d+\])?:\s*(?P<message>.*)$")
line = "Jun  1 12:00:01 HOST01 munki[123]: Could not resolve repo"
```
check: rec == {"host": "host01", "process": "munki", "message": "Could not resolve repo"}
solution: m = SYSLOG.match(line)
solution: rec = {"host": m["host"].lower(), "process": m["process"], "message": m["message"].strip()}
> `m["host"]` reads a named group by name. The pid `[123]` is swallowed by the optional non-capturing group, so `process` is just `munki`. In the real function, test `if not m: return None` before touching the groups.

--- predict
What does this print?
```python
import json
obj = json.loads('["host", "message"]')
print(isinstance(obj, dict))
```
answer: False
> `json.loads` happily returns a list here: valid JSON is not the same as a valid record. Check `isinstance(obj, dict)`, then that `obj.get("host")` and `obj.get("message")` are strings, before you trust it. `{"host": 7, "message": "x"}` is junk for the same reason.

--- quiz
With the default `RULES`, what does `classify("Permission denied: no space left on device")` return?
- [x] `'auth'`
- [ ] `'disk'`
- [ ] `None`
> The rules are a list and the first pair whose needle occurs in the lowercased message wins. `("auth", "permission denied")` comes before `("disk", "no space left")`, so the answer is `auth`. Loop over the rules in order and `return` on the first hit; do not collect all matches.

--- teach
### Count with a tuple key, then sort with a tuple key
`collections.Counter` keyed by `(host, error_class)` needs no setdefault dance: `counts[(host, cls)] += 1`. Return `dict(counts)`.

For the ranking, do not reach for `Counter.most_common`: it breaks ties by insertion order, which depends on the input, not on the spec. Build `(host, error_class, count)` tuples and sort once with a key that says "count descending, then host, then class".
```python
rows = [(host, cls, count) for (host, cls), count in counts.items()]
rows.sort(key=lambda r: (-r[2], r[0], r[1]))
return rows[:n]
```
Negating the count gives descending inside an ascending sort. Slicing with `[:n]` is safe when there are fewer than `n` rows.

--- code
Set `top` to the two largest entries of `counts` as `(host, error_class, count)` tuples, ties broken by host then class.
```python
counts = {("b", "auth"): 2, ("a", "disk"): 2, ("c", "network"): 5}
```
check: top == [("c", "network", 5), ("a", "disk", 2)]
solution: rows = [(host, cls, n) for (host, cls), n in counts.items()]
solution: rows.sort(key=lambda r: (-r[2], r[0], r[1]))
solution: top = rows[:2]
> Unpack the tuple key while building the rows, sort once with the negated count first, then slice. `Counter(counts).most_common(2)` would return `("b", "auth")` for the tie because it was inserted first.

--- fill
Complete the sort key so the biggest count comes first and ties fall back to host, then class.
```python
rows.sort(key=lambda r: (___, r[0], r[1]))
```
answer: -r[2]
> `r[2]` is the count; negating it makes larger counts sort earlier while host and class still sort ascending. `reverse=True` would flip the tie-breakers too.

--- teach
### Budget: 30 minutes
- 0–4: read twice, write the rules, note the tie order.
- 4–7: signatures and `log_triage`.
- 7–17: `parse_line`. Test it on one syslog line with a pid, one without, one JSON line, and three junk lines.
- 17–22: `classify` and `count_offenders`; two records are enough.
- 22–26: `top_offenders` with a three-way tie.
- 26–30: run the suite, then the messy CRLF case.

If the regex fights you, write the JSON path and `classify` first: they are half the tests and take five minutes.

--- exercise 13.2

--- recap
- `parse_line` returns a dict or `None`; junk never raises.
- JSON: `json.loads` in `try/except ValueError`, then `isinstance` checks on the shape.
- One anchored regex with named groups and an optional pid group.
- `Counter` keyed by a tuple; rank with `key=lambda r: (-r[2], r[0], r[1])`, not `most_common`.
