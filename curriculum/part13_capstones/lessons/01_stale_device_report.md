# Capstone: stale device report

--- teach #card-0c865f285921533e
### The ticket
Security wants a weekly Markdown report of laptops that have stopped checking in. You get an inventory export as CSV text with the header `serial,hostname,user,os,last_checkin`. A device is stale when it has not checked in for more than `max_days`, or never checked in at all. The export is messy: blank lines, stray spaces, mixed case, short rows, and the same serial twice. The report is grouped by OS and must match the example in the docstring byte for byte.

Before you type any code, write the rules in your own words, in the order they apply:
```
- parse: strip everything, serial upper, hostname and user lower, skip empty serials
- duplicates: count serials seen more than once
- stale: collapse duplicates first, then never or days > max_days
- order: os, never first, oldest first, serial
- render: exact format, blank line before each section
```
That list is the docstring of each function you are about to write.

--- teach #card-19f751c2d9c750f6
### Four functions, one composer
The shape is parse, model, decide, render. Each function takes clean data from the one before it, and the composer is five lines.
```python
def stale_device_report(text, today, max_days):
    devices = parse_inventory(text)                 # parse: clean rows
    duplicates = find_duplicates(devices)           # model: {serial: count}
    stale = find_stale(devices, today, max_days)    # decide: copies with "days", sorted
    total = len({d["serial"] for d in devices})
    return render_report(stale, duplicates, today, max_days, total)
```
`parse_inventory` uses `csv.DictReader(text.splitlines())`; a missing column comes back as `None`, so normalise with `(raw.get(k) or "").strip()`. `find_stale` collapses duplicate serials before deciding, keeping the row with the newest parseable date. `render_report` only builds strings; every sort and filter happens earlier.

--- teach #card-fad135e252e65b70
### Dates: parse safely, subtract, compare
`date.fromisoformat("2024-04-01")` turns ISO text into a `date`, and raises `ValueError` on junk like `"yesterday"`. Subtracting two dates gives a `timedelta`; its `.days` is the whole number of days between them.
```python
>>> from datetime import date
>>> (date(2024, 6, 1) - date(2024, 4, 1)).days
61
```
Wrap the parse in a tiny helper that returns `None` instead of raising, so a bad date and an empty date look the same downstream: both mean "never checked in". The cutoff is strict: `days > max_days` is stale, exactly `max_days` is fresh. `today` is a parameter, never `date.today()`, or the tests cannot pin the answer.

--- code #card-70205550eb0851c5
Set `days` to `None` when `last` is `None`, otherwise to the whole number of days from `last` to `today`. Then set `stale` to `True` when the device never checked in or `days` is over `max_days`.
```python
from datetime import date
today, max_days = date(2024, 6, 1), 30
last = date(2024, 5, 2)
```
check: days == 30
check: stale is False
solution: days = None if last is None else (today - last).days
solution: stale = days is None or days > max_days
> `(today - last).days` is 30, and 30 is not greater than 30, so this device is fresh. Set `last = None` in your head: `days` is `None`, and `days is None or ...` short-circuits to `True` before the comparison could crash.

--- quiz #card-604b297c25fb5760
`today` is 2024-06-01 and `max_days` is 30. Which devices are stale?
- [ ] Only the one that last checked in on 2024-05-02 (30 days ago)
- [x] Only the one that last checked in on 2024-05-01 (31 days ago)
- [ ] Both of them
> The rule is `days > max_days`, so exactly 30 days is still fresh and 31 is stale. The tests put one device on each side of the line; get the comparison wrong and both boundary rows fail.

--- fill #card-deb97209de41540c
Complete the helper so an unparseable date becomes `None` instead of crashing the report.
```python
def _parse_date(value):
    try:
        return date.fromisoformat(value)
    except ___:
        return None
```
answer: ValueError
> `fromisoformat` raises `ValueError` for text that is not a date, including the empty string. Catch only that, so a real bug such as passing `None` (a `TypeError`) stays visible.

--- teach #card-401a2a94678f516c
### One sort key does the whole ordering
The spec says: os (case-insensitive), then never-checked-in first, then oldest first, then serial. Turn each clause into one element of a key tuple, in the same order.
```python
def key(row):
    never = row["days"] is None
    return (row["os"].lower(), 0 if never else 1, -(row["days"] or 0), row["serial"])

stale.sort(key=key)
```
`None` cannot be compared with an int, so "never" gets its own 0/1 element. "Oldest first" means days descending inside an ascending sort: negate the number instead of using `reverse=True`. Build the stale rows as copies: `{**row, "days": days}` adds the key without touching the caller's dict, and the tests check that the input was not mutated.

--- code #card-cf373e7fa7df5dc2
Sort `rows` in place using the report order: os (case-insensitive), never-checked-in first, oldest first, then serial.
```python
rows = [{"os": "macOS", "serial": "B", "days": 40}, {"os": "macOS", "serial": "A", "days": None}, {"os": "Windows", "serial": "C", "days": 92}]
```
check: [r["serial"] for r in rows] == ["A", "B", "C"]
solution: rows.sort(key=lambda r: (r["os"].lower(), 0 if r["days"] is None else 1, -(r["days"] or 0), r["serial"]))
> Four clauses, four tuple elements. `"macos"` sorts before `"windows"`, so both Mac rows come first; inside macOS, A's `None` gives it the 0 and puts it ahead of B. Lowercasing the os keeps `Windows` and `windows` together.

--- predict #card-69afee48c68a591f
What does this print?
```python
rows = [{"serial": "B", "days": 40}, {"serial": "A", "days": None}, {"serial": "C", "days": 92}]
rows.sort(key=lambda r: (0 if r["days"] is None else 1, -(r["days"] or 0), r["serial"]))
print(" ".join(r["serial"] for r in rows))
```
answer: A C B
> A has `days` None, so its key starts with 0 and it sorts first. C and B both start with 1; -92 is less than -40, so C (the oldest) comes before B.

--- teach #card-4cb003ed2edd59b0
### Budget: 35 minutes, render last
- 0–5: read twice, write the rules, note that duplicates collapse before staleness.
- 5–10: signatures, the composer, `_parse_date`.
- 10–25: `parse_inventory`, `find_duplicates`, `find_stale`, each tried on a two-row input.
- 25–33: `render_report`. Build a list of lines and join once. Put the blank line *before* each section so there is no trailing newline. Group consecutive rows by `os` (the list is already sorted). Empty cells are `-`; never-checked-in rows show `never` and `-`.
```python
lines = ["# Stale device report", "", f"Generated: {today.isoformat()}. ..."]
for group in groups:
    lines += ["", f"## {group[0]['os']} ({len(group)})", "",
              "| serial | hostname | user | last check-in | days |", "|---|---|---|---|---|"]
    ...
return "\n".join(lines)
```
- 33–35: diff your output against the docstring example line by line.

--- exercise 13.1 #card-63a98b74af595275

--- recap #card-1d026577f6375f3f
- Write the rules first; collapse duplicates before deciding staleness.
- `date.fromisoformat` in a helper that returns `None`; `(today - last).days > max_days`.
- One key tuple, one clause per element; negate for descending.
- Render from a list of lines, blank line before each section, join once.
