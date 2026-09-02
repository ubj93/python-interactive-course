# Part 10 · Standard-library toolkit

> **What you will be able to do:** reach for the right standard-library module
> without looking it up: parse timestamps correctly across time zones, build a
> command-line interface, hash a file, shell out safely, keep a sliding window, and
> count and group things with `collections`. Plan on two to three hours including
> the exercises.

## Why this part matters

Most CPE scripts are glue: read a timestamp from an MDM, run `profiles` or
`osqueryi`, hash a package, count something, print a report. None of that needs a
third-party package. Interviewers notice when you know `datetime` handles offsets,
`argparse` handles validation, and `subprocess.run` handles capturing output, and
they notice even more when you can make that code testable. Every exercise here
takes an injected dependency (`now`, `runner`) so the tests never touch the wall
clock or a real process. That injection habit is the single most valuable thing in
this part.

## 1. datetime: aware vs naive

A **naive** datetime has no time zone. An **aware** one carries `tzinfo`. Mixing them
is an error, and comparing a naive "last check-in" against an aware "now" is the
most common datetime bug in fleet scripts.

```python
>>> from datetime import datetime, timedelta, timezone
>>> naive = datetime(2024, 5, 1, 10, 0)
>>> aware = datetime(2024, 5, 1, 10, 0, tzinfo=timezone.utc)
>>> naive.tzinfo is None, aware.tzinfo
(True, datetime.timezone.utc)
>>> aware - naive
TypeError: can't subtract offset-naive and offset-aware datetimes
>>> naive.replace(tzinfo=timezone.utc) == aware       # attach a zone, no conversion
True
```

`replace(tzinfo=...)` *labels* a naive value; `astimezone(...)` *converts* an aware
one. Do not confuse them.

### Parsing ISO 8601

```python
>>> datetime.fromisoformat("2024-05-01T10:00:00+02:00")
datetime.datetime(2024, 5, 1, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=7200)))
>>> datetime.fromisoformat("2024-05-01T10:00:00+02:00").astimezone(timezone.utc)
datetime.datetime(2024, 5, 1, 8, 0, tzinfo=datetime.timezone.utc)
>>> datetime.fromisoformat("2024-05-01 10:00:00")     # a space works too; result is naive
datetime.datetime(2024, 5, 1, 10, 0)
```

**Gotcha:** on Python 3.9 and 3.10, `fromisoformat` rejects the `Z` suffix that every
API on earth uses (`"2024-05-01T10:00:00Z"` raises `ValueError`). 3.11 accepts it. The
portable fix is one line:

```python
if raw.endswith("Z"):
    raw = raw[:-1] + "+00:00"
```

`strptime` is the older tool: `datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")`. Its
`%z` accepts `Z` and `+02:00` since 3.7, but you must know the exact shape of the
input, and it is slower. Reach for `fromisoformat` first.

### Arithmetic and formatting

```python
>>> now = datetime(2024, 5, 4, 9, 0, tzinfo=timezone.utc)
>>> then = datetime(2024, 5, 1, 10, 0, tzinfo=timezone.utc)
>>> delta = now - then
>>> delta, delta.days, delta.total_seconds()
(datetime.timedelta(days=2, seconds=82800), 2, 255600.0)
>>> now - timedelta(days=30)
datetime.datetime(2024, 4, 4, 9, 0, tzinfo=datetime.timezone.utc)
>>> now.strftime("%Y-%m-%d %H:%M")
'2024-05-04 09:00'
>>> now.isoformat()
'2024-05-04T09:00:00+00:00'
>>> now.date(), now.timestamp()
(datetime.date(2024, 5, 4), 1714813200.0)
```

`timedelta.days` rounds toward negative infinity: a delta of minus one hour has
`days == -1`. Clamp with `max(0, ...)` when "in the future" should read as zero.

| You want | Write | Not |
|---|---|---|
| the current instant, aware | `datetime.now(timezone.utc)` | `datetime.utcnow()` (naive, deprecated in 3.12) |
| a named zone | `zoneinfo.ZoneInfo("Europe/Helsinki")` (3.9+) | `pytz` |
| a testable "now" | `def f(..., now=None): now = now or datetime.now(timezone.utc)` | calling `datetime.now()` deep inside |

## 2. argparse: the interface of a script

```python
import argparse

parser = argparse.ArgumentParser(prog="devreport", description="Report on one device.")
parser.add_argument("serial")                                            # positional, required
parser.add_argument("--format", choices=["table", "json", "csv"], default="table")
parser.add_argument("--days", type=int, default=30)
parser.add_argument("--tag", dest="tags", action="append", default=[])   # repeatable
parser.add_argument("-v", "--verbose", action="store_true")
group = parser.add_mutually_exclusive_group()
group.add_argument("--online", action="store_true")
group.add_argument("--offline", action="store_true")

ns = parser.parse_args(["C02XG1234ABC", "--days", "7", "--tag", "lab"])
ns.serial, ns.days, ns.tags, ns.format          # ('C02XG1234ABC', 7, ['lab'], 'table')
```

Points that come up in interviews:

- `type=int` converts *and* validates. A bad value becomes a usage error with a
  proper message; you do not write the `try/except`. A custom callable that raises
  `argparse.ArgumentTypeError` gives you the same treatment for your own rules.
- `choices` validates; `default` fills in; `required=True` on an option forces it,
  but "required options" are a smell: make it positional or give it a default.
- `parse_args(argv)` with an **explicit list** is what makes a CLI testable. Only
  the `if __name__ == "__main__":` block should call `parse_args()` with no
  argument (which reads `sys.argv[1:]`).
- Errors go through `parser.error(...)`, which prints usage to stderr and raises
  `SystemExit(2)`. Let it. Tests use `assertRaises(SystemExit)`.
- Subcommands: `sub = parser.add_subparsers(dest="command")`, then
  `sub.add_parser("list")`. Check `ns.command is None` when no subcommand was given.

**Gotcha:** `action="append"` with `default=[]` shares that list across parses of the
*same parser object* on old Pythons. Build the parser inside a function and call it
fresh each time; it also keeps tests independent.

## 3. hashlib: verifying downloads

```python
>>> import hashlib
>>> hashlib.sha256(b"hello world").hexdigest()
'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'
>>> h = hashlib.sha256()
>>> h.update(b"hello ")
>>> h.update(b"world")
>>> h.hexdigest()
'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'
```

The hash object accumulates, so a multi-gigabyte installer is hashed in fixed-size
pieces:

```python
def sha256_file(path, chunk_size=65536):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):   # two-arg iter: call until sentinel
            h.update(chunk)
    return h.hexdigest()
```

- Hash **bytes**, never `str`: `hashlib.sha256("text")` is a `TypeError`. Encode first.
- Compare digests as lowercase strings; vendors publish uppercase, with whitespace,
  sometimes prefixed `sha256:`.
- `hashlib.file_digest(f, "sha256")` exists from 3.11 and does the loop for you.
- `md5` is fine for cache keys, not for integrity. Say so when asked.

## 4. subprocess: shelling out without shooting yourself

```python
>>> import subprocess, shlex
>>> proc = subprocess.run(["sw_vers", "-productVersion"], capture_output=True, text=True, timeout=30)
>>> proc.returncode, proc.stdout, proc.stderr
(0, '14.5\n', '')
>>> shlex.split('osqueryi --json "select * from users"')
['osqueryi', '--json', 'select * from users']
```

| Parameter | Effect |
|---|---|
| `capture_output=True` | fills `.stdout` and `.stderr` instead of inheriting the terminal |
| `text=True` | decode to `str` (else you get `bytes`) |
| `check=True` | raise `CalledProcessError` on non-zero exit |
| `timeout=30` | raise `TimeoutExpired` (and kill the child) after 30 s |
| `input="..."` | feed stdin |
| `shell=True` | run through `/bin/sh`: **avoid**; injection risk and quoting pain |

Pass a **list** of arguments. If you are given a string, `shlex.split` turns it into
a list correctly (quotes, escapes). `shlex.join` goes the other way for log messages.

**Testability.** Real processes are slow, platform-specific and side-effectful, so
the function takes the runner as a parameter:

```python
def run_command(cmd, runner=subprocess.run, timeout=30):
    argv = shlex.split(cmd) if isinstance(cmd, str) else list(cmd)
    proc = runner(argv, capture_output=True, text=True, timeout=timeout)
    ...

# in a test
def fake(argv, **kwargs):
    return subprocess.CompletedProcess(argv, 0, stdout='[{"uid":"501"}]', stderr="")
run_command(["osqueryi", "--json", "select uid from users"], runner=fake)
```

Nothing executes, the fake records what it was asked to run, and the test can assert
the exact argv. Interviewers ask "how would you test this?" and this is the answer.

## 5. logging in three lines

```python
import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log.info("checked in %s devices", 42)      # lazy formatting: use %s, not f-strings
log.warning("device %s stale for %d days", serial, days)
log.exception("install failed")            # inside an except block: adds the traceback
```

Modules call `getLogger(__name__)` and never `basicConfig`; the entry point script
configures once. `print` is for program output, `logging` is for diagnostics; keep
them apart so `--format json` output stays parseable.

## 6. os, sys, shutil, tempfile, pathlib

```python
>>> import os, sys, shutil, tempfile, platform
>>> os.environ.get("JAMF_URL", "https://jamf.example.com")   # never os.environ["X"] without a default in a script
>>> sys.argv, sys.exit(1), sys.stdin.read()                   # program interface
>>> sys.platform                                              # 'darwin', 'linux', 'win32'
>>> platform.system(), platform.mac_ver()[0], platform.machine()
('Darwin', '14.5', 'arm64')
>>> shutil.which("osqueryi")                                  # path or None; check before subprocess
>>> shutil.copy2(src, dst); shutil.rmtree(path); shutil.disk_usage("/")
>>> with tempfile.TemporaryDirectory() as tmp:                # cleaned up on exit
...     path = os.path.join(tmp, "pkg.dmg")
```

Prefer `pathlib.Path` for paths (`Path.home() / "Library"`, `.read_text()`,
`.exists()`), `os.path` when you are in old code, and `tempfile` in tests instead of
writing to the project folder.

## 7. collections: the four you need cold

```python
>>> from collections import Counter, defaultdict, deque, namedtuple
>>> Counter(["Slack", "Zoom", "Slack"])
Counter({'Slack': 2, 'Zoom': 1})
>>> Counter(["Slack", "Zoom", "Slack"]).most_common(1)
[('Slack', 2)]
>>> c = Counter(); c["x"] += 1; c["missing"]        # missing keys read as 0, no KeyError
0
>>> groups = defaultdict(list); groups["eng"].append("mbp-1")   # first access creates the list
>>> dict(groups)                                   # freeze before returning; callers expect KeyError
{'eng': ['mbp-1']}
>>> window = deque(maxlen=3)
>>> for x in [1, 2, 3, 4]: window.append(x)
>>> list(window)                                   # oldest dropped automatically
[2, 3, 4]
>>> Device = namedtuple("Device", "serial name")
>>> Device("C02X", "mbp-1").serial
'C02X'
```

- `Counter.most_common()` orders **ties by first insertion**. When output must be
  stable, sort `.items()` yourself with `key=lambda kv: (-kv[1], kv[0])`.
- `defaultdict` creates keys on *read*, so `if key in d` after a lookup lies to you.
  Convert to `dict` before handing it out.
- `deque` is O(1) at both ends; a list is O(n) for `pop(0)`. Use it for sliding
  windows, tail -n, and BFS queues.
- `namedtuple` is a lightweight record; for anything with defaults or methods use
  `@dataclass` (Part 8).

## 8. uuid, and things people ask about

```python
>>> import uuid
>>> str(uuid.uuid4())                       # random id for a request or a job
'0f4e9c1a-3d0b-4d9a-9f4e-2b6c9c2a4a11'
>>> uuid.uuid5(uuid.NAMESPACE_DNS, "mbp-1.corp.example.com")   # deterministic from a name
```

`uuid4` for identifiers you will store, `uuid5` when the same input must map to the
same id, `secrets.token_hex(16)` when it has to be unguessable.

## Interview notes for this part

- **Say "aware" out loud.** "I will parse into an aware UTC datetime and compare with
  an aware now." Then handle the `Z` suffix and naive input explicitly.
- **Inject the clock and the runner.** Write `def f(..., now=None)` and
  `def g(..., runner=subprocess.run)` before the interviewer asks how you would test
  it; then show the fake in two lines.
- **Never `shell=True`.** If the interviewer hands you a command string, reach for
  `shlex.split` and say why.
- **Convert `defaultdict` to `dict` at the boundary** and mention the phantom-key
  problem; it shows you have been bitten by it.
- **Ask what "top 3" means when there are ties.** Then sort with a composite key.
- The trap: reading a whole file to hash it, or a whole list to take the last three.
  Stream with chunks and `deque(maxlen=n)`.

## Exercises

Run `course list 10`, then `course show 10.1`. Edit the file it names, run
`course run 10.1`, repeat until green. Then compare with `course solution 10.1`.

1. `days_since` · ISO 8601 with `Z`, aware datetimes, an injected `now`
2. `parse_args` · argparse types, choices, repeatable flags, mutually exclusive group
3. `checksum_file` · chunked SHA-256 and tolerant digest comparison
4. `run_command` · subprocess wrapper with an injected runner, `shlex`, error translation
5. `recent_events` · `deque(maxlen)` sliding window with `Counter`
6. `build_adjacency` · `defaultdict(set)` for an undirected graph, frozen to `dict`
7. `most_common_with_ties` · `Counter` plus a composite sort key for stable ties
