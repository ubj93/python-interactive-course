# Part 13 · Capstones: timed, realistic problems

> **What you will be able to do:** take a one-page spec that looks like a real CPE
> ticket or take-home, turn it into four or five small functions, handle the messy
> data that real exports contain, and produce output in exactly the format asked for,
> inside an interview time budget. Each capstone is 3–4 kyu and its `time_limit_min`
> is the real budget: 30–50 minutes. Plan on five to six hours for the whole part.

## Why capstones

Parts 1–12 drilled one skill at a time. A real interview problem is never that clean.
A CPE take-home reads like this:

> Here is an inventory export as CSV. Produce a Markdown report of devices that have
> not checked in for 30 days, grouped by OS. Watch out for duplicate serials.

Nothing in that sentence is hard. What is hard is doing all of it, correctly, under
time, while the data has blank lines, `C02abc` next to `C02ABC`, a date column that
is sometimes empty, and a reviewer who will diff your output against theirs
character by character. This part is about the *process* that gets you there.

## 1. Read the spec twice, then write the rules down

Do not open the editor yet. Read the whole problem, then write the rules as a bullet
list in your own words, in the order they apply. For the stale-device ticket above:

```
- input: CSV text, header serial,hostname,user,os,last_checkin
- normalise: serial upper, hostname/user lower, strip everything, skip blank rows
- duplicate serial: keep the newest check-in, list the serial in a "duplicates" section
- stale: never checked in, OR (today - last_checkin).days > N   (exactly N is fresh)
- group by os; within a group never-checked-in first, then oldest first, then serial
- output: Markdown, exact header line, one table per os, no trailing newline
```

Three things happen when you do this. You find the questions you need to ask ("is
exactly 30 days stale?"), you discover the precedence between rules (a duplicate
must be collapsed *before* deciding staleness), and you now have the docstring for
each function. In an on-site, say the list out loud; the interviewer will correct
a wrong assumption before it costs you twenty minutes.

## 2. The four-function shape: parse → model → decide → render

Almost every fleet problem decomposes the same way:

| Stage | Takes | Returns | Typical name |
|---|---|---|---|
| parse | raw text or raw dicts | clean, normalised records | `parse_inventory`, `parse_line` |
| model | clean records | an index: dict by key, sets, counts | `index_by_serial`, `count_offenders` |
| decide | the index plus parameters (`today`, thresholds) | the answer as plain data | `find_stale`, `decide`, `diff_values` |
| render | the answer | a string, a list of dicts, a JSON-ready dict | `render_report`, `top_offenders` |

Then one top-level function composes them in four lines. This is not ceremony:

- Each stage is testable on its own with a five-line input. When the report is wrong
  you know within a minute whether parsing, deciding or rendering is at fault.
- `today`, `now` and thresholds are **parameters**, never `date.today()` inside a
  function. That is what makes the decide stage testable at all.
- The render stage never computes anything. If you find yourself sorting or
  filtering while building strings, move that code up one stage.

```python
def stale_device_report(text: str, today: date, max_days: int) -> str:
    devices = parse_inventory(text)
    duplicates = find_duplicates(devices)
    stale = find_stale(devices, today, max_days)
    return render_report(stale, duplicates, today, max_days, total=len({d["serial"] for d in devices}))
```

A reviewer reads that and knows the whole design. The tests in this part grade each
stage separately, so a working parser earns credit even when the report is off by a
newline.

## 3. Choosing the data structure

The choice is usually forced by the question you have to answer:

| You need to... | Use | Because |
|---|---|---|
| look a record up by serial | `dict` keyed by the normalised serial | O(1) and it makes duplicates visible (`if serial in seen`) |
| test membership ("is this user active?") | `set` | `in` is O(1); set algebra gives you `&`, `|`, `-` for free |
| count things | `collections.Counter` keyed by a tuple | `counts[(host, cls)] += 1` with no setdefault dance |
| keep first-seen order without duplicates | a list plus a `seen` set | dicts preserve insertion order too: `list(dict.fromkeys(items))` |
| produce a report | a `sorted(...)` list with a tuple key | deterministic, and the key documents the ordering rule |
| walk nested config | recursion with the path as a parameter | the path string is built on the way down, records collected on the way up |
| resolve includes / dependencies | DFS with `done` and `path` sets | `done` handles diamonds, `path` detects cycles; they are different sets |

Sort keys deserve a sentence in your head before you type them. "Group by OS, never
first, then oldest first, then serial" becomes:

```python
key=lambda r: (r["os"].lower(), 0 if r["days"] is None else 1, -(r["days"] or 0), r["serial"])
```

Every clause of the sentence is one element of the tuple, in the same order. `None`
cannot be compared with an int, so it gets its own 0/1 element. Descending on one
field inside an ascending sort is a negated number, not `reverse=True`.

## 4. Messy data: normalise at the boundary, once

Real exports contain every one of these, and every capstone tests for them:

| Mess | Fix | Where |
|---|---|---|
| blank lines, `,,,,` rows | skip when the key field is empty after strip | parse |
| short rows (missing trailing columns) | `csv.DictReader` gives `None`: `(row.get(k) or "").strip()` | parse |
| `C02abc` vs `C02ABC ` | `.strip().upper()` for serials, `.strip().lower()` for users, hosts, ring labels | parse |
| `None` where a string should be | `(value or "")` before any string method | parse |
| the same key twice | decide the rule up front: first wins, newest wins, or flag it | model |
| an unparseable date | a tiny helper that returns `None` instead of raising | parse or decide |
| CRLF line endings | `text.splitlines()` (not `split("\n")`) | parse |
| junk lines in a log | return `None` from `parse_line`, filter with `if rec is not None` | parse |

Write two normalisers at the top of the file and call them everywhere:

```python
def _serial(value) -> str:
    return (value or "").strip().upper()

def _user(value) -> str:
    return (value or "").strip().lower()
```

Once every serial passes through `_serial` on the way in, nothing downstream thinks
about casing again. Normalising in three different places is how `c02abc` ends up
as its own device in the report.

**Gotchas that interviewers probe here**

- `datetime.fromisoformat("2024-06-01T10:00:00Z")` raises on Python 3.9: the trailing
  `Z` is not accepted until 3.11. Strip it or replace it with `+00:00`.
  `date.fromisoformat("2024-06-01")` is fine everywhere.
- `Counter.most_common()` breaks ties by insertion order, which depends on the input.
  When the spec says "ties by host name", sort yourself with a tuple key.
- `True == 1` and `1 == 1.0` are true. A config diff that must notice a boolean
  turning into an int needs `type(a) is not type(b) or a != b`.
- Do not mutate the caller's dicts. `{**row, "days": 61}` makes a copy with one
  extra key; `row["days"] = 61` changes the input that a later stage still reads.
- `dict` iteration order is insertion order (3.7+), so "in the order the rows arrive"
  is free, but `set` order is not: sort before you emit anything from a set.

## 5. The output format is part of the spec

If the ticket shows an example report, your output must match it byte for byte.
The reliable way is to build a list of lines and join once at the end:

```python
lines = ["# Stale device report", "", f"Generated: {today.isoformat()}. Cutoff: {max_days} days."]
for os_name, rows in groups:
    lines += ["", f"## {os_name} ({len(rows)})", "", "| serial | hostname | days |", "|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['serial']} | {r['hostname'] or '-'} | {r['days'] if r['days'] is not None else '-'} |")
return "\n".join(lines)
```

- Put the blank line *before* each section, not after: no trailing newline problem.
- Empty cells: decide on `-` (or whatever the example shows) and apply it in one place.
- Numbers: `f"{x:.1f}"`, `f"{n:,}"`, and integer maths for anything that must be
  reproducible. `(n * pct + 99) // 100` is ceil without floats;
  `math.ceil(n * pct / 100)` can give a different answer for some inputs.
- Do not `print`. Return the string; the caller decides where it goes.

## 6. Self-test with tiny inputs before you run the suite

Before touching the provided tests, feed each function the smallest input that
exercises one rule and look at the answer:

```python
>>> parse_inventory("serial,hostname,user,os,last_checkin\n c02abc ,MBP-A,Alice,macOS,2024-04-01\n")
[{'serial': 'C02ABC', 'hostname': 'mbp-a', 'user': 'alice', 'os': 'macOS', 'last_checkin': '2024-04-01'}]
>>> find_stale(_, date(2024, 6, 1), 30)[0]["days"]
61
>>> find_stale(_, date(2024, 6, 1), 61)
[]
```

Two rows per rule is enough: one just inside the boundary, one just outside. Then
one "everything at once" input for the composed function. This is the same order the
test files use: helpers first, then the composed function, then the messy case.

## 7. Worked example: licence seat audit

A task in the same family as the six capstones, decomposed start to finish. The
ticket: *"Given a CSV export of installed apps (`serial,user,app,version`) and the
licence roster (`{app: [licensed users]}`), report per app how many seats are used
and which users are unlicensed. Same user on two machines is one seat. App names
and users are case-insensitive. Output Markdown, apps alphabetical."*

**Rules written down**

```
- parse rows; skip blank / missing user or app; user lower, app lower, serial upper
- seat = distinct (app, user); a user on two machines is one seat
- unlicensed = seat users not in roster[app] (roster users lowercased too)
- an app with installs but no roster entry: every user is unlicensed
- output: "## <app>: <seats> seats, <n> unlicensed" then "- user" lines sorted
```

**Parse**

```python
def parse_installs(text: str) -> List[Dict[str, str]]:
    rows = []
    for raw in csv.DictReader(text.splitlines()):
        row = {k: (raw.get(k) or "").strip() for k in ("serial", "user", "app", "version")}
        if not row["user"] or not row["app"]:
            continue
        row["user"], row["app"], row["serial"] = row["user"].lower(), row["app"].lower(), row["serial"].upper()
        rows.append(row)
    return rows
```

**Model**: the question is "which users per app", so a dict of sets.

```python
def seats_by_app(rows: List[Dict[str, str]]) -> Dict[str, Set[str]]:
    seats: Dict[str, Set[str]] = {}
    for row in rows:
        seats.setdefault(row["app"], set()).add(row["user"])
    return seats
```

**Decide**: set difference, with the roster normalised the same way.

```python
def unlicensed(seats: Dict[str, Set[str]], roster: Dict[str, List[str]]) -> Dict[str, List[str]]:
    licensed = {app.lower(): {u.lower() for u in users} for app, users in roster.items()}
    return {app: sorted(users - licensed.get(app, set())) for app, users in seats.items()}
```

**Render**: strings only, from data that is already decided and sortable.

```python
def render_audit(seats: Dict[str, Set[str]], bad: Dict[str, List[str]]) -> str:
    lines = []
    for app in sorted(seats):
        lines += ["", f"## {app}: {len(seats[app])} seats, {len(bad[app])} unlicensed"]
        lines += [f"- {u}" for u in bad[app]]
    return "\n".join(lines[1:])
```

**Compose**, then test each stage with two-row inputs: one licensed user, one not;
the same user on two serials; an app missing from the roster. Twenty minutes, four
functions, and every rule from the list maps to one line of code you can point at.

## 8. Spending the time budget

For a 40-minute problem:

| Minutes | Do |
|---|---|
| 0–5 | read twice, write the rules, ask or state assumptions |
| 5–10 | write the function signatures and the compose function; stub the rest |
| 10–30 | fill in parse → model → decide → render, testing each with tiny inputs |
| 30–37 | run the real tests; fix format and ordering issues |
| 37–40 | re-read the spec against your output; say what you would do with more time |

If you are running out of time, ship a working parse and decide stage with a rough
render, and say so. Partial, correct, and explained beats complete and wrong.

## Interview notes for this part

**Take-homes.** Reviewers open the repository, read the README, run the tests, then
read the code. In that order. So:

- `README.md`: one paragraph on what it does, how to run it, the assumptions you made
  (the rules list from section 1, cleaned up), and what you would do next.
- Tests: a `test_*.py` using `unittest` or `pytest`, one test per rule, including the
  messy-data cases. Tests are the strongest signal that you thought about edge cases.
- An entry point: `python report.py inventory.csv --days 30 --today 2024-06-01` via
  `argparse`, with `main()` calling the same composed function the tests call.
  Reading the file happens in `main`; every other function takes text or data in.
- Standard library only unless the brief says otherwise. Type hints on public
  functions. No classes unless state genuinely needs to live somewhere.
- Do not over-engineer. No plugin systems, no abstract base classes, no config
  framework, no logging setup for a 150-line script. A reviewer's favourite
  sentence is "this does exactly what was asked and nothing else".

**On-sites.** Narrate the rules, name the data structure and why, write the compose
function first so the shape is visible, and run something after every function. When
you hit an ambiguity, say the two options and pick one out loud. Ask what the output
is used for: "is this for a human or a script?" changes whether you return Markdown
or a list of dicts.

**The trap.** Starting with the render stage because the example output is the most
concrete part of the spec. You end up computing inside f-strings, cannot test
anything until it all works, and lose the last ten minutes to a sort order bug you
cannot isolate. Parse first, render last.

## Exercises

Run `course list 13`, then `course show 13.1`. Start a timer against `time_limit_min`.
Write the rules down before you code, and read the tests: they are the acceptance
criteria.

1. `stale_device_report` (4 kyu, 35 min) · CSV text in, grouped Markdown report out; cutoff rules, duplicate serials, exact format
2. `log_triage` (4 kyu, 30 min) · mixed syslog and JSON lines with junk; rules table; top offenders with deterministic ties
3. `config_drift` (4 kyu, 30 min) · expected vs actual nested configs; dotted paths; missing/extra/changed; ignore prefixes
4. `enrollment_reconciler` (3 kyu, 45 min) · MDM, directory and inventory disagree; a numbered rule ladder to enroll/retire/reassign/investigate
5. `rollout_planner` (3 kyu, 45 min) · rings, cumulative percentages, blockers and OS-version holds; integer rounding; day-by-day schedule
6. `manifest_resolver` (3 kyu, 45 min) · Munki-style includes resolved depth-first with cycle detection; install/uninstall conflicts; optional catalog
