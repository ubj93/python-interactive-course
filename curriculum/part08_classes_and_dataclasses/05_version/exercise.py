"""A comparable Version type.

Compliance rules say "macOS must be at least 14.5". Comparing version strings
as strings gets that wrong ("14.10" < "14.5"), and comparing lists of ints
gets padding wrong ([14, 5] != [14, 5, 0]). Write a small value type that does
it right, once.

`Version(text)` parses a dotted version string in `__init__`:
- Surrounding whitespace and one optional leading "v" or "V" are ignored.
- The rest is split on "."; every component must be non-empty and consist of
  digits only, otherwise raise ValueError. "" and "v" alone are errors too.
- Store `self.parts`, a tuple of ints with trailing zeros removed, but never
  shorter than one element: "1.2.0" -> (1, 2), "0.0.0" -> (0,). This makes
  "1.2" and "1.2.0" identical, and it means tuple comparison is all you need.
- `major`, `minor`, `patch` are properties returning the first three
  components, 0 when absent.

Display and comparison:
- `str(v)` is the canonical dotted form of `parts` ("1.2"); `repr(v)` is
  `Version('1.2')`.
- `__eq__` and `__lt__` compare `parts`; use `functools.total_ordering` for the
  other four operators. Comparing with a non-Version returns NotImplemented
  (so `==` is False and `<` raises TypeError).
- `__hash__` must agree with `__eq__`, so equal versions dedupe in a set.

Examples:
    >>> Version("14.10") > Version("14.5")
    True
    >>> Version("14.5") == Version("v14.5.0")
    True
    >>> sorted(Version(s) for s in ["1.10", "1.9", "1.2.1"])
    [Version('1.2.1'), Version('1.9'), Version('1.10')]
    >>> str(Version(" 2.0.0 ")), Version("2.0.0").parts
    ('2', (2,))
    >>> Version("1..2")
    Traceback (most recent call last):
    ValueError: invalid version: '1..2'
"""
from functools import total_ordering
from typing import Tuple


@total_ordering
class Version:
    def __init__(self, text: str) -> None:
        raise NotImplementedError("write Version.__init__")

    @property
    def major(self) -> int:
        raise NotImplementedError("write Version.major")

    @property
    def minor(self) -> int:
        raise NotImplementedError("write Version.minor")

    @property
    def patch(self) -> int:
        raise NotImplementedError("write Version.patch")

    def __str__(self) -> str:
        raise NotImplementedError("write Version.__str__")

    def __repr__(self) -> str:
        raise NotImplementedError("write Version.__repr__")

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError("write Version.__eq__")

    def __lt__(self, other: "Version") -> bool:
        raise NotImplementedError("write Version.__lt__")

    def __hash__(self) -> int:
        raise NotImplementedError("write Version.__hash__")
