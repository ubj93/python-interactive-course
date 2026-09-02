# Part 1 · Foundations: values, strings, and decisions

> **What you will be able to do:** read and write small Python functions that take
> values in, transform them, and return an answer. Every later part builds on this.
> If you have programmed before in any language, this part should take about an hour.

## Why start here

A Client Platform Engineering (CPE) interview rarely asks you to invert a binary tree.
It asks you to take a hostname, a serial number, a disk usage figure, or a line from a
log, and turn it into something a fleet tool can act on. That is exactly what this
part practises: **a value goes in, a decision or a new value comes out.**

Open a terminal and run `python3`. You get the REPL (read-eval-print loop), the
fastest way to check what a line of Python does. Every `>>>` block below is meant to
be typed in and played with.

## 1. Values and names

```python
>>> hostname = "MBP-J-DOE"
>>> ram_gb = 16
>>> usage = 0.83
>>> is_managed = True
```

Python figures out the type from the value: `str`, `int`, `float`, `bool`. A name is a
label stuck on a value; you can move the label to another value any time.

```python
>>> type(ram_gb)
<class 'int'>
>>> ram_gb = "sixteen"      # legal, but a bad idea: keep a name's type stable
```

`None` is the "no value" value. Functions that do not `return` anything return `None`.

### Converting between types

```python
>>> int("42")       # 42
>>> float("3.5")    # 3.5
>>> str(16)         # '16'
>>> int("42GB")     # ValueError: invalid literal for int() with base 10
>>> bool("")        # False   (empty string, 0, None, [], {} are all "falsy")
>>> bool("no")      # True    (any non-empty string is truthy, even "False")
```

That last line is a classic interview gotcha. `bool("False")` is `True`.

## 2. Strings

Strings are immutable sequences of characters. You never change a string, you make a
new one.

```python
>>> s = "  MBP-j-doe.corp.example.com \n"
>>> s.strip()                 # 'MBP-j-doe.corp.example.com'
>>> s.strip().lower()         # 'mbp-j-doe.corp.example.com'
>>> s.strip().lower().split(".")   # ['mbp-j-doe', 'corp', 'example', 'com']
>>> "mbp-j-doe".upper()       # 'MBP-J-DOE'
>>> "mbp-j-doe".startswith("mbp")   # True
>>> "abc" in "xabcx"          # True
>>> len("serial")             # 6
```

Method calls chain because each one returns a new string. Read left to right.

### Indexing and slicing

```python
>>> serial = "C02XG1234ABC"
>>> serial[0]        # 'C'
>>> serial[-1]       # 'C'   (negative counts from the end)
>>> serial[:3]       # 'C02'  (start at 0, stop before 3)
>>> serial[3:]       # 'XG1234ABC'
>>> serial[-3:]      # 'ABC'
>>> serial[::-1]     # 'CBA4321GX20C' (step -1 reverses)
```

Slices never raise on out-of-range bounds; indexes do.

### f-strings

Build strings with `f"..."` and put expressions inside `{}`. Learn the format spec
mini-language: it shows up in every reporting script you will ever write.

```python
>>> name, pct = "MBP-J-DOE", 0.8347
>>> f"{name}: {pct:.1%}"          # 'MBP-J-DOE: 83.5%'
>>> f"{pct:.2f}"                  # '0.83'
>>> f"{name:<12}|"                # 'MBP-J-DOE   |'   left-align, width 12
>>> f"{name:>12}|"                # '   MBP-J-DOE|'   right-align
>>> f"{1234567:,}"                # '1,234,567'
>>> f"{255:#x}  {255:08b}"        # '0xff  11111111'
>>> f"{name=}"                    # "name='MBP-J-DOE'"   handy for debugging
```

### Useful string methods you should know cold

| Method | Example | Result |
|---|---|---|
| `strip` / `lstrip` / `rstrip` | `" a ".strip()` | `'a'` |
| `lower` / `upper` / `title` | `"aBc".lower()` | `'abc'` |
| `split` | `"a,b,,c".split(",")` | `['a', 'b', '', 'c']` |
| `split` (no arg) | `" a  b ".split()` | `['a', 'b']` (any whitespace, no empties) |
| `join` | `"-".join(["a", "b"])` | `'a-b'` |
| `replace` | `"a.b.c".replace(".", "/")` | `'a/b/c'` |
| `startswith` / `endswith` | `"x.plist".endswith(".plist")` | `True` |
| `find` | `"abc".find("c")` | `2` (or `-1` if absent) |
| `isdigit` / `isalpha` / `isalnum` | `"123".isdigit()` | `True` |
| `zfill` | `"7".zfill(3)` | `'007'` |
| `partition` | `"k=v=w".partition("=")` | `('k', '=', 'v=w')` |

## 3. Numbers

```python
>>> 7 / 2       # 3.5    true division always returns float
>>> 7 // 2      # 3      floor division
>>> 7 % 2       # 1      remainder (modulo)
>>> 2 ** 10     # 1024
>>> round(2.675, 2)   # 2.67   floats are binary; do not use them for money
>>> abs(-3), max(3, 9), min(3, 9)
```

`1024 ** 3` bytes is a gibibyte (GiB). Vendors sell "1 TB" drives using `1000 ** 4`.
Be explicit about which you mean in code comments; interviewers notice.

## 4. Making decisions

```python
def disk_status(pct: float) -> str:
    if pct >= 0.95:
        return "CRIT"
    elif pct >= 0.80:
        return "WARN"
    else:
        return "OK"
```

Points worth knowing:

- Indentation *is* the block structure. Four spaces, always.
- Conditions are evaluated top to bottom; the first true branch wins. Order your
  thresholds from most specific to least.
- `and`, `or`, `not` are the boolean operators. `or` returns the first truthy operand,
  which gives you defaults: `name = given or "unknown"`.
- Chained comparisons read like maths: `0 <= pct <= 1`.
- Early return keeps functions flat. Prefer several `if ...: return` over deep nesting.
- `x is None` not `x == None`. `is` compares identity and is the idiom for `None`.

The conditional expression (ternary) fits small cases:

```python
label = "managed" if is_managed else "unmanaged"
```

## 5. Functions as contracts

Every exercise in this course is a function you complete. Read the signature and the
docstring as a contract: *these inputs, this output, these edge cases.*

```python
def bytes_to_human(n: int) -> str:
    """Return 1536 as '1.5 KiB', 0 as '0 B'."""
```

- Parameters are local names. The caller's variables are not changed when you rebind a
  parameter inside the function.
- `return` ends the function immediately. A function without `return` gives `None`.
- Type hints (`n: int`, `-> str`) are documentation; Python does not enforce them. Use
  them anyway. Interviewers read them as a sign you think about contracts.

## 6. Reading the tests

Each exercise ships with `test_exercise.py`. Tests are the real specification, and
reading them is not cheating: in a real job the ticket, the acceptance criteria, and
the existing tests are all you get. A typical test:

```python
def test_strips_whitespace(self):
    self.assertEqual(normalize_hostname("  MBP-J-DOE \n"), "mbp-j-doe")
```

`assertEqual(actual, expected)`. When it fails, the message shows both sides.

## Interview notes for this part

- **Say the types out loud.** "This takes a string and returns a float between 0 and
  1." Half of interview bugs are type confusions.
- **Ask about edge cases before coding.** Empty string? `None`? Negative numbers?
  Then handle them explicitly at the top of the function.
- **Prefer built-ins over hand-rolled loops.** `s.strip().lower()` beats a `for` loop
  over characters every time.

## Exercises

Run `course list 1`, then `course show 1.1`. Edit the file it names, run
`course run 1.1`, repeat until green. Then compare with `course solution 1.1`.

1. `greet_device` · say hello to a machine (f-strings)
2. `normalize_hostname` · clean up user-entered names
3. `disk_status` · thresholds and early returns
4. `os_family` · classify a platform string
5. `bytes_to_human` · loops meet formatting
6. `is_valid_serial` · validation with string methods
