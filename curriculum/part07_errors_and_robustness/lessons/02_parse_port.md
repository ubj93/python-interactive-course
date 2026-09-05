# Raising helpful errors

--- teach #card-12c3810ee9d95e86
### `raise` with a message that names the value
`raise ValueError("...")` stops the function and hands the error to the caller. A good message says what was wrong **and which value** caused it. `"invalid port"` sends the on-call engineer back to add prints; `"port 70000 is out of range 1-65535"` does not.
```python
if not 1 <= port <= 65535:
    raise ValueError(f"port {port} is out of range 1-65535")
```

--- teach #card-2749ec49b3965f2c
### `!r` puts the value in quotes
In an f-string, `{text!r}` inserts the `repr` of the value: a string comes out with quotes, so the reader can see stray spaces and tell `'80a'` from `80a`. Numbers and `None` come out as they are.
```python
>>> text = "80a"
>>> f"port must be digits only, got {text!r}"
"port must be digits only, got '80a'"
```

--- predict #card-c68e3fc548c15d0d
What does this print?
```python
text = "http"
print(f"got {text!r}")
```
answer: got 'http'
> `!r` uses `repr`, which wraps a string in single quotes. Plain `{text}` would print `got http`.

--- teach #card-1a634c0390dc537e
### `TypeError` for the wrong type, with the type's name
When the value is not an `int` or a `str` at all, the problem is the type, so raise `TypeError`. `type(value).__name__` gives the short name, such as `float` or `NoneType`, for the message.
```python
if not isinstance(value, (int, str)):
    raise TypeError(f"expected int or str, got {type(value).__name__}")
```

--- predict #card-d032e3a2dda45a8e
What does this print?
```python
print(type(None).__name__, type(8.0).__name__)
```
answer: NoneType float
> `type(x)` is the class of the value and `__name__` is its name as text. `None` is the only value of class `NoneType`.

--- teach #card-93bcf2f750085967
### `bool` is an `int`: reject it explicitly
`True` and `False` are instances of `int` in Python, so `isinstance(True, int)` is `True`. If bools are not welcome, check for them first, before the `int` check.
```python
if isinstance(value, bool):
    raise TypeError("expected int or str, got bool")
```

--- quiz #card-bbd791e637e058fb
What does `isinstance(True, int)` return?
- [x] `True`
- [ ] `False`
- [ ] It raises `TypeError`
> `bool` is a subclass of `int`; `True` is `1` with a nicer name. Any "must be an int" rule needs an explicit bool check.

--- teach #card-8fb4d3a8fea051b2
### Strings: strip, then test with `isdigit`
For a string, strip the whitespace, then check three things in order: empty, not all digits, out of range. `str.isdigit()` is `True` only when every character is a digit, so `"-1"`, `"8.0"` and `"8 0"` all fail it, while `"080"` passes and `int("080")` is `80`.
```python
text = value.strip()
if not text:
    raise ValueError("port is empty")
if not text.isdigit():
    raise ValueError(f"port must be digits only, got {text!r}")
port = int(text)
```
Then run the same range check you use for ints.

--- code #card-608b8d505ab153a0
Complete `digits_port`: strip `text`; raise `ValueError("port is empty")` if nothing is left; raise `ValueError(f"port must be digits only, got {text!r}")` if it is not all digits; otherwise return `int(text)`.
```python
def digits_port(text):
```
check: digits_port(" 443 ") == 443
check: digits_port("080") == 80
solution:     text = text.strip()
solution:     if not text:
solution:         raise ValueError("port is empty")
solution:     if not text.isdigit():
solution:         raise ValueError(f"port must be digits only, got {text!r}")
solution:     return int(text)
> Strip once, then the checks go from cheapest to most specific. `"080".isdigit()` is `True` and `int("080")` is `80`, so leading zeros are fine.

--- fill #card-5e197506d4125185
Complete the test so only pure digit strings continue.
```python
if not text.___():
    raise ValueError(f"port must be digits only, got {text!r}")
```
answer: isdigit
> `isdigit()` rejects signs, dots, letters and inner spaces in one call, which is exactly the list of things the spec says to refuse.

--- exercise 7.2 #card-852b80a6b10e57e8

--- recap #card-970c9a45437250d3
- `raise ValueError(f"... {value} ...")`: name what was wrong and which value.
- `{x!r}` puts strings in quotes in a message.
- `TypeError` for wrong types; `type(value).__name__` for the message.
- `bool` is an `int`: reject it before the `int` check.
- Strings: `strip()`, empty check, `isdigit()`, then the range check.
