"""Reference solutions for parse_version_string."""
import re
from typing import Optional, Tuple

VERSION = re.compile(
    r"[vV]?(?P<major>\d+)(?:\.(?P<minor>\d+))?(?:\.(?P<patch>\d+))?"
    r"(?:\s+\((?P<build>[A-Za-z0-9]+)\))?"
)


# Best practice: fullmatch on a named-group pattern; optional groups come back as None,
# and `or "0"` turns that into the default. Strip first so the pattern does not need \s*.
def parse_version_string(s: str) -> Tuple[Tuple[int, int, int], Optional[str]]:
    m = VERSION.fullmatch(s.strip())
    if not m:
        raise ValueError(f"not a version string: {s!r}")
    version = tuple(int(m.group(name) or "0") for name in ("major", "minor", "patch"))
    return version, m.group("build")  # type: ignore[return-value]


# Clever: no regex at all. partition off the build, split the rest on '.', pad to three.
# More lines, but every step is a string method you already know; the validation is manual.
def parse_version_string_split(s: str) -> Tuple[Tuple[int, int, int], Optional[str]]:
    s = s.strip()
    version_text, _, rest = s.partition(" ")
    rest = rest.strip()
    build: Optional[str] = None
    if rest:
        if not (rest.startswith("(") and rest.endswith(")")) or not rest[1:-1].isalnum():
            raise ValueError(f"bad build: {s!r}")
        build = rest[1:-1]
    if version_text[:1] in ("v", "V"):
        version_text = version_text[1:]
    parts = version_text.split(".")
    if not 1 <= len(parts) <= 3 or not all(p.isdigit() for p in parts):
        raise ValueError(f"bad version: {s!r}")
    nums = [int(p) for p in parts] + [0] * (3 - len(parts))
    return (nums[0], nums[1], nums[2]), build
