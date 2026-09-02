"""Reference solutions for build_command."""
from typing import List, Optional, Sequence, Union

ACTIONS = ("install", "remove", "update")


# Best practice: validate first, then build the list in the documented order with one
# `if` per optional piece. A fresh list literal on every call means no shared state, and
# `extra_args=None` (not `[]`) is the idiom that avoids the mutable-default trap.
def build_command(
    package: str,
    action: str = "install",
    verbose: bool = False,
    timeout: Optional[Union[int, float]] = None,
    extra_args: Optional[Sequence[str]] = None,
) -> List[str]:
    if action not in ACTIONS:
        raise ValueError(f"action must be one of {ACTIONS}, got {action!r}")
    if not package:
        raise ValueError("package must be a non-empty string")
    argv = ["pkgctl", action, package]
    if verbose:
        argv.append("--verbose")
    if timeout is not None:
        argv.extend(["--timeout", str(timeout)])
    if extra_args:
        argv.extend(extra_args)
    return argv


# Clever: build the optional parts as (condition, pieces) pairs and keep only the ones
# that apply. Reads like the usage line; easy to extend, harder to step through.
def build_command_table(
    package: str,
    action: str = "install",
    verbose: bool = False,
    timeout: Optional[Union[int, float]] = None,
    extra_args: Optional[Sequence[str]] = None,
) -> List[str]:
    if action not in ACTIONS:
        raise ValueError(f"action must be one of {ACTIONS}, got {action!r}")
    if not package:
        raise ValueError("package must be a non-empty string")
    optional = [
        (verbose, ["--verbose"]),
        (timeout is not None, ["--timeout", str(timeout)]),
        (bool(extra_args), list(extra_args or [])),
    ]
    argv = ["pkgctl", action, package]
    for present, pieces in optional:
        if present:
            argv.extend(pieces)
    return argv
