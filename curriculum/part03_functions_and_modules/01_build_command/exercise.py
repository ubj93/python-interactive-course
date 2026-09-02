"""Build a package-manager command line.

Our deployment scripts shell out to an internal tool, `pkgctl`. Instead of
gluing strings together, we build the argv list and hand it to subprocess.
Write `build_command(package, action="install", verbose=False, timeout=None,
extra_args=None)` that returns the argv as a list of strings, in this order:

    pkgctl <action> <package> [--verbose] [--timeout <seconds>] [extra args...]

Rules:
- `action` must be one of "install", "remove", "update"; anything else raises
  ValueError
- `package` must be a non-empty string; an empty string raises ValueError
- `--verbose` is present only when verbose is True
- `--timeout` and its value are present only when timeout is not None; the
  value is formatted with str(), so 30 becomes "30" and 2.5 becomes "2.5"
- `extra_args`, when given, is a sequence of strings appended at the end in
  order; None means nothing extra
- every element of the result is a str
- return a NEW list on every call; callers may modify it (this is the
  mutable-default trap: do not use extra_args=[])

Examples:
    >>> build_command("zoom")
    ['pkgctl', 'install', 'zoom']
    >>> build_command("zoom", action="remove", verbose=True)
    ['pkgctl', 'remove', 'zoom', '--verbose']
    >>> build_command("zoom", timeout=30, extra_args=["--force"])
    ['pkgctl', 'install', 'zoom', '--timeout', '30', '--force']
"""
from typing import List, Optional, Sequence, Union

ACTIONS = ("install", "remove", "update")


def build_command(
    package: str,
    action: str = "install",
    verbose: bool = False,
    timeout: Optional[Union[int, float]] = None,
    extra_args: Optional[Sequence[str]] = None,
) -> List[str]:
    raise NotImplementedError("write build_command")
