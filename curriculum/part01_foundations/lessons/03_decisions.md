# Making decisions

--- teach
### if, elif, else
A program decides with `if`. The first condition that is true wins; the others are skipped. Indentation (four spaces) marks what belongs to each branch.
```python
if pct >= 0.95:
    status = "CRIT"
elif pct >= 0.80:
    status = "WARN"
else:
    status = "OK"
```
`elif` means "else, if". You can have as many as you need.

--- predict
What does this print?
```python
pct = 0.85
if pct >= 0.95:
    print("CRIT")
elif pct >= 0.80:
    print("WARN")
else:
    print("OK")
```
answer: WARN
> 0.85 is not >= 0.95, so the first branch is skipped; it is >= 0.80, so the second branch runs and the rest are ignored.

--- code
Print `WARN` if `pct` is 0.80 or more, otherwise print `OK`.
```python
pct = 0.9
```
expect: WARN
solution: if pct >= 0.80:
solution:     print("WARN")
solution: else:
solution:     print("OK")
> The condition line ends with a colon and the branch bodies are indented four spaces.

--- teach
### Order matters
Python checks branches top to bottom and stops at the first true one. If you tested `>= 0.80` first, 0.99 would be labelled WARN and never reach the CRIT check. Put the most specific (highest) threshold first.

--- teach
### Comparisons, and the special value None
`==`, `!=`, `<`, `<=`, `>`, `>=` compare values. Two comparisons can be chained: `0 <= x <= 1` means "x is between 0 and 1". `None` means "no value"; test for it with `is`, not `==`.
```python
>>> x = 0.5
>>> 0 <= x <= 1
True
>>> x is None
False
```

--- quiz
Which expression is true only when `x` is between 0 and 1 inclusive?
- [ ] `0 <= x or x <= 1`
- [x] `0 <= x <= 1`
- [ ] `x in (0, 1)`
> Chained comparison reads like maths. The `or` version is true for every number, and `in (0, 1)` only matches exactly 0 or 1.

--- fill
Complete the guard so it catches a missing value.
```python
if used ___ None:
    return "UNKNOWN"
```
answer: is
> `is None` is the idiom. `== None` usually works but `is` is faster, clearer, and what reviewers expect.

--- code
Write the body of `status`: return `"UNKNOWN"` when `used` is None, otherwise return `"OK"`. Then print `status(None)`.
```python
def status(used):
```
expect: UNKNOWN
check: status(0.5) == "OK"
solution:     if used is None:
solution:         return "UNKNOWN"
solution:     return "OK"
solution: print(status(None))
> The guard returns early, so the last `return "OK"` only runs for real values. The body lines are indented four spaces; the `print` is not, because it is outside the function.

--- teach
### Return early
Handle the bad cases first and `return` immediately. Every line after a guard can then assume the input is good, which keeps the function flat instead of nested.
```python
def disk_status(used):
    if used is None or not 0 <= used <= 1:
        return "UNKNOWN"
    if used >= 0.95:
        return "CRIT"
    ...
```
Once a function returns, nothing below runs, so no `else` is needed.

--- exercise 1.3

--- recap
- `if` / `elif` / `else`: the first true branch runs, the rest are skipped.
- Put the most specific condition first.
- `0 <= x <= 1` chains comparisons; `x is None` tests for no value.
- Guard clauses with early `return` keep functions flat.
