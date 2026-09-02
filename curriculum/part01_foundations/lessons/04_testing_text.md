# Testing text

--- teach
### `in` asks "is this inside that?"
For strings, `in` tests whether one piece of text appears inside another. It is case-sensitive, so normalise first.
```python
>>> "mac" in "macos 14.5"
True
>>> "Mac" in "macos 14.5"
False
```

--- predict
What does this print?
```python
print("windows" in "Microsoft Windows 11".lower())
```
answer: True
> `lower()` turns the text into "microsoft windows 11", which contains "windows".

--- teach
### Normalise once, then test
Inventory data is messy: odd casing, stray spaces, sometimes nothing at all. Clean it once at the top of the function so every later test sees the same shape. `x or ""` gives you an empty string when `x` is `None`.
```python
s = (os_string or "").strip().lower()
```
If `os_string` is `None`, `(None or "")` is `""`, and `"".strip().lower()` is still `""` instead of crashing.

--- predict
What does this print?
```python
os_string = None
print(repr((os_string or "").strip()))
```
answer: ''
> `None or ""` evaluates to `""`. `repr` shows the empty string as two quotes.

--- teach
### Testing several possibilities at once
`startswith` accepts a tuple of prefixes. For "contains any of these", use `any()` with a generator: it stops at the first match.
```python
>>> s = "ubuntu 22.04"
>>> s.startswith(("ios", "ipados"))
False
>>> any(k in s for k in ("linux", "ubuntu", "debian"))
True
```

--- quiz
What does `any(k in "rhel 9" for k in ("ubuntu", "rhel"))` return?
- [x] `True`
- [ ] `False`
- [ ] `'rhel'`
> `any` returns True as soon as one test is true. "rhel" is in "rhel 9". It returns a bool, never the matching item.

--- teach
### Check the specific case before the general one
"iOS 17" contains "os", and "Mac OS X" contains "os x". If you test the general pattern first, the specific one never gets a chance. Order your checks from most specific to least, exactly like the thresholds in the last lesson.

--- exercise 1.4

--- recap
- `"a" in s` tests for a substring; normalise case first.
- `(x or "").strip().lower()` turns None and messy input into clean text.
- `startswith((..., ...))` and `any(k in s for k in ...)` test several options.
- Specific checks go before general ones.
