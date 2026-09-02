# Dates that know their time zone

--- teach
### Naive and aware datetimes
A `datetime` is a date plus a time. A **naive** one has no time zone; an **aware** one carries `tzinfo`, the zone it belongs to. Python refuses to mix the two, because "10:00" without a zone is not an instant in time.
```python
>>> from datetime import datetime, timezone
>>> naive = datetime(2024, 5, 1, 10, 0)
>>> aware = datetime(2024, 5, 1, 10, 0, tzinfo=timezone.utc)
>>> naive.tzinfo is None
True
>>> aware - naive
TypeError: can't subtract offset-naive and offset-aware datetimes
```
Fleet scripts hit this bug all the time: an aware "now" minus a naive "last check-in".

--- quiz
`then` is naive and `now` is aware. What does `now - then` do?
- [ ] Returns a `timedelta`, assuming UTC for `then`
- [x] Raises `TypeError`
- [ ] Returns `None`
> Python never guesses a zone. Make both values aware first, then subtract.

--- teach
### Parsing ISO 8601 with `fromisoformat`
`datetime.fromisoformat` reads the `2024-05-01T10:00:00+02:00` shape and keeps the offset, so the result is aware. A string with no offset gives a naive result. On Python 3.9 the trailing `Z` (which means UTC) is rejected, so swap it for `+00:00` first.
```python
>>> datetime.fromisoformat("2024-05-01T10:00:00+02:00").tzinfo is None
False
>>> datetime.fromisoformat("2024-05-01 10:00:00").tzinfo is None
True
>>> s = "2024-05-01T10:00:00Z"
>>> if s.endswith("Z"):
...     s = s[:-1] + "+00:00"
```
Anything it cannot read raises `ValueError`, which is exactly what the exercise wants for garbage input.

--- fill
Complete the line that turns a trailing `Z` into an offset `fromisoformat` accepts.
```python
if s.endswith("Z"):
    s = s[:-1] + "___"
```
answer: +00:00
> `s[:-1]` drops the last character; `+00:00` is the explicit way to write "UTC, no offset".

--- teach
### Label a naive value, convert an aware one
Two methods look alike and do opposite jobs. `replace(tzinfo=timezone.utc)` **labels** a naive datetime as UTC without changing the numbers. `astimezone(timezone.utc)` **converts** an aware datetime to UTC, so 12:00 at +02:00 becomes 10:00.
```python
>>> naive.replace(tzinfo=timezone.utc)
datetime.datetime(2024, 5, 1, 10, 0, tzinfo=datetime.timezone.utc)
>>> datetime.fromisoformat("2024-05-01T12:00:00+02:00").astimezone(timezone.utc)
datetime.datetime(2024, 5, 1, 10, 0, tzinfo=datetime.timezone.utc)
```
So: if `dt.tzinfo is None`, label it; then convert with `astimezone`. Converting something already in UTC changes nothing.

--- code
Set `utc` to the timestamp parsed from `raw`, converted to UTC. It should read 10:00 UTC and be aware.
```python
from datetime import datetime, timezone
raw = "2024-05-01T12:00:00+02:00"
```
check: utc == datetime(2024, 5, 1, 10, 0, tzinfo=timezone.utc)
check: utc.tzinfo == timezone.utc
solution: utc = datetime.fromisoformat(raw).astimezone(timezone.utc)
> `fromisoformat` keeps the `+02:00` offset, so the value is already aware; `astimezone(timezone.utc)` converts 12:00+02:00 to 10:00 UTC.

--- predict
What does this print?
```python
from datetime import datetime, timezone
dt = datetime.fromisoformat("2024-05-01T12:00:00+02:00")
print(dt.astimezone(timezone.utc).hour)
```
answer: 10
> 12:00 at two hours ahead of UTC is 10:00 in UTC. `astimezone` converts; it does not just relabel.

--- teach
### Subtracting gives a `timedelta`
Two aware datetimes subtract to a `timedelta`. Its `.days` is the whole-day part, rounded down (2 days 23 hours is 2). A future timestamp gives a negative delta, and `.days` rounds toward minus infinity, so minus one hour reads as `-1`. Clamp with `max(0, ...)`.
```python
>>> delta = datetime(2024, 5, 4, 9, 0) - datetime(2024, 5, 1, 10, 0)
>>> delta.days
2
>>> max(0, (datetime(2024, 5, 1) - datetime(2024, 5, 9)).days)
0
```

--- predict
What does this print?
```python
from datetime import datetime
print((datetime(2024, 5, 4, 9, 0) - datetime(2024, 5, 1, 10, 0)).days)
```
answer: 2
> The gap is 2 days and 23 hours. `.days` keeps the whole days only.

--- teach
### Inject the clock
A function that calls `datetime.now()` inside gives a different answer every run, so a test cannot pin it. Instead, take `now` as a parameter and let the caller pass it. Tests pass a fixed aware datetime; production passes `datetime.now(timezone.utc)`.
```python
def days_since(raw, now):
    then = parse_timestamp(raw)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return max(0, (now - then).days)

days_since("2024-05-01T10:00:00Z", now=datetime(2024, 5, 4, 9, 0, tzinfo=timezone.utc))
```
You will meet this idea again with `runner`, `sleep` and `client`: whatever touches the outside world comes in as an argument.

--- quiz
Why does `days_since(raw, now)` take `now` as a parameter instead of calling `datetime.now()`?
- [ ] `datetime.now()` is slower
- [x] So a test can pass a fixed instant and get the same answer every run
- [ ] `datetime.now()` cannot return an aware value
> A test needs a deterministic result. The caller owns the clock; the function only does maths.

--- exercise 10.1

--- recap
- Aware datetimes carry `tzinfo`; mixing them with naive ones raises `TypeError`.
- `fromisoformat` parses ISO 8601; replace a trailing `Z` with `+00:00` first.
- `replace(tzinfo=...)` labels a naive value; `astimezone(...)` converts an aware one.
- `(now - then).days` rounds down; `max(0, ...)` clamps the future.
- Take `now` as a parameter so tests never touch the wall clock.
