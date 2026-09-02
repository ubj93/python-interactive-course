"""A custom exception hierarchy for config errors.

Our agent reads settings from a dict such as {"mdm_url": "...", "port": "8443"}.
Callers want to catch "anything wrong with the config" in one place but still
be able to tell a missing key from a bad value. Build a small hierarchy and two
accessor functions.

Exceptions:
- `ConfigError(Exception)`: the base class. Plain `Exception` behaviour; it takes
  a message like any exception.
- `MissingKeyError(ConfigError)`: constructed as MissingKeyError(key). Its
  message is exactly "missing required key: <key>" and it has a `.key` attribute.
- `InvalidValueError(ConfigError)`: constructed as InvalidValueError(key, value).
  Its message is exactly "invalid value for <key>: <value!r>" and it has `.key`
  and `.value` attributes.

Functions:
- `get_required(config, key)` returns config[key], or raises MissingKeyError(key)
  when the key is absent. A key that is present with value None or "" is
  returned as-is; only absence is an error.
- `get_int(config, key)` returns config[key] converted with int(). A missing key
  raises MissingKeyError. If int() fails (ValueError or TypeError), raise
  InvalidValueError(key, value) *chained* to the original exception with
  `raise ... from`, so `err.__cause__` is the ValueError/TypeError.

Both exception classes must call super().__init__ with the message so str(err)
and tracebacks work.

Examples:
    >>> get_required({"mdm_url": "https://mdm"}, "mdm_url")
    'https://mdm'
    >>> get_required({}, "mdm_url")
    Traceback (most recent call last):
    MissingKeyError: missing required key: mdm_url
    >>> get_int({"port": "8443"}, "port")
    8443
    >>> try:
    ...     get_int({"port": "https"}, "port")
    ... except ConfigError as e:
    ...     (type(e).__name__, e.key, e.value, str(e))
    ('InvalidValueError', 'port', 'https', "invalid value for port: 'https'")
"""
from typing import Any, Dict


class ConfigError(Exception):
    """Base class for configuration problems."""


class MissingKeyError(ConfigError):
    def __init__(self, key: str):
        raise NotImplementedError("write MissingKeyError.__init__")


class InvalidValueError(ConfigError):
    def __init__(self, key: str, value: Any):
        raise NotImplementedError("write InvalidValueError.__init__")


def get_required(config: Dict[str, Any], key: str) -> Any:
    raise NotImplementedError("write get_required")


def get_int(config: Dict[str, Any], key: str) -> int:
    raise NotImplementedError("write get_int")
