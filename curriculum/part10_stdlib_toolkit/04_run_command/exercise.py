"""A subprocess wrapper with an injectable runner.

Fleet scripts shell out constantly: `profiles`, `launchctl`, `osqueryi`,
`dsregcmd`. Untestable code calls `subprocess.run` directly. Testable code takes
the runner as a parameter with `subprocess.run` as the default; the tests pass a
fake, so nothing real ever executes. That is the whole pattern this exercise
drills.

`run_command(cmd, runner=subprocess.run, timeout=30, check=True)`:

- `cmd` is a list of argv strings, or a single string that you split with
  `shlex.split` so quoted arguments survive as one item. An empty list or a
  blank string raises ValueError before the runner is called.
- call `runner(argv, capture_output=True, text=True, timeout=timeout)` with the
  argv list as the first positional argument. Never pass shell=True.
- the runner returns a CompletedProcess-like object with `.returncode`,
  `.stdout` and `.stderr`; wrap those in a `CommandResult` (argv, returncode,
  stdout, stderr) and return it.
- if the return code is non-zero and `check` is True, raise `CommandError`
  (already defined below): the message names the command and the return code,
  and the exception carries `.returncode` and `.stderr`. With check=False,
  return the result instead.
- if the runner raises `subprocess.TimeoutExpired`, raise CommandError with
  returncode None and a message that says it timed out.

`query_osquery(sql, runner=subprocess.run)` runs `["osqueryi", "--json", sql]`
through run_command and returns `json.loads` of the stdout: a list of row dicts.
Empty or whitespace-only output returns []. A non-zero exit propagates the
CommandError.

Examples:
    >>> def fake(argv, **kw):
    ...     return subprocess.CompletedProcess(argv, 0, stdout="14.5\\n", stderr="")
    >>> run_command("sw_vers -productVersion", runner=fake).stdout
    '14.5\\n'
"""
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


def run_command(
    cmd: Union[str, List[str]],
    runner: Callable = subprocess.run,
    timeout: float = 30,
    check: bool = True,
) -> CommandResult:
    raise NotImplementedError("write run_command")


def query_osquery(sql: str, runner: Callable = subprocess.run) -> List[dict]:
    raise NotImplementedError("write query_osquery")
