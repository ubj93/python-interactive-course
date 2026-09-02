"""Parse an OS version string.

macOS reports its version as "14.5.1 (23F79)": a dotted version followed by an
optional build identifier in parentheses. Other sources drop the patch number,
the build, or add a leading "v". Write `parse_version_string(s)` that returns a
2-tuple `((major, minor, patch), build)`:

- major, minor and patch are ints; a missing minor or patch defaults to 0
- build is the string inside the parentheses, or None when there is none
- surrounding whitespace and a leading "v" or "V" are tolerated
- one or more spaces may separate the version from the build

Anything else raises ValueError: an empty string, non-numeric parts, four or more
dotted parts, empty parts ("14..5"), text after the build, or a version
without digits. Use re.fullmatch so that the whole string has to fit the shape.

Because the version part is a tuple of ints it sorts correctly:
parse_version_string("14.10")[0] > parse_version_string("14.9")[0].

Examples:
    >>> parse_version_string("14.5.1 (23F79)")
    ((14, 5, 1), '23F79')
    >>> parse_version_string("14.5")
    ((14, 5, 0), None)
    >>> parse_version_string("  v13 (22A380) ")
    ((13, 0, 0), '22A380')
"""
import re
from typing import Optional, Tuple


def parse_version_string(s: str) -> Tuple[Tuple[int, int, int], Optional[str]]:
    raise NotImplementedError("write parse_version_string")
