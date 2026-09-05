# A retry decorator

--- teach #card-630f894f49e05b46
### A decorator is a function that wraps a function
A decorator takes a function and returns a replacement, usually an inner `wrapper` that does something extra and then calls the original. The `@name` line above a `def` is only a shortcut for `func = name(func)`.
```python
def shout(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).upper()
    return wrapper

@shout
def label():
    return "mbp"
```
`*args, **kwargs` in `wrapper` passes every argument straight through, so the wrapper works for any function.

--- code #card-67e91a163a7c54cf
Write a decorator `shout` whose wrapper returns the upper-cased result of the wrapped function, then set `loud = shout(label)`.
```python
def label(name):
    return f"host {name}"
```
check: loud("mbp") == "HOST MBP"
check: label("mbp") == "host mbp"
solution: def shout(func):
solution:     def wrapper(*args, **kwargs):
solution:         return func(*args, **kwargs).upper()
solution:     return wrapper
solution: loud = shout(label)
> `shout(label)` returns `wrapper`, which calls the original and changes its result. `label` itself is untouched; `@shout` above the `def` would have rebound the name instead.

--- predict #card-6bf5dde9b6935cc7
What does this print?
```python
def shout(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).upper()
    return wrapper

@shout
def label(name):
    return f"host {name}"

print(label("mbp"))
```
answer: HOST MBP
> `label` now refers to `wrapper`. Calling it runs the original, gets `"host mbp"`, and upper-cases it on the way out.

--- teach #card-3419fefbe4335f48
### A decorator with arguments needs one more layer
`@retry(times=3)` calls `retry(times=3)` first; whatever that returns is the real decorator. So `retry` is a function that returns `decorator`, which returns `wrapper`. Three `def`s, nested. The inner ones can read `times` and the other options because they are closures.
```python
def retry(times=3, sleep=time.sleep):
    def decorator(func):
        def wrapper(*args, **kwargs):
            ...
        return wrapper
    return decorator
```
Validate the options in the outer function: `times < 1` should raise `ValueError` at decoration time, before any call.

--- predict #card-434dd0572b305c7b
What does this print?
```python
def repeat(times):
    def decorator(func):
        def wrapper():
            return func() * times
        return wrapper
    return decorator

@repeat(3)
def dash():
    return "-"

print(dash())
```
answer: ---
> `repeat(3)` returns `decorator`, which wraps `dash`. `wrapper` remembers `times` from the outer call and repeats the string three times.

--- teach #card-8ce8311d9d825d57
### The loop: try, catch, sleep, and re-raise on the last attempt
Count attempts from 1 to `times`. On success, `return` the result at once. On a listed exception, if attempts remain, sleep and grow the wait; if this was the last attempt, a bare `raise` re-raises the very same exception object. Exceptions not in the tuple are never caught, so they propagate immediately.
```python
wait = delay
for attempt in range(1, times + 1):
    try:
        return func(*args, **kwargs)
    except exceptions:
        if attempt == times:
            raise
        sleep(wait)
        wait *= backoff
```

--- quiz #card-37ae85eca5fa5cca
With `times=3`, the function fails every time. How many calls and how many sleeps happen?
- [ ] 3 calls, 3 sleeps
- [x] 3 calls, 2 sleeps
- [ ] 4 calls, 3 sleeps
> `times` is the total number of attempts. There is no sleep after the final failure; the bare `raise` runs instead.

--- predict #card-4dc8d187ebe75d2b
What does this print?
```python
wait, waits = 0.5, []
for attempt in range(1, 4):
    if attempt == 3:
        break
    waits.append(wait)
    wait *= 3.0
print(waits)
```
answer: [0.5, 1.5]
> The first wait is `delay`; each next one is the previous times `backoff`. The last attempt breaks out before recording a wait.

--- teach #card-d4e9d34d1dcd5b87
### Inject `sleep`; keep the name with `functools.wraps`
`sleep` is a parameter so tests pass a fake that records the delays and returns instantly. Never call `time.sleep` directly in the wrapper. And put `@functools.wraps(func)` on `wrapper` so the decorated function keeps its `__name__` and `__doc__`; without it every wrapped function is called `wrapper`.
```python
import functools

def decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ...
    return wrapper
```

--- fill #card-625b93b6a5895486
Complete the line so `check_in.__name__` stays `"check_in"` after decoration.
```python
@functools.___(func)
def wrapper(*args, **kwargs):
```
answer: wraps
> `functools.wraps(func)` copies `__name__`, `__doc__` and friends from `func` onto `wrapper`. Logs, tracebacks and the tests then see the real name.

--- exercise 7.6 #card-3a4858dbc2185726

--- recap #card-e1ef7e6c0d0e54a2
- A decorator takes a function and returns a `wrapper`; `@name` is `func = name(func)`.
- Arguments need a third layer: `retry(...)` returns `decorator`, which returns `wrapper`.
- Loop over attempts; `return` on success, bare `raise` on the last failure.
- The wait starts at `delay` and is multiplied by `backoff` after each sleep.
- Inject `sleep`; use `functools.wraps` to keep the function's name.
