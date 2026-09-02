# Streaming a log

--- teach
### Iterate the file; never `read()` a log
A log can be gigabytes. `f.read()` and `f.readlines()` load all of it into memory. `for line in f:` reads one line, handles it, and forgets it, so memory stays flat no matter how big the file is.
```python
with open("agent.log", encoding="utf-8") as f:
    for line in f:
        ...                 # one line in memory at a time
```
Saying "I iterate the file so memory is constant" out loud is what the interviewer is waiting for.

--- quiz
Which loop keeps memory flat on a 10 GB log?
- [ ] `for line in f.readlines():`
- [ ] `for line in f.read().splitlines():`
- [x] `for line in f:`
> `readlines()` and `read()` both build the whole file in memory first. Iterating the file object reads a line at a time.

--- teach
### Start the counts with every key, in order
The result must have exactly the keys `ERROR`, `WARN`, `INFO`, in that order, even for an empty file. So build the dict before the loop, with every count at 0, and only add to existing keys inside the loop. Dicts keep the order keys were inserted.
```python
LEVELS = ("ERROR", "WARN", "INFO")
counts = {level: 0 for level in LEVELS}
```

--- code
Build `counts` with every level in `LEVELS` at 0, then add 2 to `ERROR`.
```python
LEVELS = ("ERROR", "WARN", "INFO")
```
check: counts == {"ERROR": 2, "WARN": 0, "INFO": 0}
check: list(counts) == ["ERROR", "WARN", "INFO"]
solution: counts = {level: 0 for level in LEVELS}
solution: counts["ERROR"] += 2
> The dict comprehension seeds all three keys in `LEVELS` order. Because the keys already exist, `+= 2` works without a check.

--- predict
What does this print?
```python
counts = {level: 0 for level in ("ERROR", "WARN", "INFO")}
counts["WARN"] += 1
print(counts)
```
answer: {'ERROR': 0, 'WARN': 1, 'INFO': 0}
> The dict comprehension seeds all three keys at 0 in the given order; `+= 1` bumps one of them.

--- teach
### Find the first bracketed token with `partition`
`s.partition("[")` splits at the first `[` only and returns three parts: before, the separator, after. If the separator is not there, the middle part is `""`. Partition again on `]` to cut the token out.
```python
_, opened, rest = line.partition("[")
if not opened:
    continue                     # no '[' on this line
token, closed, _ = rest.partition("]")
```
Because `partition` stops at the first match, a later `[ERROR 403]` in the message is never seen.

--- predict
What does this print?
```python
line = "t [INFO] saw [WARN] in payload"
_, _, rest = line.partition("[")
token, _, _ = rest.partition("]")
print(token)
```
answer: INFO
> The first `[` is before `INFO`, and the first `]` after it closes that same token. The later `[WARN]` is in the part that gets thrown away.

--- teach
### Aliases and unknown levels
`WARNING` should count as `WARN`; `DEBUG`, `error` and `Info` should be ignored. A small dict maps aliases; `dict.get(key, key)` returns the key itself when there is no alias. Then `if level in counts` keeps only the three you want.
```python
ALIASES = {"WARNING": "WARN"}

level = ALIASES.get(token, token)
if level in counts:
    counts[level] += 1
```

--- code
Count the levels in `lines` into `counts`: take the first bracketed token, map aliases, ignore unknown levels and lines without a bracket.
```python
LEVELS, ALIASES = ("ERROR", "WARN", "INFO"), {"WARNING": "WARN"}
lines = ["t [INFO] a", "t [WARNING] b", "t [DEBUG] c", "no level", "t [ERROR] d [ERROR 403]"]
counts = {level: 0 for level in LEVELS}
```
check: counts == {"ERROR": 1, "WARN": 1, "INFO": 1}
solution: for line in lines:
solution:     _, opened, rest = line.partition("[")
solution:     if not opened:
solution:         continue
solution:     token, _, _ = rest.partition("]")
solution:     level = ALIASES.get(token, token)
solution:     if level in counts:
solution:         counts[level] += 1
> `partition("[")` skips lines with no bracket, the second `partition` cuts out the first token only, `ALIASES.get` turns `WARNING` into `WARN`, and `if level in counts` drops `DEBUG`.

--- fill
Complete the line so `WARNING` becomes `WARN` and every other token is unchanged.
```python
level = ALIASES.get(token, ___)
```
answer: token
> The second argument of `get` is the default. Using `token` as its own default means "look up an alias, otherwise keep what you have".

--- exercise 6.2

--- recap
- `for line in f:` streams a file; `read()` and `readlines()` load it all.
- Seed the result dict with every key at 0 so order and keys are fixed.
- `partition("[")` finds the first bracket; a second `partition("]")` cuts the token.
- `ALIASES.get(token, token)` maps aliases; `if level in counts` filters the rest.
