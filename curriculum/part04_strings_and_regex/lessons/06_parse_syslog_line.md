# Named groups on a real log line

--- teach
### Compile once, at module level
`re.compile(pattern)` turns a pattern into an object with the same methods: `SYSLOG.fullmatch(line)`, `SYSLOG.search(text)`. Define it once at the top of the file with an `UPPER_CASE` name; it documents intent, and the pattern is built one time instead of on every call.
```python
import re

SYSLOG = re.compile(r"(?P<host>\S+) (?P<message>.*)")

m = SYSLOG.fullmatch("mbp-1 hello")
```
Long patterns can be spread over lines with `re.VERBOSE` (more in the lesson); this exercise fits on a couple of lines either way.

--- teach
### Classes for the pieces of a syslog line
`\S` is one non-whitespace character, so `\S+` is a hostname. `\w` is a letter, digit or underscore; inside `[...]` a dot is literal and a `-` at the end is literal, so `[\w.-]+` is a process name like `com.apple.xpc.launchd`. `[A-Z][a-z]{2}` is a month, and `[ \d]\d` is a day that may be space-padded.
```python
>>> re.findall(r"[A-Z][a-z]{2} [ \d]\d", "Jun 12 and Jun  2")
['Jun 12', 'Jun  2']
```

--- predict
What does this print?
```python
import re
print(re.findall(r"[\w.-]+", "com.apple.xpc.launchd[1]: ok"))
```
answer: ['com.apple.xpc.launchd', '1', 'ok']
> `[` and `:` are not in the class, so the run stops before them. That is why this class is the right one for the process name: it ends exactly where the pid or the colon begins.

--- teach
### An optional bracketed pid, then "the rest"
Brackets are special in a pattern, so a literal one is `\[` or `\]`. Wrap the pid in an optional non-capturing group so `kernel:` and `mdmclient[512]:` both fit. `.*` matches anything, including nothing, so the message may be empty; `: ?` allows the colon with or without a following space.
```python
r"(?P<process>[\w.-]+)(?:\[(?P<pid>\d+)\])?: ?(?P<message>.*)"
```
With `fullmatch`, the `.*` runs to the end of the line, so a message containing its own `: ` stays whole.

--- code
Print the pid, the number inside the square brackets of `line`.
```python
import re
line = "mbp-j-doe mdmclient[512]: Received push"
```
expect: 512
solution: print(re.search(r"\[(\d+)\]", line).group(1))
> `\[` and `\]` are literal brackets; the group between them captures the digits. `search` finds it anywhere in the line, and `group(1)` returns just the number as text.

--- quiz
Why does `(?P<process>[\w.-]+)` stop before `[512]` instead of running on?
- [x] `[` is not in the class, so the run of matching characters ends there
- [ ] `+` matches as few characters as possible
- [ ] The pattern has an anchor after the process group
> A class with `+` takes every consecutive character in the set and stops at the first one outside it. `+` is greedy, not lazy; and there is no anchor.

--- teach
### `groupdict` and fixing the one non-string field
`m.groupdict()` returns a dict of every named group, which is almost the answer. The pid is text, or `None` when its group did not match, so convert it with a conditional expression: `a if condition else b`.
```python
m = SYSLOG.fullmatch(line)
if not m:
    return None
parsed = m.groupdict()
parsed["pid"] = int(m.group("pid")) if m.group("pid") else None
return parsed
```

--- code
Set `parsed` to the dict of named groups from `m`, with the pid converted to an int.
```python
import re
m = re.fullmatch(r"(?P<host>\S+) (?P<process>[\w.-]+)\[(?P<pid>\d+)\]: (?P<message>.*)", "mbp-1 mdmclient[512]: ok")
```
check: parsed["host"] == "mbp-1"
check: parsed["pid"] == 512
solution: parsed = m.groupdict()
solution: parsed["pid"] = int(parsed["pid"])
> `groupdict()` gives every named group as a string. Only the pid needs `int()`; in the exercise the group may also be `None`, so guard it with `if m.group("pid") else None`.

--- teach
### Many lines: reuse the one-line parser
Lines read from a file end in `\n`, and a `fullmatch` would fail on the newline. Strip it with `rstrip("\n")` before matching. Then `parse_syslog` is a loop that calls `parse_syslog_line` and keeps the results that are not `None`.
```python
results = []
for line in lines:
    parsed = parse_syslog_line(line)
    if parsed is not None:
        results.append(parsed)
return results
```
Blank and junk lines return `None` from the single-line parser, so they are skipped without any extra checks.

--- fill
Complete the call so a trailing newline does not break the match.
```python
m = SYSLOG.fullmatch(line.___("\n"))
```
answer: rstrip
> `rstrip("\n")` removes newlines from the right end only. `strip()` would also remove a trailing space, and the empty-message test expects `": "` to still match.

--- exercise 4.6

--- recap
- `re.compile` at module level, `UPPER_CASE` name, then `PATTERN.fullmatch(line)`.
- `\S+` hostname, `[\w.-]+` process, `[ \d]\d` space-padded day.
- `(?:\[(?P<pid>\d+)\])?` is an optional pid; `.*` takes the rest.
- `groupdict()` gives the record; convert the pid with `int(...) if ... else None`.
