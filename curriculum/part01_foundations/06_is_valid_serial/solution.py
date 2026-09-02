"""Reference solutions for is_valid_serial."""
from typing import Optional

ALLOWED = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")


# Best practice: guard clauses, then an explicit character-set check, then the length rules.
# Note: str.isalnum() is *not* enough on its own: it accepts lowercase and non-ASCII letters like 'Ä'.
def is_valid_serial(serial: Optional[str]) -> bool:
    if not serial:
        return False
    if any(ch not in ALLOWED for ch in serial):
        return False
    if len(serial) in (10, 12):
        return True
    if len(serial) == 7:
        return any(ch.isdigit() for ch in serial)
    return False


# Clever: set arithmetic. set(serial) <= ALLOWED is "every character is allowed".
def is_valid_serial_sets(serial: Optional[str]) -> bool:
    if not serial or not set(serial) <= ALLOWED:
        return False
    n = len(serial)
    return n in (10, 12) or (n == 7 and bool(set(serial) & set("0123456789")))
