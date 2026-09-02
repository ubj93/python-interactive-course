# Part 7 · Errors and robustness

> **What you will be able to do:** read a traceback and know which exception to
> catch, write `try`/`except` that catches only what you mean, design your own
> exception classes, decide between "ask first" and "try and recover", report every
> problem in a record instead of only the first, and wrap a flaky call in a retry
> decorator that tests can run without waiting. About two hours with exercises.

## Why this matters

Fleet scripts run unattended on thousands of machines. The difference between a
script that gets adopted and one that gets ripped out is what happens on the
machine where the config file is missing, the API returns garbage, or a CSV row has
"n/a" where a number should be. Interviewers probe this constantly: "what happens
if the file is not there?" is the second question after "does it work?".

## 1. Exceptions are values with a type

When something goes wrong Python raises an exception object. If nothing catches it
the program stops and prints a traceback. Read tracebacks **bottom-up**: the last
line names the exception and the message; the lines above show where.

```python
>>> int("16GB")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: invalid literal for int() with base 10: '16GB'
```

The ones you will meet daily, and how they relate:

```
BaseException
 ├── KeyboardInterrupt, SystemExit         (do not catch these by accident)
 └── Exception
      ├── ValueError                       int("x"), wrong content
      │    └── json.JSONDecodeError
      ├── TypeError                        int(None), wrong type
      ├── KeyError, IndexError             missing key, bad index (both LookupError)
      ├── AttributeError                   None.strip()
      ├── OSError                          anything the OS refuses
      │    ├── FileNotFoundError
      │    ├── PermissionError
      │    ├── IsADirectoryError, NotADirectoryError
      │    └── TimeoutError
      └── RuntimeError, NotImplementedError
```

Catching a parent catches every child: `except OSError` also catches
`FileNotFoundError`. `except Exception` catches almost everything, which is almost
never what you want.

## 2. `try` / `except` / `else` / `finally`

```python
def read_config(path):
    try:
        f = open(path, encoding="utf-8")
    except FileNotFoundError:
        return {}                     # missing config means "use defaults"
    else:
        with f:                       # runs only if no exception was raised
            return json.load(f)
    finally:
        log("read_config attempted")  # runs no matter what, even after return
```

- Keep the `try` body **as small as possible**: one call that can fail. If ten lines
  sit inside `try`, you no longer know which one raised.
- `except A:` then `except B:` are tested in order; put the specific class first.
  `except (A, B):` handles two the same way.
- `except ValueError as e:` binds the exception; `str(e)` is the message.
- `else` is for the code that should run only on success but should not be
  protected by the `except`.
- `finally` is for cleanup. `with` is usually the nicer way to spell it.

### Catching too much

```python
try:
    value = int(row["ram_gb"])
except:                    # bare except: catches KeyboardInterrupt and SystemExit too
    value = 0
```

The bare `except:` and `except Exception: pass` are the two lines that get a
candidate marked down. They hide typos (`row["ram_bg"]` is a `KeyError` you would
never see), bugs, and Ctrl-C. Catch the exception you expect, by name, and let the
rest surface.

```python
try:
    value = int(row["ram_gb"])
except (ValueError, TypeError):    # "n/a", "", None
    value = 0
```

## 3. Raising

```python
def parse_port(text: str) -> int:
    port = int(text)
    if not 1 <= port <= 65535:
        raise ValueError(f"port {port} is out of range 1-65535")
    return port
```

A good message names **what** was wrong and **which value** caused it. `"invalid
port"` sends the on-call engineer back to add prints; `"port 70000 is out of range
1-65535"` does not.

Pick the type by meaning: bad content is `ValueError`, wrong type is `TypeError`,
missing key is `KeyError`. Reuse built-ins when they fit; the caller can then catch
the same class they already know.

### Re-raising and chaining

Inside an `except` block, a bare `raise` re-raises the current exception unchanged.
`raise NewError(...) from e` raises a different one **and records the original** as
`__cause__`, so the traceback shows "The above exception was the direct cause of the
following exception". Use it whenever you translate a low-level error into a
domain-level one:

```python
try:
    root = plistlib.loads(data)
except plistlib.InvalidFileException as e:
    raise ValueError(f"{path} is not a plist") from e
```

`raise ... from None` deliberately hides the original; use it sparingly.

## 4. Your own exceptions

A custom exception is a class that inherits from `Exception`. Give it a base class
per module and subclasses per situation, and store the useful facts as attributes
so callers do not have to parse the message.

```python
class ConfigError(Exception):
    """Base for everything wrong with a config file."""

class MissingKeyError(ConfigError):
    def __init__(self, key: str):
        super().__init__(f"missing required key: {key}")
        self.key = key

class InvalidValueError(ConfigError):
    def __init__(self, key: str, value):
        super().__init__(f"invalid value for {key}: {value!r}")
        self.key = key
        self.value = value
```

```python
>>> try:
...     port = get_int(config, "port")
... except MissingKeyError as e:
...     print("add", e.key)
... except ConfigError as e:            # catches every other ConfigError subclass
...     print("fix", e)
```

Always call `super().__init__(message)` so `str(e)` and the traceback work. Name
the class with an `Error` suffix; inherit from `ValueError` or `OSError` instead of
`Exception` when your error *is* one of those in spirit.

## 5. EAFP versus LBYL

| | Look Before You Leap | Easier to Ask Forgiveness than Permission |
|---|---|---|
| shape | `if key in d: v = d[key]` | `try: v = d[key] except KeyError:` |
| when | the check is cheap and complete | the check would duplicate the operation, or races |
| files | `if p.exists(): open(p)` (racy) | `try: open(p) except FileNotFoundError:` |
| strings | `if s.isdigit(): int(s)` (misses "-1", "+1") | `try: int(s) except ValueError:` |

Python culture leans EAFP: the operation itself is the most accurate check. The
`exists()` then `open()` pattern is the classic example of why: the file can vanish
between the two calls, and `exists()` says nothing about permissions.

Use LBYL when a failed attempt would have side effects, or when the condition is a
plain value test (`if not devices: return []`).

## 6. Fail fast or collect everything?

Two valid policies; the interview question is which one the caller needs.

- **Fail fast**: raise on the first problem. Right for programmer errors, for
  functions deep in a pipeline, and for "this cannot continue" situations.
- **Collect**: check every rule, gather the messages, return the list (or raise once
  with all of them). Right for validating user-facing input, where "fix these five
  fields" beats five round trips.

```python
def validate(record: dict) -> list:
    errors = []
    if "serial" not in record:
        errors.append("missing field: serial")
    if not isinstance(record.get("ram_gb"), int) or record.get("ram_gb", 0) <= 0:
        errors.append(f"ram_gb: must be a positive integer, got {record.get('ram_gb')!r}")
    return errors            # [] means valid
```

Note the shape: one `if` per rule, each appending a message in a fixed format, no
early return. Keep the message format identical across rules so callers (and tests)
can rely on it.

**Gotcha:** `isinstance(True, int)` is `True`. If a field must be an int, reject
bools explicitly.

## 7. Decorators, introduced by way of `retry`

A decorator is a function that takes a function and returns a replacement. The
`@name` line above a `def` is only sugar for `f = name(f)`.

```python
import functools

def log_calls(func):
    @functools.wraps(func)                     # keep func's __name__ and docstring
    def wrapper(*args, **kwargs):
        print("calling", func.__name__)
        return func(*args, **kwargs)
    return wrapper

@log_calls
def check_in(serial):
    ...
```

A decorator **with arguments** needs one more layer: `retry(times=3)` runs first and
returns the actual decorator.

```python
def retry(times=3, exceptions=(Exception,), sleep=time.sleep, delay=1.0, backoff=2.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wait = delay
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise                  # out of attempts: re-raise the last one
                    sleep(wait)
                    wait *= backoff
        return wrapper
    return decorator

@retry(times=3, exceptions=(ConnectionError,), sleep=time.sleep)
def fetch_inventory():
    ...
```

Why `sleep` is a parameter: the tests pass a fake that records the delays and returns
instantly, so a "retry three times with backoff" test takes microseconds. The same
trick applies to `now`, `random`, `runner` and `client`: inject anything that touches
the outside world.

| Decorator piece | Purpose |
|---|---|
| outer function | receives the options, returns `decorator` |
| `decorator(func)` | receives the function, returns `wrapper` |
| `wrapper(*args, **kwargs)` | runs each call; must return `func`'s result |
| `functools.wraps(func)` | copies `__name__`, `__doc__`, so tools and logs see the real name |

## 8. Robustness checklist

- Validate at the boundary (file, API, argv), trust the inside.
- Catch specific exceptions, close to where they can happen.
- Messages name the value that was wrong.
- Never mutate a shared default: return a copy when you hand back a fallback.
- Retry only what is safe to repeat (reads, idempotent writes), and cap the attempts.
- Let unexpected exceptions propagate; a crash with a traceback beats silent
  corruption.

## Interview notes for this part

- **Say which exception, and why that one.** "This is a `ValueError` because the
  type is right and the content is wrong" shows you know the hierarchy.
- **Ask about policy.** Skip bad rows or abort? Return a default or raise? Retry how
  many times? These are product decisions; ask, then encode the answer visibly.
- **Keep `try` blocks tiny.** Interviewers watch for a `try` wrapped around twenty
  lines with a bare `except` at the bottom.
- **Inject the clock.** The moment you write `time.sleep`, say "I will make this a
  parameter so tests do not wait".
- **The trap:** `except Exception: pass`. If you must swallow, log it, and catch the
  narrowest class that fits.

## Exercises

Run `course list 7`, then `course show 7.1`, and so on.

1. `safe_int` · catch `ValueError` and `TypeError`, return a default
2. `parse_port` · raise `ValueError` with a message that names the problem
3. `config_error` · a custom exception hierarchy with attributes and `raise from`
4. `read_json_or_default` · treat a missing file and broken JSON differently
5. `validate_device_record` · collect every error instead of stopping at the first
6. `retry` · a decorator with arguments, injected `sleep`, re-raise after n attempts
