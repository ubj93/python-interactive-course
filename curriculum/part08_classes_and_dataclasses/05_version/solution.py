"""Reference solutions for Version."""
from dataclasses import dataclass
from functools import total_ordering
from typing import Tuple


def _parse(text: str) -> Tuple[int, ...]:
    """Shared parser: strict about shape, then strip trailing zeros so tuples compare cleanly."""
    body = text.strip()
    if body[:1] in ("v", "V"):
        body = body[1:]
    pieces = body.split(".")
    if not all(p.isdigit() for p in pieces):        # "" is not isdigit, so "", "1..2", "1." all fail
        raise ValueError(f"invalid version: {text!r}")
    parts = [int(p) for p in pieces]
    while len(parts) > 1 and parts[-1] == 0:
        parts.pop()
    return tuple(parts)


# Best practice: parse once in __init__, store a canonical tuple, and let tuple comparison
# do the ordering. __eq__/__lt__ return NotImplemented for foreign types; total_ordering
# fills in the rest; __hash__ uses the same canonical tuple so it agrees with __eq__.
@total_ordering
class Version:
    def __init__(self, text: str) -> None:
        self.parts = _parse(text)

    @property
    def major(self) -> int:
        return self.parts[0]

    @property
    def minor(self) -> int:
        return self.parts[1] if len(self.parts) > 1 else 0

    @property
    def patch(self) -> int:
        return self.parts[2] if len(self.parts) > 2 else 0

    def __str__(self) -> str:
        return ".".join(str(p) for p in self.parts)

    def __repr__(self) -> str:
        return f"Version({str(self)!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self.parts == other.parts

    def __lt__(self, other: "Version") -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self.parts < other.parts

    def __hash__(self) -> int:
        return hash(self.parts)


# Clever: when "compare one tuple" is the whole story, a frozen, ordered dataclass with a
# single field generates __eq__, __lt__ (and friends) and __hash__ for you. The constructor
# then takes the tuple, so parsing moves to a classmethod. Same behaviour, less code.
@dataclass(frozen=True, order=True)
class VersionDC:
    parts: Tuple[int, ...]

    @classmethod
    def parse(cls, text: str) -> "VersionDC":
        return cls(_parse(text))

    def __str__(self) -> str:
        return ".".join(str(p) for p in self.parts)
