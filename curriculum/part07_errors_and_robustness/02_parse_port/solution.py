"""Reference solutions for parse_port."""
from typing import Union

MIN_PORT, MAX_PORT = 1, 65535


# Best practice: check the type first (TypeError), then the text (ValueError), then the
# range (ValueError). Each message carries the offending value, formatted with !r for text.
def parse_port(value: Union[int, str]) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise TypeError(f"expected int or str, got {type(value).__name__}")
    if isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError("port is empty")
        if not text.isdigit():
            raise ValueError(f"port must be digits only, got {text!r}")
        port = int(text)
    else:
        port = value
    if not MIN_PORT <= port <= MAX_PORT:
        raise ValueError(f"port {port} is out of range {MIN_PORT}-{MAX_PORT}")
    return port


# Clever: convert str to int in a helper so the range check is written once. Same
# behaviour; shows how splitting "parse" from "validate" keeps each error in one place.
def _to_int(value: Union[int, str]) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise TypeError(f"expected int or str, got {type(value).__name__}")
    if isinstance(value, int):
        return value
    text = value.strip()
    if not text:
        raise ValueError("port is empty")
    if not text.isdigit():
        raise ValueError(f"port must be digits only, got {text!r}")
    return int(text)


def parse_port_split(value: Union[int, str]) -> int:
    port = _to_int(value)
    if not MIN_PORT <= port <= MAX_PORT:
        raise ValueError(f"port {port} is out of range {MIN_PORT}-{MAX_PORT}")
    return port
