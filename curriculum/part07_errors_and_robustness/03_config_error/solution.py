"""Reference solutions for ConfigError, MissingKeyError, InvalidValueError, get_required, get_int."""
from typing import Any, Dict


# Best practice: a base class per module, one subclass per situation, facts stored as
# attributes and a message built once in __init__ via super().__init__.
class ConfigError(Exception):
    """Base class for configuration problems."""


class MissingKeyError(ConfigError):
    def __init__(self, key: str):
        super().__init__(f"missing required key: {key}")
        self.key = key


class InvalidValueError(ConfigError):
    def __init__(self, key: str, value: Any):
        super().__init__(f"invalid value for {key}: {value!r}")
        self.key = key
        self.value = value


# Presence is the question, so `in` is the right test; a value of None is still present.
def get_required(config: Dict[str, Any], key: str) -> Any:
    if key not in config:
        raise MissingKeyError(key)
    return config[key]


# Reuse get_required so "missing" is defined in exactly one place; translate the
# low-level conversion error into a domain error and keep the cause chained.
def get_int(config: Dict[str, Any], key: str) -> int:
    value = get_required(config, key)
    try:
        return int(value)
    except (ValueError, TypeError) as e:
        raise InvalidValueError(key, value) from e


# Clever: EAFP for get_required. KeyError -> MissingKeyError, chained with `from None`
# because the KeyError adds nothing the new message does not already say.
def get_required_eafp(config: Dict[str, Any], key: str) -> Any:
    try:
        return config[key]
    except KeyError:
        raise MissingKeyError(key) from None
