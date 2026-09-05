# Enums

--- teach #card-093cfb1a6b8858b7
### An Enum is a fixed set of named constants
`Platform.MAC` is a member: it has a `.name` (`"MAC"`) and a `.value` (`"mac"`). Members are singletons, so compare them with `is` or `==` to each other. Calling the class with a value looks the member up; an unknown value raises `ValueError`.
```python
from enum import Enum

class Platform(Enum):
    MAC = "mac"
    WINDOWS = "windows"

>>> Platform("mac") is Platform.MAC
True
>>> Platform("darwin")
ValueError: 'darwin' is not a valid Platform
```
Note that `Platform.MAC == "mac"` is `False`: a member is not its value.

--- code #card-2a30f254ede65182
Declare an Enum `Platform` with members `MAC = "mac"` and `WINDOWS = "windows"`, then print the `.name` of the member whose value is `"windows"`.
```python
from enum import Enum
```
expect: WINDOWS
check: Platform("mac") is Platform.MAC
solution: class Platform(Enum):
solution:     MAC = "mac"
solution:     WINDOWS = "windows"
solution: print(Platform("windows").name)
> `Platform("windows")` looks the member up by value; `.name` is the identifier you declared it with. The lookup returns the one and only `Platform.WINDOWS` object.

--- teach #card-79acdff94dcc5d43
### Turn the lookup into "member or None"
Rule 3 of the exercise is "return the member if the text is a value". `cls(text)` does that but raises on a miss. Wrap it in `try`/`except ValueError` (Part 7) to get a quiet `None` instead, then fall through to the alias table with `dict.get`.
```python
def _lookup(cls, text):
    try:
        return cls(text)
    except ValueError:
        return ALIASES.get(text)
```
Inside a classmethod, `cls` is the enum class, so `cls(text)` is `Platform(text)`.

--- teach #card-fe264466e6e65b7e
### Keep the alias table outside the class
Every non-dunder name in an Enum body becomes a member. A dict named `ALIASES` inside the class would turn into `Platform.ALIASES`, a fifth "platform". Define the table at module level, after the class, so it can refer to the members.
```python
class Platform(Enum):
    MAC = "mac"
    ...

ALIASES = {
    "macos": Platform.MAC, "darwin": Platform.MAC,
    "win": Platform.WINDOWS, "ubuntu": Platform.LINUX,
}
```

--- quiz #card-716a693db81255dd
Where should the `ALIASES` dict live?
- [ ] Inside the class body, above the members
- [ ] Inside the class body, below the members
- [x] At module level, after the class
> Anything in the body becomes a member, wherever it sits. After the class is the only place that is both outside the body and able to name `Platform.MAC`.

--- teach #card-e718ee29beae59fd
### Normalise before you look up
Real input is `"Mac OS X 10.15.7"`. The rule: strip, lowercase, cut from the first digit, strip again, collapse runs of spaces. `re.split(r"\d", s, maxsplit=1)[0]` gives everything before the first digit (Part 4). `" ".join(s.split())` collapses whitespace, because `split()` with no argument drops every run of spaces.
```python
text = raw.strip().lower()
text = re.split(r"\d", text, maxsplit=1)[0]
text = " ".join(text.split())        # "mac os x"
```
Guard first: `None` or blank input raises `ValueError` before any of this.

--- code #card-a64a53d2cdaf55ad
Set `text` to the normalised form of `raw`: stripped, lowercased, cut at the first digit, with runs of whitespace collapsed to one space.
```python
import re
raw = "  Mac OS   X 10.15.7 "
```
check: text == "mac os x"
solution: text = re.split(r"\d", raw.strip().lower(), maxsplit=1)[0]
solution: text = " ".join(text.split())
> The split at the first digit drops the version; `split()` with no argument breaks on any whitespace and ignores the ends, so joining with one space gives the clean key to look up.

--- teach #card-6c96f0cabf6f5c67
### Try the whole text, then the first word; add the property
"windows server" is not a value or an alias, but its first word is. `text.split(" ", 1)[0]` is the first word. Try both candidates in order and raise when neither matches. The `is_apple` property is a membership test on `self`.
```python
for candidate in (text, text.split(" ", 1)[0]):
    member = _lookup(cls, candidate)
    if member is not None:
        return member
raise ValueError(f"unknown platform: {raw!r}")

@property
def is_apple(self):
    return self in (Platform.MAC, Platform.IOS)
```

--- fill #card-87a5eee345d9555c
Complete the property so it is True for MAC and IOS only.
```python
@property
def is_apple(self):
    return self ___ (Platform.MAC, Platform.IOS)
```
answer: in
> Inside a property on an Enum, `self` is the member. `in` against a tuple of members is the clearest way to say "one of these".

--- exercise 8.3 #card-fbd659659aa953d1

--- recap #card-2c7f8eb2baf75a59
- An Enum member has `.name` and `.value`; `Platform("mac")` looks up by value or raises.
- Wrap the lookup in `try`/`except ValueError` to get `None`; then `ALIASES.get`.
- Lookup tables go at module level, after the class, or they become members.
- Normalise: strip, lower, cut at the first digit, collapse spaces; then try the whole text, then the first word.
