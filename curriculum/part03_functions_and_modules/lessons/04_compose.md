# Functions are values

--- teach
### A function name without parentheses is a value
`str.strip` is the function; `str.strip()` calls it. You can store the function in a variable, put it in a list, or pass it to another function. Add the parentheses only when you want it to run.
```python
>>> step = str.lower
>>> step("MBP")
'mbp'
>>> steps = [str.strip, str.lower]
>>> steps[0]("  x ")
'x'
```
`[str.strip()]` is the classic slip: it calls with no argument and crashes.

--- code
Set `steps` to a list holding the `str.strip` and `str.lower` functions (not called), then set `value` by applying each step to `raw` in a loop.
```python
raw = "  MBP-J-DOE "
```
check: value == "mbp-j-doe"
check: steps[0] is str.strip
solution: steps = [str.strip, str.lower]
solution: value = raw
solution: for step in steps:
solution:     value = step(value)
> The list stores the functions themselves; the loop adds the parentheses, calling each one with the current value.

--- predict
What does this print?
```python
def double(n):
    return n * 2

f = double
print(f(4))
```
answer: 8
> `f = double` gives the same function a second name. Calling `f(4)` runs `double`'s body.

--- teach
### `callable` checks before you trust
`callable(x)` is True when `x` can be called: functions, methods, `len`, `str.strip`. Strings and `None` are not callable. Check every argument up front and raise `TypeError`, so a misplaced `"strip"` fails where it was written, not later in the middle of a pipeline.
```python
>>> callable(str.lower)
True
>>> callable("strip")
False
```

--- fill
Complete the check so a non-function argument is rejected.
```python
for f in funcs:
    if not ___(f):
        raise TypeError(f"{f!r} is not callable")
```
answer: callable
> `callable(f)` is the built-in test. `TypeError` is right because the argument is the wrong kind of thing, not a bad value of the right kind.

--- teach
### A function can build and return another function
Define an inner function inside the outer one and `return` it, without calling it. The inner function keeps using the outer function's variables even after the outer has returned. That is a closure.
```python
def make_adder(k):
    def add(x):
        return x + k
    return add

>>> add_ten = make_adder(10)
>>> add_ten(5)
15
```
Every call to `make_adder` makes a fresh `add` with its own `k`, so `make_adder(1)` and `make_adder(10)` do not interfere.

--- code
Write the body of `make_multiplier(k)`: it returns a function that multiplies its argument by `k`. Then print `make_multiplier(3)(5)`.
```python
def make_multiplier(k):
```
expect: 15
check: make_multiplier(2)(10) == 20
solution:     def multiply(x):
solution:         return x * k
solution:     return multiply
solution: print(make_multiplier(3)(5))
> The inner `multiply` remembers `k` after `make_multiplier` has returned. `make_multiplier(3)` is a function; calling it with 5 gives 15.

--- predict
What does this print?
```python
def make_prefixer(prefix):
    def prefixer(s):
        return prefix + s
    return prefixer

tag = make_prefixer("mbp-")
print(tag("doe"))
```
answer: mbp-doe
> `make_prefixer("mbp-")` returns the inner `prefixer`, which remembers `prefix`. Calling it joins the two strings.

--- teach
### Right to left with `reversed`
`compose(f, g, h)(x)` must be `f(g(h(x)))`: the last function runs first. `reversed(funcs)` walks a sequence backwards. Inside the inner function, start with `x` and apply each function to the running result.
```python
def composed(x):
    for f in reversed(funcs):
        x = f(x)
    return x
```
With no functions at all, the loop does nothing and `x` comes back unchanged: the identity function, for free.

--- quiz
What is `compose(lambda x: x + 1, lambda x: x * 10)(4)`?
- [ ] `50`
- [x] `41`
- [ ] `14`
> The last function runs first: `4 * 10` is `40`, then `+ 1` gives `41`. Applying them left to right would give `50`.

--- exercise 3.4

--- recap
- A function without `()` is a value you can store and pass.
- `callable(x)` tests it; raise `TypeError` for anything else.
- An inner function returned from an outer one keeps the outer's variables (a closure).
- `reversed(funcs)` applies the last function first.
