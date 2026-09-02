# Property lists

--- teach
### `plistlib` turns a plist into plain Python
macOS stores profiles and preferences as property lists. `plistlib.loads(data)` takes the raw `bytes` (XML or binary, it does not matter) and gives you `dict`, `list`, `str`, `int` and `bool`. `plistlib.dumps(obj)` goes the other way, which is handy for building test data.
```python
>>> import plistlib
>>> data = plistlib.dumps({"PayloadType": "Configuration", "n": 2})
>>> plistlib.loads(data)
{'PayloadType': 'Configuration', 'n': 2}
```
Read plist files with `open(path, "rb")`: the `b` gives bytes, which is what `loads` wants.

--- predict
What does this print?
```python
import plistlib
data = plistlib.dumps({"PayloadRemovalDisallowed": True})
print(plistlib.loads(data))
```
answer: {'PayloadRemovalDisallowed': True}
> The round trip preserves the type: the plist `<true/>` comes back as Python `True`, not the string `"true"`.

--- teach
### The shape of a configuration profile
The top level is a dict with `PayloadType` equal to `"Configuration"`, an identifier, a display name, and a `PayloadContent` list. Each entry in that list is a payload dict with its own `PayloadType`, `PayloadIdentifier` and usually a `PayloadDisplayName`. Treat everything except `PayloadType` as optional, because vendors leave keys out.
```python
{"PayloadType": "Configuration",
 "PayloadIdentifier": "com.corp.wifi",
 "PayloadContent": [
     {"PayloadType": "com.apple.wifi.managed",
      "PayloadIdentifier": "com.corp.wifi.1"}]}
```

--- teach
### Defaults for missing keys with `.get`
`d.get(key, default)` returns the default instead of raising `KeyError`. Use it for every optional key: `""` for text, `False` for the removal flag, `[]` for a missing `PayloadContent`. For a payload with no display name, fall back to that payload's type.
```python
content = root.get("PayloadContent", [])
name = payload.get("PayloadDisplayName", payload["PayloadType"])
```
`bool(root.get("PayloadRemovalDisallowed", False))` makes sure the flag is a real bool.

--- code
Load `data`, then set `identifier` to its `PayloadIdentifier` and `count` to the number of payloads, which is 0 when `PayloadContent` is missing.
```python
import plistlib
data = plistlib.dumps({"PayloadType": "Configuration", "PayloadIdentifier": "com.corp.empty"})
```
check: identifier == "com.corp.empty"
check: count == 0
solution: root = plistlib.loads(data)
solution: identifier = root["PayloadIdentifier"]
solution: count = len(root.get("PayloadContent", []))
> `loads` gives a dict. The identifier is required, so `[]` is fine; `PayloadContent` is optional, so `.get(..., [])` turns "missing" into an empty list.

--- fill
Complete the line so a missing display name falls back to the payload's type.
```python
name = payload.get("PayloadDisplayName", ___)
```
answer: payload["PayloadType"]
> The second argument of `get` is used only when the key is missing, so a real display name wins when it exists.

--- teach
### Distinct, sorted types
`payload_types` must list each type once, in sorted order. Turn the list into a `set` to drop duplicates, then `sorted()` to get a list back in order.
```python
>>> sorted({"b", "a", "b"})
['a', 'b']
```

--- predict
What does this print?
```python
types = ["com.apple.wifi.managed", "com.apple.MCX.FileVault2", "com.apple.wifi.managed"]
print(sorted(set(types)))
```
answer: ['com.apple.MCX.FileVault2', 'com.apple.wifi.managed']
> `set` removes the duplicate; `sorted` orders the strings. Uppercase `M` sorts before lowercase `w`.

--- teach
### Turning two parse errors into one `ValueError`
Bad bytes make `plistlib.loads` raise `plistlib.InvalidFileException` or, for broken XML, `ExpatError`. Callers should not need to know either name. Catch both with a tuple, and raise `ValueError` **from** the original so the traceback shows both.
```python
try:
    root = plistlib.loads(data)
except (plistlib.InvalidFileException, ExpatError) as e:
    raise ValueError("not a valid plist") from e
```
`as e` names the caught error; `from e` records it as the cause. Then check the shape yourself: not a dict, or `PayloadType` not `"Configuration"`, is also a `ValueError`.

--- quiz
Why write `raise ValueError("not a valid plist") from e` instead of just `raise ValueError("not a valid plist")`?
- [ ] `from e` makes the new error a subclass of the old one
- [x] It records the original error as the cause, so the traceback shows what really went wrong
- [ ] Without `from e` the code does not run
> Both forms run. `from e` stores the original in `__cause__`, which the tests check and which on-call engineers rely on when reading the traceback.

--- exercise 6.6

--- recap
- `plistlib.loads(bytes)` reads XML or binary plists; `dumps` writes them.
- A profile is a dict with `PayloadType` `"Configuration"` and a `PayloadContent` list.
- `.get(key, default)` supplies defaults for optional keys.
- `sorted(set(xs))` gives distinct values in order.
- `except (A, B) as e: raise ValueError(...) from e` unifies parse errors.
