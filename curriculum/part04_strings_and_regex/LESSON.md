# Part 4 · Strings and regular expressions

> **What you will be able to do:** take any line of text a fleet tool throws at you
> (a syslog line, a `key=value` blob, a version string, an API token that must not
> reach the ticket) and pull the parts out reliably, then put text back together in a
> shape humans and machines can read. Plan on two hours including the exercises.

## Why this part matters

Most of what a Client Platform Engineer processes is text: command output, log
files, plist and JSON exports, hostnames typed by a help-desk agent, CSVs from a
purchasing system. Interviewers know this, so the "parse this line" question is the
single most common warm-up you will get. The candidates who do well know the string
methods cold, reach for `re` when the shape of the text is genuinely irregular, and
can say *why* they chose one over the other.

## 1. Splitting and joining

```python
>>> line = "serial=C02XG1234ABC; os=macOS 14.5; managed=true"
>>> line.split(";")
['serial=C02XG1234ABC', ' os=macOS 14.5', ' managed=true']
>>> line.split("; ", 1)                 # maxsplit: at most one split
['serial=C02XG1234ABC', 'os=macOS 14.5; managed=true']
>>> "a  b\tc\n".split()                 # no argument: any run of whitespace, no empties
['a', 'b', 'c']
>>> "a  b".split(" ")                   # explicit separator keeps empties
['a', '', 'b']
>>> "line1\nline2\r\nline3".splitlines()
['line1', 'line2', 'line3']
```

`partition` splits exactly once and always returns three parts, which makes it the
safest way to split on the *first* occurrence of something:

```python
>>> "os=macOS 14.5".partition("=")
('os', '=', 'macOS 14.5')
>>> "password=a=b=c".partition("=")     # value keeps its own '=' signs
('password', '=', 'a=b=c')
>>> "no-equals-here".partition("=")     # never raises; empty sep and tail
('no-equals-here', '', '')
>>> "a.b.c".rpartition(".")             # from the right
('a.b', '.', 'c')
```

**Gotcha:** `"k=v".split("=", 1)` gives two items, but `"k".split("=", 1)` gives one.
Unpacking `key, value = s.split("=", 1)` raises `ValueError` on the second. Use
`partition` when the separator might be missing.

`join` is a method on the *separator* and takes an iterable of strings:

```python
>>> ", ".join(["mbp-1", "mbp-2"])
'mbp-1, mbp-2'
>>> ", ".join([1, 2])                   # TypeError: sequence item 0: expected str instance
>>> ", ".join(str(n) for n in [1, 2])
'1, 2'
```

Building a string with `+=` in a loop works, but interviewers expect the
"collect into a list, join once" idiom because it is linear rather than quadratic.

## 2. Trimming, replacing, finding

```python
>>> "  mbp-1 \n".strip()                # whitespace by default
'mbp-1'
>>> "xxmbp-1xx".strip("x")              # a *set* of characters, not a prefix
'mbp-1'
>>> "www.example.com".strip("w.")       # removes any of 'w' or '.' from both ends
'example.com'
>>> "com.apple.Safari".removeprefix("com.apple.")   # 3.9+: an actual prefix
'Safari'
>>> "a.b.c".replace(".", "/")
'a/b/c'
>>> "a.b.c".replace(".", "/", 1)        # count argument
'a/b.c'
>>> "mdmclient[512]".find("[")          # index or -1
9
>>> "mdmclient[512]".index("]")         # index or ValueError
13
```

**Gotcha:** `"filename.plist".strip(".plist")` does *not* remove the extension; it
strips any of the characters `. p l i s t` from both ends and gives `'filename'` here
only by luck (try it on `"list.plist"`). Use `removesuffix` or slicing.

### Case

```python
>>> "MacBook Pro".lower(), "MacBook Pro".upper()
('macbook pro', 'MACBOOK PRO')
>>> "straße".lower() == "STRASSE".lower()     # False
>>> "straße".casefold() == "STRASSE".casefold()   # True
>>> "mdm check-in v2".title()
'Mdm Check-In V2'
>>> "mdm check-in v2".capitalize()
'Mdm check-in v2'
```

`casefold` is the right tool for case-insensitive *comparison*; `lower` is fine for
ASCII data like hostnames. `title` capitalises after *every* non-letter, including
digits (`"v2a".title()` is `'V2A'`), which is why exercise 4.2 avoids it. Remember
too that `isalnum()` and `isdigit()` accept non-ASCII characters such as `"ä"` and
`"²"`; compare against an explicit character set when the data must be ASCII.

## 3. Slicing, again

You met slicing in Part 1. Two idioms come up constantly when parsing:

```python
>>> s = "C02XG1234ABC"
>>> s[-4:]                # last four characters, safe on short strings
'4ABC'
>>> "ab"[-4:]             # slices never raise
'ab'
>>> "*" * (len(s) - 4) + s[-4:]     # mask all but the last four
'********4ABC'
>>> s[:3], s[3:]          # prefix, rest
('C02', 'XG1234ABC')
>>> [s[i:i + 4] for i in range(0, len(s), 4)]   # fixed-size chunks
['C02X', 'G123', '4ABC']
```

## 4. The format spec mini-language

Everything after the colon in `{value:spec}` follows one grammar:

```
[[fill]align][sign][#][0][width][,][.precision][type]
```

| Spec | Input | Output | Meaning |
|---|---|---|---|
| `{:<10}` | `"mbp"` | `'mbp       '` | left-align in 10 |
| `{:>10}` | `"mbp"` | `'       mbp'` | right-align |
| `{:^10}` | `"mbp"` | `'   mbp    '` | centre |
| `{:-<10}` | `"mbp"` | `'mbp-------'` | fill character |
| `{:08.3f}` | `3.14159` | `'0003.142'` | zero pad, width 8, 3 decimals |
| `{:,}` | `1234567` | `'1,234,567'` | thousands separator |
| `{:.1%}` | `0.835` | `'83.5%'` | percent |
| `{:x}` / `{:#010b}` | `255` | `'ff'` / `'0b11111111'` | hex, binary with prefix |
| `{:+d}` | `5` | `'+5'` | always show sign |
| `{!r}` | `"a"` | `"'a'"` | repr instead of str |

Widths can themselves be expressions, which is how you build tables from data:

```python
>>> rows = [("mbp-j-doe", "macOS", 83.5), ("win-lab-01", "Windows", 7.0)]
>>> w = max(len(r[0]) for r in rows)
>>> for host, os_name, pct in rows:
...     print(f"{host:<{w}}  {os_name:<8}  {pct:>6.1f}")
mbp-j-doe   macOS       83.5
win-lab-01  Windows      7.0
```

Strings default to left alignment and numbers to right alignment. Say that out loud
in an interview when you write a table; it shows you know why the columns line up.

## 5. `str` versus `bytes`

Text in Python 3 is `str`, a sequence of Unicode code points. What comes off the
network, out of a subprocess, or from a file opened in `"rb"` mode is `bytes`.
Converting between them is explicit and always needs an encoding.

```python
>>> "café".encode("utf-8")
b'caf\xc3\xa9'
>>> b'caf\xc3\xa9'.decode("utf-8")
'café'
>>> len("café"), len("café".encode("utf-8"))
(4, 5)
>>> b"MBP-1".decode()                     # utf-8 is the default
'MBP-1'
>>> b"\xff".decode("utf-8")               # UnicodeDecodeError
>>> b"\xff".decode("utf-8", errors="replace")
'\ufffd'
>>> "abc" == b"abc"                       # False, and no error: a classic bug
False
```

`bytes` has most of the same methods (`split`, `strip`, `startswith`) but they take
bytes arguments: `b"a,b".split(b",")`. Decode at the boundary of your program and
work with `str` everywhere inside; encode again only when writing out. Prefer
`subprocess.run(..., text=True)` and `open(path, encoding="utf-8")` so you rarely
see raw bytes at all.

## 6. `textwrap`: wrapping, dedenting, indenting

```python
>>> import textwrap
>>> textwrap.fill("Device MBP-J-DOE has not checked in for 31 days.", width=30)
'Device MBP-J-DOE has not\nchecked in for 31 days.'
>>> textwrap.indent("line1\nline2", "  > ")
'  > line1\n  > line2'
>>> textwrap.dedent("""\
...     first
...       second
... """)
'first\n  second\n'
```

`dedent` removes the *common* leading whitespace from every line, which is how you
keep a multi-line string readable inside an indented function.

## 7. Regular expressions

A regular expression describes a *set of strings*. The `re` module lets you ask
whether a string is in the set, where, and which parts matched. Always write patterns
as raw strings (`r"..."`) so backslashes reach the regex engine untouched.

### 7.1 The functions

| Call | Returns | Use when |
|---|---|---|
| `re.search(p, s)` | first `Match` anywhere, or `None` | "does it contain ...?" |
| `re.match(p, s)` | `Match` only if it matches at the *start* | prefix check |
| `re.fullmatch(p, s)` | `Match` only if the *whole* string matches | validation |
| `re.findall(p, s)` | list of strings (or tuples if groups) | pull all occurrences |
| `re.finditer(p, s)` | iterator of `Match` objects | you need positions or groups |
| `re.sub(p, repl, s)` | new string | replace; `repl` can be a function |
| `re.split(p, s)` | list | split on a pattern, e.g. `r"[,;]\s*"` |

```python
>>> import re
>>> re.search(r"\d+", "mdmclient[512]: ok").group()
'512'
>>> re.match(r"\d+", "mdmclient[512]") is None
True
>>> re.fullmatch(r"[A-Z0-9]{12}", "C02XG1234ABC") is not None
True
>>> re.findall(r"\d+", "10.0.0.5 port 443")
['10', '0', '0', '5', '443']
```

**Gotcha:** `match` is not "matches"; it is anchored at the start only. For
validation you want `fullmatch` (or `^...$` in the pattern). Forgetting this is the
most common regex bug interviewers see.

### 7.2 Syntax you need

| Pattern | Matches |
|---|---|
| `.` | any character except newline |
| `\d` `\w` `\s` | digit, word char `[A-Za-z0-9_]`, whitespace |
| `\D` `\W` `\S` | the opposites |
| `[abc]` `[^abc]` `[a-f0-9]` | character class, negated class, range |
| `*` `+` `?` `{3}` `{1,3}` | 0+, 1+, 0 or 1, exactly 3, 1 to 3 |
| `*?` `+?` | the same, but *lazy* (shortest match) |
| `^` `$` `\b` | start, end, word boundary |
| `a|b` | alternation |
| `(...)` `(?:...)` | capturing group, non-capturing group |
| `(?P<name>...)` | named group |
| `(?=...)` `(?!...)` `(?<=...)` `(?<!...)` | lookahead, negative lookahead, lookbehind, negative lookbehind |
| `\.` `\[` `\\` | literal dot, bracket, backslash |

The dot is the classic trap: `r"10.0.0.1"` matches `"10x0y0z1"`. Escape it.

### 7.3 Groups and named groups

```python
>>> m = re.search(r"(\w+)\[(\d+)\]", "Jun 12 14:03:22 host mdmclient[512]: ok")
>>> m.group(0), m.group(1), m.group(2)
('mdmclient[512]', 'mdmclient', '512')
>>> m.groups()
('mdmclient', '512')
>>> m.start(), m.end(), m.span(2)
(20, 34, (30, 33))
```

Named groups turn a match into something that reads like a record:

```python
>>> pat = re.compile(r"(?P<major>\d+)\.(?P<minor>\d+)(?:\.(?P<patch>\d+))?")
>>> m = pat.fullmatch("14.5")
>>> m.group("major"), m["minor"], m["patch"]
('14', '5', None)
>>> m.groupdict()
{'major': '14', 'minor': '5', 'patch': None}
```

A group that did not participate returns `None`, not `''`. Convert with
`int(m["patch"] or 0)` when a missing part should default to zero.

### 7.4 Compile once, use many times

```python
IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
KV = re.compile(r"(?P<key>\w+)\s*=\s*(?P<value>[^;]*)")

for line in lines:
    for m in KV.finditer(line):
        ...
```

Module-level compiled patterns with `UPPER_CASE` names are the convention. The
functions on `re` cache compiled patterns too, so this is about readability and
documenting intent more than speed. Flags go on the compile call:
`re.compile(r"error", re.IGNORECASE)`; `re.MULTILINE` makes `^`/`$` match at line
breaks; `re.VERBOSE` lets you spread a pattern over lines with comments.

### 7.5 Greedy versus lazy

```python
>>> re.search(r"\[.*\]", "[a] and [b]").group()
'[a] and [b]'
>>> re.search(r"\[.*?\]", "[a] and [b]").group()
'[a]'
>>> re.search(r"\[[^\]]*\]", "[a] and [b]").group()     # the clearest of the three
'[a]'
```

A negated character class (`[^\]]*`) says exactly what you mean ("anything but a
closing bracket") and cannot run away across the line the way `.*` does.

### 7.6 Patterns you will use in CPE work

```python
IPV4     = r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])"   # then check each octet <= 255
SEMVER   = r"^v?(\d+)\.(\d+)\.(\d+)$"
SYSLOG_TS = r"[A-Z][a-z]{2} [ \d]\d \d\d:\d\d:\d\d"          # 'Jun  2 09:00:01'
ISO_TS   = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})"
```

A regex can check *shape* but rarely *range*: `\d{1,3}` happily matches `999`. The
idiomatic answer is a regex for shape followed by a small Python check
(`all(0 <= int(o) <= 255 for o in octets)`). Say that in the interview rather than
pasting the 60-character "exact IPv4" pattern from the internet.

### 7.7 `re.sub` with a callable

The replacement can be a function that receives the `Match` and returns the text to
insert. This is how you mask, rewrite, or count while replacing:

```python
>>> def mask(m):
...     value = m.group(2)
...     return m.group(1) + "*" * (len(value) - 4) + value[-4:]
>>> re.sub(r"(password=)(\S+)", mask, "user=jdoe password=hunter2secret")
'user=jdoe password=*********cret'
```

In a string replacement, `\1` or `\g<name>` refers to groups:
`re.sub(r"(\d+)\.(\d+)", r"\2.\1", "14.5")` gives `'5.14'`.

### 7.8 When *not* to use regex

- **Structured formats have parsers.** JSON, CSV, plists, and URLs should be read
  with `json`, `csv`, `plistlib`, and `urllib.parse`. A regex over JSON breaks on the
  first escaped quote.
- **Simple tests have simple tools.** `s.startswith("ERROR")`, `"[" in s`,
  `s.isdigit()` are faster to write, faster to run, and need no explanation.
- **Fixed separators want `split`/`partition`.** `"a=b"` does not need `re`.
- **Unbounded `.*` next to alternation can backtrack catastrophically.** Prefer
  negated classes and anchors.
- **A pattern nobody can read is a maintenance bug.** Use named groups and
  `re.VERBOSE` or break it into two steps.

The test an interviewer applies: can you say in one sentence what the pattern
matches? If not, simplify.

## 8. Gotchas in one place

- `str.strip(chars)` strips a character set, not a substring.
- `re.match` anchors at the start only; use `fullmatch` to validate.
- An unmatched optional group is `None`; `int(None)` raises.
- `split(",")` on an empty string gives `['']`, not `[]`.
- `"abc" == b"abc"` is `False` with no warning.
- `str.title()` capitalises after digits and apostrophes.
- The dot matches anything; escape it in IPs and versions.
- `findall` returns tuples when the pattern has two or more groups.

## Interview notes for this part

- **Name the tool before you use it.** "This is a fixed `;`-separated format, so I
  will `split` and `partition`; the timestamp is irregular, so that part gets a
  regex." Choosing the lighter tool earns points.
- **Ask what the data really looks like.** "Can the value contain the separator?
  Is the pid always present? Are days zero-padded?" Every one of those is an edge case
  in this part's exercises, and asking is better than guessing.
- **Validate shape with regex, range with Python.** Say it, then do it.
- **The trap:** writing `re.match` for validation and never noticing that
  `"C02XG1234ABC-old"` passes. Reach for `fullmatch`.
- **Write a compiled pattern at module level with a name.** It shows you have done
  this outside of interviews.

## Exercises

Run `course list 4`, then `course show 4.1`.

1. `parse_kv_line` · `split`, `partition`, `strip`; tolerant parsing of `key=value` lines
2. `snake_to_camel` · case conversion both ways without `str.title`
3. `extract_ips` · `re.findall` with lookarounds, then validate octets in Python
4. `mask_secrets` · `re.sub` with a callable that keeps the last four characters
5. `parse_version_string` · `fullmatch`, optional groups, `None` to `0`
6. `parse_syslog_line` · named groups and `groupdict` on a real log format
7. `render_table` · the format spec mini-language with widths computed from data
