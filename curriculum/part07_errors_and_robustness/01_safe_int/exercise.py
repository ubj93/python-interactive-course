"""Convert to int without crashing.

Inventory exports are full of values that should be numbers but are not:
"n/a", "", None, "16 GB". Write `safe_int(value, default=0)` that returns
`int(value)` when the conversion works and `default` when it does not.

Rules:
- strings with surrounding whitespace and an optional sign convert: " 42 ",
  "-3", "+7"
- floats are truncated toward zero the way int() does: 3.9 -> 3, -3.9 -> -3
- anything int() rejects returns the default: "abc", "3.5", "1,024", "",
  None, lists (int raises ValueError or TypeError; catch exactly those two)
- `default` is returned as-is, whatever it is (None is allowed)
- do not catch every exception; only ValueError and TypeError

Examples:
    >>> safe_int("42")
    42
    >>> safe_int(" -3 ")
    -3
    >>> safe_int("n/a")
    0
    >>> safe_int(None, default=-1)
    -1
    >>> safe_int(3.9)
    3
"""
from typing import Any, Optional


def safe_int(value: Any, default: Optional[int] = 0) -> Optional[int]:
    raise NotImplementedError("write safe_int")
