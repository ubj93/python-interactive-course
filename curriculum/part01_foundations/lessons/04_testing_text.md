# Testing text

--- teach #card-1e7821976cd05a76
### `in` asks "is this inside that?"
For strings, `in` tests whether one piece of text appears inside another. It is case-sensitive, so normalise first.
```python
>>> "mac" in "macos 14.5"
True
>>> "Mac" in "macos 14.5"
False
```

--- predict #card-19bfc413dbfb52e1
What does this print?
```python
print("windows" in "Microsoft Windows 11".lower())
```
answer: True
> `lower()` turns the text into "microsoft windows 11", which contains "windows".

--- teach #card-162bd7ddb83a5584
### Normalise once, then test
Inventory data is messy: odd casing, stray spaces, sometimes nothing at all. Clean it once at the top of the function so every later test sees the same shape. `x or ""` gives you an empty string when `x` is `None`.
```python
s = (os_string or "").strip().lower()
```
If `os_string` is `None`, `(None or "")` is `""`, and `"".strip().lower()` is still `""` instead of crashing.

--- predict #card-39676e6f445e56cd
What does this print?
```python
os_string = None
print(repr((os_string or "").strip()))
```
answer: ''
> `None or ""` evaluates to `""`. `repr` shows the empty string as two quotes.

--- code #card-38583d84dbc259b8
Set `s` to the cleaned-up version of `os_string`: stripped and lowercased, and an empty string if `os_string` is None.
```python
os_string = "  Microsoft Windows 11 "
```
check: s == "microsoft windows 11"
solution: s = (os_string or "").strip().lower()
> The `or ""` handles None, then `strip()` and `lower()` do the cleaning. Test it in your head with `os_string = None` too.

--- teach #card-15cf34fda1ad5164
### Testing several possibilities at once
`startswith` accepts a tuple of prefixes. For "contains any of these", use `any()` with a generator: it stops at the first match.
```python
>>> s = "ubuntu 22.04"
>>> s.startswith(("ios", "ipados"))
False
>>> any(k in s for k in ("linux", "ubuntu", "debian"))
True
```

--- quiz #card-f0243bdd0d1e5fe0
What does `any(k in "rhel 9" for k in ("ubuntu", "rhel"))` return?
- [x] `True`
- [ ] `False`
- [ ] `'rhel'`
> `any` returns True as soon as one test is true. "rhel" is in "rhel 9". It returns a bool, never the matching item.

--- code #card-ea88497e4d385be2
Print `linux` if `s` contains any of the words in `LINUX_WORDS`, otherwise print `other`.
```python
s = "ubuntu 22.04"
LINUX_WORDS = ("linux", "ubuntu", "debian")
```
expect: linux
solution: if any(k in s for k in LINUX_WORDS):
solution:     print("linux")
solution: else:
solution:     print("other")
> `any(k in s for k in LINUX_WORDS)` reads as "any keyword is in s". Wrap it in an `if` to choose the label.

--- teach #card-80b72979f6d35d07
### Check the specific case before the general one
"iOS 17" contains "os", and "Mac OS X" contains "os x". If you test the general pattern first, the specific one never gets a chance. Order your checks from most specific to least, exactly like the thresholds in the last lesson.

--- exercise 1.4 #card-af824c4fe7aa5334

--- recap #card-4bffeeac3b4f5234
- `"a" in s` tests for a substring; normalise case first.
- `(x or "").strip().lower()` turns None and messy input into clean text.
- `startswith((..., ...))` and `any(k in s for k in ...)` test several options.
- Specific checks go before general ones.
