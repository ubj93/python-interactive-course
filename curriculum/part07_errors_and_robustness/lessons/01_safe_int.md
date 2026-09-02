# Catching the right error

--- teach
### An exception has a type and a message
When something goes wrong, Python raises an exception and, if nobody catches it, stops with a traceback. Read a traceback from the bottom: the last line names the type and the message. `int()` raises two different types depending on what went wrong.
```python
>>> int("16 GB")
ValueError: invalid literal for int() with base 10: '16 GB'
>>> int(None)
TypeError: int() argument must be a string, a bytes-like object or a real number, not 'NoneType'
```
`ValueError`: right type, wrong content. `TypeError`: wrong type altogether.

--- quiz
Which exception does `int("3.5")` raise?
- [x] `ValueError`
- [ ] `TypeError`
- [ ] It returns `3`
> `"3.5"` is a string, so the type is fine, but the content is not a whole number. That is `ValueError`. `int()` never rounds text.

--- teach
### What `int()` accepts
Strings with surrounding spaces and a sign are fine. Floats are truncated toward zero. Anything else is an error.
```python
>>> int(" -3 "), int("+7"), int("007")
(-3, 7, 7)
>>> int(3.9), int(-3.9)
(3, -3)
```
`"1,024"` and `""` raise `ValueError`; a list or `None` raises `TypeError`.

--- code
Set `values` to the `int` of every string in `raw`.
```python
raw = [" 42 ", "-3", "+7", "007"]
```
check: values == [42, -3, 7, 7]
solution: values = [int(s) for s in raw]
> All four are accepted: `int()` ignores surrounding whitespace, reads a sign, and drops leading zeros.

--- predict
What does this print?
```python
print(int(" 42 "), int(-3.9))
```
answer: 42 -3
> `int()` strips whitespace from a string on its own, and truncates a float toward zero, so `-3.9` becomes `-3`, not `-4`.

--- teach
### `try` / `except` catches only what you name
Put the one call that can fail inside `try`. If it raises an exception of the named type, the `except` block runs instead of a crash. A tuple names several types at once.
```python
try:
    return int(value)
except (ValueError, TypeError):
    return default
```
Keep the `try` body tiny, one call, so you know exactly which line raised.

--- code
Complete `to_int`: return `int(value)`, or `None` when the conversion raises `ValueError` or `TypeError`.
```python
def to_int(value):
```
check: to_int("42") == 42
check: to_int("n/a") is None
check: to_int(None) is None
solution:     try:
solution:         return int(value)
solution:     except (ValueError, TypeError):
solution:         return None
> The `try` body is the single call that can fail. The tuple names both conversion errors; `"n/a"` raises the first, `None` raises the second.

--- fill
Complete the line so both bad content and bad types fall through to the default.
```python
try:
    return int(value)
except (ValueError, ___):
    return default
```
answer: TypeError
> `int(None)` and `int([1, 2])` raise `TypeError`; `int("abc")` raises `ValueError`. The tuple catches both and nothing else.

--- teach
### Do not catch everything
A bare `except:` or `except Exception:` catches typos, bugs and even Ctrl-C. The last test hands `safe_int` an object whose `__int__` raises `RuntimeError`; that must still crash, because it is not a conversion problem. Name the exceptions you expect and let the rest surface.
```python
try:
    return int(value)
except:                # catches everything, hides bugs: do not write this
    return default
```

--- quiz
Why is `except Exception:` wrong in `safe_int`?
- [ ] It does not catch `ValueError`
- [x] It also hides unrelated errors, like a `RuntimeError` from a bug
- [ ] It is slower than naming the exceptions
> `Exception` is the parent of almost every error, so it swallows things that are not conversion failures. Catch the two you expect by name.

--- exercise 7.1

--- recap
- `ValueError` is right type, wrong content; `TypeError` is wrong type.
- `int()` accepts padded, signed strings and truncates floats.
- `try:` one call, `except (ValueError, TypeError):` the fallback.
- Never a bare `except:`; let unexpected errors crash.
