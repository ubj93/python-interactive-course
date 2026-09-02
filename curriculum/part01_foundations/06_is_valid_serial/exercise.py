"""Validate a serial number.

Our asset system accepts two serial formats. Write `is_valid_serial(serial)` that
returns True only when the input matches one of them exactly:

Apple style
- 10 or 12 characters
- uppercase letters A-Z and digits 0-9 only

Dell service tag
- exactly 7 characters
- uppercase letters and digits only
- must contain at least one digit

Anything else is invalid: lowercase letters, spaces, hyphens, other lengths,
empty strings, and None. Do not use the `re` module for this one; string
methods are enough and the point is to practise them.

Examples:
    >>> is_valid_serial("C02XG1234ABC")
    True
    >>> is_valid_serial("FVFXC123")
    False
    >>> is_valid_serial("7GH2K3Q")
    True
    >>> is_valid_serial("ABCDEFG")
    False
"""
from typing import Optional


def is_valid_serial(serial: Optional[str]) -> bool:
    raise NotImplementedError("write is_valid_serial")
