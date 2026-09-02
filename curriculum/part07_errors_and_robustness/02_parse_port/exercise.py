"""Parse a TCP port with helpful errors.

A config file has a `port` setting and people type all sorts of things into
it. Write `parse_port(value)` that returns the port as an int, or raises an
exception whose message tells the reader exactly what to fix.

Accept:
- an int (not a bool) in the range 1..65535, returned unchanged
- a str made of digits, with surrounding whitespace allowed and leading zeros
  allowed ("080" -> 80), whose value is in range

Raise:
- TypeError when `value` is not an int or a str (None, float, bool, list ...);
  the message must contain the type name, e.g. "expected int or str, got float"
- ValueError "port is empty" when the string is empty or only whitespace
- ValueError when the string is not all digits (signs, dots, letters, spaces
  inside); the message must contain the original text in quotes, e.g.
  "port must be digits only, got '80a'"
- ValueError when the number is outside 1..65535; the message must contain
  the number and the text "out of range", e.g. "port 70000 is out of range 1-65535"

Examples:
    >>> parse_port("8080")
    8080
    >>> parse_port(" 443 ")
    443
    >>> parse_port("0")
    Traceback (most recent call last):
    ValueError: port 0 is out of range 1-65535
    >>> parse_port("80a")
    Traceback (most recent call last):
    ValueError: port must be digits only, got '80a'
"""
from typing import Union


def parse_port(value: Union[int, str]) -> int:
    raise NotImplementedError("write parse_port")
