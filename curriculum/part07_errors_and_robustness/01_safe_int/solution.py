"""Reference solutions for safe_int."""
from typing import Any, Optional


# Best practice: EAFP. int() already knows every rule about whitespace, signs and
# floats; we only decide what to do when it refuses, and we name the two exceptions
# it raises so anything else still surfaces.
def safe_int(value: Any, default: Optional[int] = 0) -> Optional[int]:
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


# Clever (and worse): LBYL with string checks. It must special-case floats, signs and
# whitespace by hand, and still misses cases int() handles. Shown for contrast.
def safe_int_lbyl(value: Any, default: Optional[int] = 0) -> Optional[int]:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        s = value.strip()
        if s.startswith(("-", "+")):
            s = s[1:]
        if s.isdigit():
            return int(value)
    return default
