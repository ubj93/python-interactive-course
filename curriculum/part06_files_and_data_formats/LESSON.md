# Part 6 · Files and data formats

> **What you will be able to do:** open a file safely, choose the right way to read it
> (all at once, line by line, or in chunks), write results back, walk a directory tree
> with `pathlib`, and move data in and out of JSON, CSV and plist files without
> losing types or corrupting encodings. Budget about two hours including exercises.

## Why this matters

Almost every CPE script starts by reading something from disk: an inventory export,
a log the MDM agent wrote, a configuration profile, a list of hostnames someone pasted
into a text file. And almost every script ends by writing a report. Interviewers use
file tasks because they expose the habits that matter in production: do you close
files, do you handle encodings, do you load a 4 GB log into memory, do you know that
CSV cells are always strings?

## 1. Opening files: `with`, mode, encoding

```python
>>> with open("hosts.txt", "r", encoding="utf-8") as f:
...     text = f.read()
...
>>> f.closed
True
```

Three habits, every time:

- **`with`** closes the file when the block ends, even if an exception is raised.
  Never write `f = open(...)` on its own line in an interview.
- **Mode**: `"r"` read text (default), `"w"` write (truncates!), `"a"` append,
  `"x"` create-or-fail, add `"b"` for bytes: `"rb"`, `"wb"`.
- **`encoding="utf-8"`** always. Without it Python uses the platform default, which is
  UTF-8 on macOS and Linux but was cp1252 on Windows for years. A script that works
  on your Mac and crashes on a Windows endpoint usually forgot this argument.

```python
>>> open("profile.mobileconfig", "rb").read()[:5]     # bytes, no encoding argument
b'<?xml'
```

Text mode gives you `str` and translates `\r\n` to `\n` on read. Binary mode gives you
`bytes` untouched. Plists and hashes want bytes; logs and CSV want text.

## 2. Three ways to read

| Strategy | Code | Use when |
|---|---|---|
| Whole file | `f.read()` | small files, config, JSON |
| Line by line | `for line in f:` | logs, anything that might be big |
| Fixed chunks | `while chunk := f.read(65536):` | hashing, copying, binary data |

```python
>>> with open("agent.log", encoding="utf-8") as f:
...     for line in f:
...         if "[ERROR]" in line:
...             print(line.rstrip("\n"))
```

Iterating a file object yields one line at a time **including the trailing newline**.
Strip it (`line.rstrip("\n")` or `line.strip()`) before comparing. Memory stays flat no
matter how big the file is, which is the answer to "what if the log is 10 GB?".

The non-idiomatic version people write in interviews is `for line in f.readlines():`.
It works, but `readlines()` builds a list of every line first. Say why you are not
doing that.

### The "last n lines" problem

`collections.deque(maxlen=n)` keeps only the newest `n` items: push everything through
it and what is left is the tail. One pass, `n` lines of memory.

```python
>>> from collections import deque
>>> with open("agent.log", encoding="utf-8") as f:
...     last = deque(f, maxlen=3)
...
>>> [line.rstrip("\n") for line in last]
['... third-from-last', '... second-from-last', '... last']
```

### Skipping blanks and comments

Config-style text files mix data with comments. The pattern is strip, then test:

```python
>>> hosts = []
>>> with open("hosts.txt", encoding="utf-8") as f:
...     for raw in f:
...         line = raw.strip()
...         if not line or line.startswith("#"):
...             continue
...         hosts.append(line)
```

## 3. Writing

```python
>>> with open("report.txt", "w", encoding="utf-8") as f:
...     f.write("hostname,status\n")          # write() does not add a newline
...     f.writelines(f"{h},ok\n" for h in hosts)
...     print("done", file=f)                 # print() does add one
```

`"w"` truncates the file the moment you open it. If the script crashes halfway you
have a half-written report. For anything important write to a temporary name and
`os.replace(tmp, final)` at the end; the rename is atomic on POSIX filesystems.

## 4. `pathlib`: paths as objects

Stop building paths with string concatenation. `pathlib.Path` knows about separators,
suffixes and parents, and it reads and writes small files in one call.

```python
>>> from pathlib import Path
>>> p = Path("/var/log/jamf.log")
>>> p.name, p.stem, p.suffix, p.parent
('jamf.log', 'jamf', '.log', PosixPath('/var/log'))
>>> Path("/var/log") / "install.log"       # `/` joins paths
PosixPath('/var/log/install.log')
>>> p.exists(), p.is_file(), p.is_dir()
(True, True, False)
>>> p.stat().st_size                       # bytes
48213
>>> Path("hosts.txt").read_text(encoding="utf-8").splitlines()
['mbp-j-doe', 'win-lab-01']
>>> Path("out.txt").write_text("hello\n", encoding="utf-8")
6
```

Walking a tree:

```python
>>> root = Path("/Library/Managed Installs")
>>> [p for p in root.rglob("*.plist") if p.is_file()]
>>> sorted(root.rglob("*"), key=lambda p: p.stat().st_size, reverse=True)[:5]
```

`glob` looks in one directory, `rglob` recurses. Both yield directories too, so filter
with `is_file()` when you want files. `p.relative_to(root)` gives the path inside the
tree, and `.as_posix()` turns it into forward-slash text on every platform.

| Need | Idiom |
|---|---|
| join | `base / "sub" / name` |
| extension, case-insensitive | `p.suffix.lower() == ".log"` |
| change extension | `p.with_suffix(".json")` |
| make parents | `p.parent.mkdir(parents=True, exist_ok=True)` |
| home, cwd | `Path.home()`, `Path.cwd()` |
| absolute | `p.resolve()` |

Functions that take a path should accept both `str` and `Path`: `Path(path)` is a
no-op on a `Path` and converts a string, so start every such function with it.

## 5. JSON

```python
>>> import json
>>> data = {"serial": "C02XG1234ABC", "tags": ["lab", "loaner"], "ram_gb": 16}
>>> s = json.dumps(data)                             # to a string
>>> json.loads(s) == data                            # from a string
True
>>> with open("device.json", "w", encoding="utf-8") as f:
...     json.dump(data, f, indent=2, sort_keys=True)  # to a file
>>> with open("device.json", encoding="utf-8") as f:
...     back = json.load(f)                           # from a file
```

`s` versus no `s`: `loads`/`dumps` work on **s**trings, `load`/`dump` on files.

Options you will actually use:

| Keyword | Effect |
|---|---|
| `indent=2` | pretty print, one key per line |
| `sort_keys=True` | deterministic output, diff-friendly |
| `ensure_ascii=False` | keep "Zürich" as is instead of `"Zürich"` |
| `default=fn` | called for values JSON cannot encode (dates, sets, Paths) |

```python
>>> from datetime import datetime
>>> json.dumps({"seen": datetime(2024, 5, 1)})
TypeError: Object of type datetime is not JSON serializable
>>> def to_json(o):
...     if isinstance(o, datetime):
...         return o.isoformat()
...     if isinstance(o, set):
...         return sorted(o)
...     raise TypeError(f"cannot serialize {type(o).__name__}")
...
>>> json.dumps({"seen": datetime(2024, 5, 1), "tags": {"b", "a"}}, default=to_json)
'{"seen": "2024-05-01T00:00:00", "tags": ["a", "b"]}'
```

**Gotchas**

- JSON keys are always strings: `json.loads(json.dumps({1: "a"}))` gives `{"1": "a"}`.
- Tuples come back as lists. Sets and dates do not go at all without `default=`.
- `json.load` on an empty file raises `JSONDecodeError`, a subclass of `ValueError`.
- `indent` adds a trailing newline? No. Write one yourself if tools like `diff` matter.

## 6. CSV

Never split CSV on commas by hand; quoted fields contain commas. Use the `csv` module,
and open the file with `newline=""` in both directions, otherwise embedded newlines in
quoted cells get mangled on Windows.

```python
>>> import csv
>>> with open("inventory.csv", newline="", encoding="utf-8") as f:
...     for row in csv.DictReader(f):
...         print(row)
{'serial': 'C02XG1234ABC', 'hostname': 'mbp-j-doe', 'ram_gb': '16'}
```

**Every cell is a string.** `'16'`, not `16`. Convert on the way in, and expect the
conversion to fail on some rows: real exports contain `"n/a"`, blanks and stray
whitespace. Decide up front whether a bad row is skipped or fatal, and say so.

```python
>>> with open("report.csv", "w", newline="", encoding="utf-8") as f:
...     w = csv.DictWriter(f, fieldnames=["serial", "status"])
...     w.writeheader()
...     w.writerow({"serial": "C02XG1234ABC", "status": "stale"})
```

`csv.reader` gives lists; `DictReader` uses the first row as keys. A short row gives
`None` for the missing keys; a long row stores the extras under the key `None`. Both
are your "malformed row" signal.

## 7. Plists

macOS stores preferences, launchd jobs and configuration profiles as property lists.
`plistlib` turns them into plain Python: `dict`, `list`, `str`, `int`, `bool`,
`bytes` (for `<data>`), `datetime`.

```python
>>> import plistlib
>>> with open("wifi.mobileconfig", "rb") as f:      # bytes!
...     profile = plistlib.load(f)
>>> profile["PayloadType"]
'Configuration'
>>> [p["PayloadType"] for p in profile["PayloadContent"]]
['com.apple.wifi.managed', 'com.apple.security.pem']
```

A configuration profile is a dict with `PayloadType` `"Configuration"`,
`PayloadIdentifier`, `PayloadDisplayName`, `PayloadUUID`, and a `PayloadContent` list
of payload dicts, each with its own `PayloadType`, `PayloadIdentifier` and usually a
`PayloadDisplayName`. Treat every key beyond `PayloadType` as optional: vendors omit
them.

`plistlib.loads(data)` reads bytes; `plistlib.dumps(obj)` writes XML by default and
`fmt=plistlib.FMT_BINARY` writes the binary form. Both formats load with the same
call. Bad input raises `plistlib.InvalidFileException` (a `ValueError`) or, for
broken XML, `xml.parsers.expat.ExpatError`; catch both if you want one error type.

## 8. Choosing a format

| Format | Read | Write | Types preserved | Human-editable |
|---|---|---|---|---|
| plain text | `for line in f` | `f.write` | none | yes |
| JSON | `json.load` | `json.dump` | str, numbers, bool, None, list, dict | yes |
| CSV | `csv.DictReader` | `csv.DictWriter` | none, all strings | in a spreadsheet |
| plist | `plistlib.load` | `plistlib.dump` | plus bytes and datetime | with care |

## Interview notes for this part

- **Say the memory model out loud.** "I iterate the file so memory is constant even
  if the log is huge" is the sentence interviewers are waiting for. If you do use
  `read()`, say why it is safe here.
- **Name the encoding.** Adding `encoding="utf-8"` unprompted signals that you have
  been bitten by Windows. `newline=""` for CSV signals the same.
- **Ask what a malformed row should do.** Skip it, count it, log it, or abort? There
  is no right answer, but there is a wrong one: silently crashing on row 40,000.
- **Types at the boundary.** CSV gives strings, JSON gives lists not tuples, plist
  gives `datetime` objects. Convert once, right after loading, and keep the rest of
  the program typed.
- **The trap:** building paths with `+` and `"/"`, forgetting `with`, and testing
  file code against a real path on your laptop instead of a `tempfile` directory.

## Exercises

Run `course list 6`, then `course show 6.1`, and so on.

1. `read_hostnames` · read, strip, skip blanks and comments
2. `count_log_levels` · stream a log line by line and count
3. `load_inventory_csv` · `csv.DictReader`, type conversion, malformed rows
4. `write_report_json` · `json.dump` with `indent`, `sort_keys`, `default=` and round-trip
5. `tail_lines` · last n lines with a `deque`, constant memory
6. `parse_profile_plist` · `plistlib` and the configuration profile shape
7. `find_large_files` · `pathlib.rglob`, `stat`, suffix filters, sorting by size
