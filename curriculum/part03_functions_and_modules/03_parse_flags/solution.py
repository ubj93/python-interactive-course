"""Reference solutions for parse_flags."""
from typing import Dict, Union


# Best practice: validate the shape of each argument, then str.partition splits on the
# first "=" only and tells you (via the separator) whether there was one at all. Plain
# dict assignment gives last-one-wins for free.
def parse_flags(*args: str) -> Dict[str, Union[str, bool]]:
    flags: Dict[str, Union[str, bool]] = {}
    for arg in args:
        if not arg.startswith("--"):
            raise ValueError(f"expected an argument starting with --, got {arg!r}")
        key, sep, value = arg[2:].partition("=")
        if not key:
            raise ValueError(f"missing flag name in {arg!r}")
        key = key.replace("-", "_")
        flags[key] = value if sep else True
    return flags


# Clever: split("=", 1) instead of partition. Equivalent, but you have to test the
# length of the result to know whether "=" was present; partition's middle value is
# the more honest signal. Shown because split(sep, 1) is the form most people know.
def parse_flags_split(*args: str) -> Dict[str, Union[str, bool]]:
    flags: Dict[str, Union[str, bool]] = {}
    for arg in args:
        if not arg.startswith("--"):
            raise ValueError(f"expected an argument starting with --, got {arg!r}")
        parts = arg[2:].split("=", 1)
        if not parts[0]:
            raise ValueError(f"missing flag name in {arg!r}")
        key = parts[0].replace("-", "_")
        flags[key] = parts[1] if len(parts) == 2 else True
    return flags
