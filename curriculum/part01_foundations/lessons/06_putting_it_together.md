# Putting it together: validation

--- teach
### Validation is a series of gates
A validator answers one question: is this input acceptable? Write it as gates in order: cheap, common rejections first, then the detailed rules. Each gate returns `False` on its own; if the input gets past every gate, return `True`.
```python
def is_ok(serial):
    if not serial:              # None or empty string
        return False
    if len(serial) != 7:
        return False
    return True
```

--- predict
What does this print?
```python
print(len("C02XG1234ABC"))
```
answer: 12
> `len` counts characters. Twelve characters is the long Apple serial format.

--- teach
### Checking every character
`for ch in serial` walks the string one character at a time. Combine it with `any()` or `all()` to ask "does at least one character..." or "do all characters...". A set of allowed characters makes the membership test fast and explicit.
```python
ALLOWED = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

all(ch in ALLOWED for ch in serial)      # every character is allowed
any(ch.isdigit() for ch in serial)       # at least one digit
```

--- fill
Complete the expression that is True when the serial contains at least one digit.
```python
has_digit = any(ch.___() for ch in serial)
```
answer: isdigit
> `str.isdigit()` is True for a single digit character. `any` stops as soon as it finds one.

--- quiz
Why is `serial.isalnum()` not enough to check "uppercase letters and digits only"?
- [ ] It returns a string, not a bool
- [x] It also accepts lowercase and accented letters like `ä`
- [ ] It fails on strings longer than 10 characters
> `isalnum` is true for any letter or digit in any alphabet and any case. The spec allows only A-Z and 0-9, so compare against an explicit set.

--- teach
### Return the comparison itself
When the answer is a yes/no, return the expression instead of wrapping it in `if ... return True else return False`.
```python
return len(serial) in (10, 12)
```
`in` with a tuple tests membership in a fixed set of choices. Interviewers read this as fluent Python.

--- exercise 1.6

--- recap
- Validators are ordered gates; reject early, accept at the end.
- `for ch in s` walks characters; `all(...)` and `any(...)` summarise them.
- Compare against an explicit set of allowed characters rather than `isalnum`.
- Return boolean expressions directly.
