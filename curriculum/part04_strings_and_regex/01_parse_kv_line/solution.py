"""Reference solutions for parse_kv_line."""
from typing import Dict


# Best practice: split on the field separator, skip blanks, partition each field once.
# partition never raises, so the "missing '='" case is an explicit check on the separator.
def parse_kv_line(line: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for field in line.split(";"):
        field = field.strip()
        if not field:
            continue
        key, sep, value = field.partition("=")
        key = key.strip()
        if not sep or not key:
            raise ValueError(f"malformed field: {field!r}")
        result[key] = value.strip()
    return result


# Clever: split(maxsplit=1) plus tuple unpacking. The unpack itself raises ValueError
# when '=' is missing, which is exactly the error the spec asks for.
def parse_kv_line_unpack(line: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for field in filter(str.strip, line.split(";")):
        key, value = field.split("=", 1)
        if not key.strip():
            raise ValueError(f"empty key in {field!r}")
        result[key.strip()] = value.strip()
    return result
