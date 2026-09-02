"""Reference solutions for validate_device_record."""
import re
from datetime import date
from typing import Any, Callable, Dict, List

REQUIRED = ("serial", "hostname", "os", "ram_gb", "last_seen")
KNOWN_OS = ("Linux", "Windows", "macOS")

SERIAL_RE = re.compile(r"^[A-Z0-9]{7,12}$")
HOSTNAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")


# Best practice: one predicate per field that returns True/False and never raises, a
# table of (field, predicate, message) in the required order, and a loop that appends.
# The policy "collect, do not stop" is visible in the shape: no early return anywhere.
def _is_serial(v: Any) -> bool:
    return isinstance(v, str) and SERIAL_RE.match(v) is not None


def _is_hostname(v: Any) -> bool:
    return isinstance(v, str) and HOSTNAME_RE.match(v) is not None


def _is_os(v: Any) -> bool:
    return v in KNOWN_OS


def _is_ram(v: Any) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v > 0


def _is_iso_date(v: Any) -> bool:
    if not isinstance(v, str) or len(v) != 10:      # fromisoformat also accepts '20240501' on 3.11+
        return False
    try:
        date.fromisoformat(v)
    except ValueError:
        return False
    return True


CHECKS: List[Any] = [
    ("serial", _is_serial, "serial: must be 7-12 uppercase letters or digits"),
    ("hostname", _is_hostname, "hostname: must be 1-63 letters, digits or hyphens"),
    ("os", _is_os, "os: must be one of Linux, Windows, macOS"),
    ("ram_gb", _is_ram, "ram_gb: must be a positive integer"),
    ("last_seen", _is_iso_date, "last_seen: must be an ISO date YYYY-MM-DD"),
]


def validate_device_record(record: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    for name in REQUIRED:
        if name not in record:
            errors.append(f"missing field: {name}")
    for name, ok, message in CHECKS:
        if name in record and not ok(record[name]):
            errors.append(f"{message}, got {record[name]!r}")
    for name in sorted(set(record) - set(REQUIRED)):
        errors.append(f"unknown field: {name}")
    return errors


# Clever: the same rules without regex, using only string methods. Longer, but shows
# that "validation" is just booleans and that every rule is a one-liner if you want it.
def validate_device_record_no_regex(record: Dict[str, Any]) -> List[str]:
    def serial_ok(v: Any) -> bool:
        return isinstance(v, str) and 7 <= len(v) <= 12 and all(c.isascii() and (c.isupper() or c.isdigit()) for c in v)

    def hostname_ok(v: Any) -> bool:
        return (
            isinstance(v, str)
            and 1 <= len(v) <= 63
            and all(c.isascii() and (c.isalnum() or c == "-") for c in v)
            and not v.startswith("-")
            and not v.endswith("-")
        )

    rules: List[Any] = [
        ("serial", serial_ok, "serial: must be 7-12 uppercase letters or digits"),
        ("hostname", hostname_ok, "hostname: must be 1-63 letters, digits or hyphens"),
        ("os", _is_os, "os: must be one of Linux, Windows, macOS"),
        ("ram_gb", _is_ram, "ram_gb: must be a positive integer"),
        ("last_seen", _is_iso_date, "last_seen: must be an ISO date YYYY-MM-DD"),
    ]
    errors = [f"missing field: {n}" for n in REQUIRED if n not in record]
    errors += [f"{msg}, got {record[n]!r}" for n, ok, msg in rules if n in record and not ok(record[n])]
    errors += [f"unknown field: {n}" for n in sorted(set(record) - set(REQUIRED))]
    return errors
