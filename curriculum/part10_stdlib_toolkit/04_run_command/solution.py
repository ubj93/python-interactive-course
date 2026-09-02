"""Reference solutions for run_command / query_osquery."""
import json
import shlex
import subprocess
from dataclasses import dataclass
from typing import Callable, List, Optional, Union


@dataclass
class CommandResult:
    argv: List[str]
    returncode: int
    stdout: str
    stderr: str


class CommandError(Exception):
    def __init__(self, message: str, returncode: Optional[int] = None, stderr: str = ""):
        super().__init__(message)
        self.returncode = returncode
        self.stderr = stderr


# Best practice: normalise the command to a list first (shlex for strings, never shell=True),
# validate before touching the runner, and translate the two failure modes (non-zero exit,
# timeout) into one exception type the caller can catch.
def run_command(
    cmd: Union[str, List[str]],
    runner: Callable = subprocess.run,
    timeout: float = 30,
    check: bool = True,
) -> CommandResult:
    argv = shlex.split(cmd) if isinstance(cmd, str) else list(cmd)
    if not argv:
        raise ValueError("empty command")
    try:
        proc = runner(argv, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise CommandError(f"{shlex.join(argv)} timed out after {timeout}s") from exc
    result = CommandResult(argv, proc.returncode, proc.stdout or "", proc.stderr or "")
    if check and result.returncode != 0:
        raise CommandError(
            f"{shlex.join(argv)} exited with {result.returncode}: {result.stderr.strip()}",
            returncode=result.returncode,
            stderr=result.stderr,
        )
    return result


# The parse step is one line because run_command already did the error handling.
def query_osquery(sql: str, runner: Callable = subprocess.run) -> List[dict]:
    out = run_command(["osqueryi", "--json", sql], runner=runner).stdout
    return json.loads(out) if out.strip() else []


# Clever: let subprocess.run(check=True) raise CalledProcessError and translate it. Fewer
# branches, and it works for any runner that honours check=; the fake in the tests does not,
# so this version is here to show the idiom, not to pass them.
def run_command_check(cmd: Union[str, List[str]], runner: Callable = subprocess.run, timeout: float = 30) -> CommandResult:
    argv = shlex.split(cmd) if isinstance(cmd, str) else list(cmd)
    if not argv:
        raise ValueError("empty command")
    try:
        proc = runner(argv, capture_output=True, text=True, timeout=timeout, check=True)
    except subprocess.CalledProcessError as exc:
        raise CommandError(f"{shlex.join(argv)} exited with {exc.returncode}", exc.returncode, exc.stderr or "") from exc
    except subprocess.TimeoutExpired as exc:
        raise CommandError(f"{shlex.join(argv)} timed out after {timeout}s") from exc
    return CommandResult(argv, proc.returncode, proc.stdout or "", proc.stderr or "")
