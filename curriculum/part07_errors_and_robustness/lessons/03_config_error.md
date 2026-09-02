# Your own exceptions

--- teach
### An exception is a class that inherits from `Exception`
Write `class ConfigError(Exception): pass` and you have a new exception type. Raise it and catch it like any built-in one. A base class per module lets callers catch "anything wrong with the config" in one `except`.
```python
class ConfigError(Exception):
    """Base class for configuration problems."""

raise ConfigError("something is off")
```
Name exception classes with an `Error` suffix.

--- teach
### Subclasses carry facts as attributes
A subclass can take its own arguments, build the message, and store the useful facts on `self` so callers do not have to parse text. Always pass the message to `super().__init__(...)`, otherwise `str(e)` and the traceback are empty.
```python
class MissingKeyError(ConfigError):
    def __init__(self, key):
        super().__init__(f"missing required key: {key}")
        self.key = key
```
`MissingKeyError("port")` then has `.key == "port"` and `str(e) == "missing required key: port"`.

--- code
Define `MissingKeyError(ConfigError)` that takes `key`, has the message `missing required key: <key>`, and stores the key as `.key`.
```python
class ConfigError(Exception):
    """Base class for configuration problems."""
```
check: str(MissingKeyError("port")) == "missing required key: port"
check: MissingKeyError("port").key == "port"
check: issubclass(MissingKeyError, ConfigError)
solution: class MissingKeyError(ConfigError):
solution:     def __init__(self, key):
solution:         super().__init__(f"missing required key: {key}")
solution:         self.key = key
> `super().__init__(message)` gives the exception its text; `self.key = key` stores the fact so callers can read it without parsing the message.

--- fill
Complete the constructor so `str(e)` shows the message.
```python
class MissingKeyError(ConfigError):
    def __init__(self, key):
        super().___(f"missing required key: {key}")
        self.key = key
```
answer: __init__
> `super().__init__(message)` runs `Exception`'s own setup, which is what stores the message for `str(e)` and tracebacks.

--- predict
What does this print?
```python
class MissingKeyError(Exception):
    def __init__(self, key):
        super().__init__(f"missing required key: {key}")
        self.key = key

e = MissingKeyError("mdm_url")
print(str(e), "|", e.key)
```
answer: missing required key: mdm_url | mdm_url
> `str(e)` is the message handed to `super().__init__`; `e.key` is the attribute set afterwards. Both are available without raising.

--- teach
### `!r` in the message for values
`InvalidValueError(key, value)` needs the value shown as its `repr`: `'https'` with quotes, `None` and `3.5` without. `{value!r}` does that.
```python
class InvalidValueError(ConfigError):
    def __init__(self, key, value):
        super().__init__(f"invalid value for {key}: {value!r}")
        self.key = key
        self.value = value
```

--- teach
### Catching the base catches every subclass
`except ConfigError` catches `MissingKeyError` and `InvalidValueError` too. Put the specific class first if you want to treat it differently; Python tries `except` clauses top to bottom.
```python
try:
    port = get_int(config, "port")
except MissingKeyError as e:
    print("add", e.key)
except ConfigError as e:
    print("fix", e)
```

--- quiz
`get_int` raises `InvalidValueError`. Which `except` clause catches it?
- [ ] Only `except InvalidValueError:`
- [x] `except InvalidValueError:` or `except ConfigError:` or `except Exception:`
- [ ] Only `except Exception:`
> Catching a class catches all its subclasses. `InvalidValueError` is a `ConfigError`, which is an `Exception`, so any of the three works.

--- teach
### Translate a low-level error with `raise ... from`
`get_int` calls `int()` on the config value. When that raises `ValueError` or `TypeError`, raise your own `InvalidValueError` **from** it: the original is kept as `e.__cause__` and the traceback shows both. For the missing key, `get_required` is a plain `in` test; only absence is an error, `None` and `""` are returned as they are.
```python
try:
    return int(value)
except (ValueError, TypeError) as e:
    raise InvalidValueError(key, value) from e
```

--- fill
Complete the line so the original conversion error is kept as the cause.
```python
except (ValueError, TypeError) as e:
    raise InvalidValueError(key, value) ___ e
```
answer: from
> `raise X from e` sets `X.__cause__ = e`. The tests check that the cause is the original `ValueError` or `TypeError`.

--- exercise 7.3

--- recap
- `class ConfigError(Exception)` makes a new exception type.
- Subclasses call `super().__init__(message)` and store facts on `self`.
- `{value!r}` shows the value the way Python would.
- `except ConfigError` catches every subclass.
- `raise Custom(...) from e` keeps the original error as `__cause__`.
