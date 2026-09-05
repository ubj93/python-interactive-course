# Running a pipeline

--- teach #card-ecee03d774e25de4
### Apply steps left to right
A pipeline is a list of functions applied in order: the output of one is the input of the next. Keep the running value in one name and overwrite it each pass.
```python
value = "  MBP-J-DOE "
for step in [str.strip, str.lower]:
    value = step(value)
>>> value
'mbp-j-doe'
```
An empty list of steps runs the loop zero times, so the value comes back unchanged.

--- code #card-7765133906e95ec1
Run `value` through every function in `steps`, in order, then print the result.
```python
value = "  MBP-J-DOE "
steps = [str.strip, str.lower]
```
expect: mbp-j-doe
solution: for step in steps:
solution:     value = step(value)
solution: print(value)
> Each pass overwrites `value` with the step's output, so the second step sees the stripped text and lowercases it.

--- predict #card-323c8a86c35f58d3
What does this print?
```python
value = 3
for step in [lambda n: n + 1, lambda n: n * 10]:
    value = step(value)
print(value)
```
answer: 40
> Left to right: `3 + 1` is 4, then `4 * 10` is 40. A pipeline runs in the opposite direction from `compose`.

--- teach #card-c4bafeb5932f5507
### `None` is not the same as falsy
`0`, `""` and `[]` are falsy: `if not value:` treats them as "nothing". But a pipeline that stops "when a step returns None" must let those through. Test `is None`, never `not value`.
```python
>>> value = 0
>>> value is None
False
>>> not value
True
```
Say "is None when I mean None" out loud; interviewers listen for it.

--- quiz #card-30e6d158f03f5730
A step returns `""`. What should `apply_pipeline` do next?
- [ ] Stop and return `None`, because `""` is falsy
- [x] Pass `""` to the next step
- [ ] Raise `ValueError`
> Only `None` stops the pipeline. `""`, `0` and `[]` are ordinary values that the next step receives.

--- teach #card-361ec1f7d23c542a
### Stop early with `return`
Inside the loop, check the result after each step. `return None` ends the function immediately, so later steps are never called. Check the starting value too, before the loop, so a `None` input calls nothing.
```python
if value is None:
    return None
for step in steps:
    value = step(value)
    if value is None:
        return None
return value
```

--- code #card-41079a8f4e445966
Write the body of `run(value, steps)`: apply the steps in order, return `None` as soon as a step returns `None`, otherwise return the final value.
```python
reject_lab = lambda h: None if h.startswith("lab-") else h
def run(value, steps):
```
check: run("mbp-01", [reject_lab, str.upper]) == "MBP-01"
check: run("lab-01", [reject_lab, str.upper]) is None
solution:     for step in steps:
solution:         value = step(value)
solution:         if value is None:
solution:             return None
solution:     return value
> The `is None` check sits inside the loop, so `return None` fires before `str.upper` ever runs on the rejected value.

--- fill #card-5d377d4c1d9e50ca
Complete the check that stops the pipeline as soon as a step drops the record.
```python
value = step(value)
if value ___ None:
    return None
```
answer: is
> `is None` is the identity test for the one value that means "drop this". `== None` usually works but is not the idiom.

--- teach #card-0ac48b9aeb125b8b
### Validate all steps before running any
A half-run pipeline is worse than none: the first step may already have written somewhere. So check every step with `callable` first, and only then start applying. `all(callable(s) for s in steps)` says it in one line.
```python
if not all(callable(s) for s in steps):
    raise TypeError("every step must be callable")
```
Order of the function body: validate steps, check for a `None` start, then the loop.

--- predict #card-ff58ccc320365286
What does this print?
```python
steps = [str.strip, "lower"]
print(all(callable(s) for s in steps))
```
answer: False
> `"lower"` is a string, not a function, so `callable` returns False for it and `all` is False. The pipeline should raise `TypeError` before any step runs.

--- exercise 3.5 #card-2cba5f3d31115bf4

--- recap #card-9aa3f8ecb9cd5d25
- Pipeline: `for step in steps: value = step(value)`.
- Only `None` stops it; `0`, `""`, `[]` pass through. Test with `is None`.
- `return` inside the loop stops before later steps run.
- Check `callable` on every step before running the first one.
