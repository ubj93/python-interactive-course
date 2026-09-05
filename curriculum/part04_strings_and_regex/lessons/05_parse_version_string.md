# Validating the whole string

--- teach #card-6402c808ae2559ac
### `fullmatch` means the whole string must fit
`re.search` finds the pattern anywhere. `re.match` only checks the *start*. `re.fullmatch` succeeds only if the entire string matches, which is what validation needs. All three return a `Match`, or `None` when they fail.
```python
>>> import re
>>> re.fullmatch(r"\d+", "14")
<re.Match object; span=(0, 2), match='14'>
>>> re.fullmatch(r"\d+", "14 extra") is None
True
```
Test with `if not m: raise ValueError(...)`. Strip the input first so the pattern does not need to allow spaces at both ends.

--- predict #card-0da38eaf298f5f7d
What does this print?
```python
import re
print(re.match(r"\d+", "14.5 extra") is None, re.fullmatch(r"\d+", "14.5 extra") is None)
```
answer: False True
> `match` is happy because the string *starts* with digits. `fullmatch` refuses because `.5 extra` is left over. Using `match` for validation is the classic interview bug.

--- teach #card-9562e4bd631557a2
### `?` makes a piece optional
`?` after something means "zero or one of it". `[vV]?` allows an optional leading `v`. To make a longer piece optional, wrap it in a non-capturing group: `(?:\.\d+)?` is "a dot and digits, or nothing".
```python
>>> re.fullmatch(r"[vV]?\d+(?:\.\d+)?", "v13") is not None
True
>>> re.fullmatch(r"[vV]?\d+(?:\.\d+)?", "13.6") is not None
True
```
Chain two optional groups for the minor and patch numbers.

--- quiz #card-d34e72d93954581a
With `fullmatch`, which pattern accepts `14`, `14.5` and `14.5.1` but rejects `14.5.1.2`?
- [ ] `r"\d+(?:\.\d+)*"`
- [x] `r"\d+(?:\.\d+){0,2}"`
- [ ] `r"\d+\.\d+\.\d+"`
> `{0,2}` allows at most two more groups. `*` allows any number, so four parts would pass. The third needs exactly three parts and rejects `14`.

--- code #card-bfa95e2066d95995
Print `True` if the whole of `s` is an optional `v`, a number, and up to two more dotted numbers; otherwise `False`.
```python
import re
s = "v14.5.1"
```
expect: True
solution: print(re.fullmatch(r"[vV]?\d+(?:\.\d+){0,2}", s) is not None)
> `fullmatch` returns a `Match` for the whole string, and `is not None` turns that into a bool. With `s = "14.5.1.2"` the same line prints `False`.

--- teach #card-f845daadb74559fb
### Named groups
`(?P<name>...)` is a capturing group with a name. Read it back with `m.group("name")`. A group inside an optional piece that did not take part returns `None`, not `''`.
```python
>>> pat = r"(?P<major>\d+)(?:\.(?P<minor>\d+))?"
>>> m = re.fullmatch(pat, "14.5")
>>> m.group("major"), m.group("minor")
('14', '5')
>>> re.fullmatch(pat, "14").group("minor") is None
True
```

--- predict #card-ca169322dd9556e0
What does this print?
```python
import re
m = re.fullmatch(r"(?P<a>\d+)(?:\.(?P<b>\d+))?", "14")
print(m.group("b"))
```
answer: None
> The optional group never matched, so group `b` is `None`. `int(None)` would raise, so the next card handles it.

--- teach #card-5b6103faad585316
### Turn `None` into a default, then into a number
`x or "0"` gives `"0"` when `x` is `None`, and `int(...)` makes the number. Do it for each of the three parts and collect them in a tuple: tuples of ints compare number by number, so `(14, 10) > (14, 9)` is `True` where the strings would say the opposite.
```python
major = int(m.group("major") or "0")
```
Two more pattern bits for the build: `\s+` is one or more spaces, and `\(` `\)` are literal parentheses, so `(?:\s+\((?P<build>[A-Za-z0-9]+)\))?` is an optional space-then-build. Its group is `None` when absent, which is the value you return.

--- fill #card-0fc7bb56bac85819
Complete the line so a missing patch number becomes 0.
```python
patch = int(m.group("patch") ___ "0")
```
answer: or
> `None or "0"` is `"0"`; `"1" or "0"` is `"1"`. `int` then converts either. Without the `or`, `int(None)` raises `TypeError`.

--- code #card-60eb19ba01c4510d
Set `version` to a tuple of three ints from the match `m`, using 0 for any part that is missing.
```python
import re
m = re.fullmatch(r"(?P<major>\d+)(?:\.(?P<minor>\d+))?(?:\.(?P<patch>\d+))?", "14.5")
```
check: version == (14, 5, 0)
solution: version = tuple(int(m.group(n) or "0") for n in ("major", "minor", "patch"))
> `patch` did not match, so its group is `None` and `or "0"` steps in. `tuple(...)` collects the three ints; a list would not compare equal to the tuple the exercise expects.

--- exercise 4.5 #card-2dffe6accb305792

--- recap #card-a8642cc0817f59cb
- `re.fullmatch` validates the whole string; `match` only checks the start.
- `?` and `(?:...)?` make a character or a piece optional.
- `(?P<name>...)` names a group; an unmatched group is `None`.
- `int(m.group("x") or "0")` turns a missing part into 0.
