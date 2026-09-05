# Values and names

--- teach #card-b76e617005a0548e
### Python remembers things by name
A program works with values: a number, a piece of text, a yes/no. You keep a value around by giving it a name with `=`. Read it as "name gets value".
```python
hostname = "MBP-J-DOE"
ram_gb = 16
is_managed = True
```
Later, wherever you write `ram_gb`, Python swaps in `16`.

--- teach #card-4caba46855a05ba3
### Every value has a type
Text is a `str` (string), whole numbers are `int`, decimals are `float`, and `True`/`False` are `bool`. Python works the type out from what you wrote, and `type()` tells you what it decided.
```python
>>> type("16")
<class 'str'>
>>> type(16)
<class 'int'>
```
Quotes make text. `"16"` is text that happens to look like a number; `16` is a number.

--- code #card-e66ad63cb8085a87
Create a name `ram_gb` holding the whole number 16, then print its type.
```python
# your code here
```
expect: <class 'int'>
check: ram_gb == 16
solution: ram_gb = 16
solution: print(type(ram_gb))
> Two statements: `name = value` stores the number, and `print(type(ram_gb))` shows the type Python chose.

--- quiz #card-1b2b01a267ca5e87
What does `type(3.5)` return?
- [ ] `<class 'int'>`
- [x] `<class 'float'>`
- [ ] `<class 'str'>`
> A number with a decimal point is a float. `int` is for whole numbers only.

--- teach #card-a3ddbdd9e49550d4
### f-strings put values into text
Put an `f` before the opening quote and any expression inside `{}` is evaluated and dropped into the text. This is how you build messages, filenames, and report lines.
```python
>>> name = "MBP-J-DOE"
>>> f"Hello, {name}!"
'Hello, MBP-J-DOE!'
>>> f"{ram_gb} GB is {ram_gb * 1024} MB"
'16 GB is 16384 MB'
```

--- fill #card-d4ea3f8d120c5a0a
Complete the f-string so it reads `Device MBP-J-DOE is managed`.
```python
hostname = "MBP-J-DOE"
line = f"Device ___ is managed"
```
answer: {hostname}
> Inside an f-string, `{hostname}` is replaced by the value of the name `hostname`.

--- predict #card-6178bad21edd5bcd
What does this print?
```python
count = 2 + 3
print(f"{count} devices online")
```
answer: 5 devices online
> `2 + 3` was evaluated when `count` was created, so the f-string sees `5`.

--- code #card-02e0455984f252c8
Print exactly `MBP-J-DOE has 16 GB` using an f-string and the two names.
```python
hostname = "MBP-J-DOE"
ram_gb = 16
```
expect: MBP-J-DOE has 16 GB
solution: print(f"{hostname} has {ram_gb} GB")
> The braces pull in each value; everything else is typed literally, including the spaces.

--- teach #card-4742bf00465e5dc6
### Functions take values in and hand a value back
`def` names a function and lists its inputs. `return` hands the result to whoever called it. Printing shows text on screen; returning gives the value to the program. Tests, and interviewers, want the `return`.
```python
def label(hostname, ram_gb):
    return f"{hostname} ({ram_gb} GB)"

text = label("MBP-J-DOE", 16)   # text is now 'MBP-J-DOE (16 GB)'
```

--- quiz #card-79f70b00fbb05840
A test calls `greet("x")` and checks the result. Which body makes the test pass?
- [ ] `print(f"Hello, {name}!")`
- [x] `return f"Hello, {name}!"`
- [ ] `f"Hello, {name}!"`
> Only `return` sends the value back to the caller. `print` shows it on screen and returns `None`; a bare expression does nothing.

--- exercise 1.1 #card-183f0e2f52b8526e

--- recap #card-58b49f12f5c65bad
- `name = value` stores a value under a name.
- `str`, `int`, `float`, `bool` are the basic types; `type(x)` tells you which.
- `f"...{expr}..."` builds text from values.
- A function `return`s its answer; `print` only displays.
