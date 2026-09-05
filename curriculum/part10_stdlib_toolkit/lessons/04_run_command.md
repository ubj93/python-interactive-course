# Shelling out, testably

--- teach #bash-process-worked
### Bash bridge: exit status and exceptions are different signals
Bash exposes a command's exit status through `$?`. With Python's `subprocess.run(check=False)`, a nonzero status is a result value, not an exception. `check=True` converts it to `CalledProcessError`. Launch failures and timeouts can raise exceptions independently.
```python
from subprocess import CompletedProcess

def fake_runner(argv, **options):
    return CompletedProcess(argv, 3, stdout="", stderr="busy")

result = fake_runner(["fake-check"])
print(result.returncode)  # 3; no exception was raised
```
Only the injected fake is called here; no process starts. This bridge needs functions, `try`/`except` and `raise` (lessons 3.1 and 7.1–7.2). Choose whether your wrapper returns a status or raises a documented error, then make callers use that contract.

--- code #bash-process-modify
Repair `read_status(runner)`: call the injected runner with `["fake-status"]`, return stripped stdout when its status is zero, and raise `RuntimeError` otherwise. The supplied runner is always a fake; do not import or call a real process runner.

Browser: edit the function. Terminal: type the complete corrected function below the starter.
```python
from subprocess import CompletedProcess

def read_status(runner):
    result = runner(["fake-status"])
    return result.stdout.strip()

seen = []

def fake_ready(argv):
    seen.append(argv)
    return CompletedProcess(argv, 0, stdout=" ready\n", stderr="")

def fake_busy(argv):
    return CompletedProcess(argv, 4, stdout="partial", stderr="busy")

def raises_runtime(function, runner):
    try:
        function(runner)
    except RuntimeError:
        return True
    return False
```
check: read_status(fake_ready) == "ready" and seen == [["fake-status"]]
check: raises_runtime(read_status, fake_busy)
check: read_status(lambda argv: CompletedProcess(argv, 0, stdout="idle\n")) == "idle"
solution: def read_status(runner):
solution:     result = runner(["fake-status"])
solution:     if result.returncode != 0:
solution:         raise RuntimeError("status command failed")
solution:     return result.stdout.strip()
> The fake's nonzero return code did not raise by itself; your wrapper deliberately translates it into a Python exception. No command was executed.

--- code #bash-process-check
Independent check: write `probe_ok(runner)`. Call the injected runner with `["fake-probe"]` and return `True` only for status zero. Return `False` for another status or an `OSError` from the fake runner. Do not catch unrelated programming errors or start a process.

Browser: edit the function. Terminal: type the complete corrected function below the starter.
```python
from subprocess import CompletedProcess

def probe_ok(runner):
    pass

def fake_ok(argv):
    assert argv == ["fake-probe"]
    return CompletedProcess(argv, 0)

def fake_missing(argv):
    raise OSError("fake tool unavailable")

def fake_bug(argv):
    raise ValueError("fake programmer mistake")

def leaves_bug_visible(function):
    try:
        function(fake_bug)
    except ValueError:
        return True
    return False
```
check: probe_ok(fake_ok) is True
check: probe_ok(lambda argv: CompletedProcess(argv, 9)) is False
check: probe_ok(fake_missing) is False
check: leaves_bug_visible(probe_ok)
solution: def probe_ok(runner):
solution:     try:
solution:         result = runner(["fake-probe"])
solution:     except OSError:
solution:         return False
solution:     return result.returncode == 0
> A nonzero result and a raised `OSError` take different paths to the same documented `False`. Catching only `OSError` keeps a programming `ValueError` visible. The bridge is complete; continue this lesson or return to the diagnostic.

--- teach #card-2572d58f08c15ed6
### `subprocess.run` with a list of arguments
`subprocess.run(argv, ...)` starts a program and waits for it. Pass the command as a **list**: the program, then each argument. `capture_output=True` collects stdout and stderr instead of showing them; `text=True` gives you `str` instead of bytes; `timeout` stops a hung command. The result has `.returncode`, `.stdout` and `.stderr`.
```python
import subprocess
proc = subprocess.run(["sw_vers", "-productVersion"], capture_output=True, text=True, timeout=30)
proc.returncode, proc.stdout        # (0, '14.5\n')
```
A return code of 0 means success; anything else is an error the program reported.

--- quiz #card-2b0d3ea855fc5ac8
Which call gives you the program's output as a string in `proc.stdout`?
- [ ] `subprocess.run(["sw_vers"])`
- [x] `subprocess.run(["sw_vers"], capture_output=True, text=True)`
- [ ] `subprocess.run("sw_vers", shell=True)`
> Without `capture_output` the output goes to the terminal and `.stdout` is `None`; without `text` it is bytes. `shell=True` is the option to avoid.

--- teach #card-8e0a68defd4a551d
### From a string to argv with `shlex`
Sometimes you are handed a command as one string. `shlex.split` cuts it into a list the way a shell would, keeping quoted parts together. That is how you avoid `shell=True`, which runs through `/bin/sh` and lets crafted input inject extra commands. `shlex.join` goes the other way, for error messages.
```python
>>> import shlex
>>> shlex.split('osqueryi --json "select * from users"')
['osqueryi', '--json', 'select * from users']
>>> shlex.join(["echo", "hi there"])
"echo 'hi there'"
```

--- predict #card-d31616d775615a52
What does this print?
```python
import shlex
print(shlex.split('osqueryi --json "select * from users"'))
```
answer: ['osqueryi', '--json', 'select * from users']
> The quoted SQL stays one item. Plain `str.split()` would cut it into four pieces.

--- teach #card-10cbf3d7178759fe
### Inject the runner
Real processes are slow, platform-specific and have side effects, so a test must never start one. The fix is the same as `now` in lesson 10.1: the function takes the thing that does the work as a parameter, with the real one as the default.
```python
def run_command(cmd, runner=subprocess.run, timeout=30):
    argv = shlex.split(cmd) if isinstance(cmd, str) else list(cmd)
    proc = runner(argv, capture_output=True, text=True, timeout=timeout)
    ...
```
A test passes a fake that records what it was asked to run and returns a canned `subprocess.CompletedProcess`. Nothing executes, and the test can assert the exact argv.

--- code #card-3731dde76b115781
Write `run_version(runner=subprocess.run)` that calls `runner(["sw_vers", "-productVersion"], capture_output=True, text=True)` and returns the stripped stdout. Then print `run_version(runner=fake)`.
```python
import subprocess
def fake(argv, **kw):
    return subprocess.CompletedProcess(argv, 0, stdout="14.5\n", stderr="")
```
expect: 14.5
solution: def run_version(runner=subprocess.run):
solution:     proc = runner(["sw_vers", "-productVersion"], capture_output=True, text=True)
solution:     return proc.stdout.strip()
solution: print(run_version(runner=fake))
> The default is the real `subprocess.run`, but this call passes `fake`, so nothing executes and the canned `"14.5\n"` comes back to be stripped.

--- predict #card-5b8f9739735c54b8
What does this print?
```python
import subprocess
def fake(argv, **kw):
    return subprocess.CompletedProcess(argv, 0, stdout="14.5\n", stderr="")
proc = fake(["sw_vers"], capture_output=True, text=True)
print(proc.returncode, proc.stdout.strip())
```
answer: 0 14.5
> The fake never runs `sw_vers`; it just builds the same kind of object `subprocess.run` would return.

--- teach #card-762669639a705d37
### Translate failures into one exception
Two things go wrong: the program exits non-zero, or it hangs and the runner raises `subprocess.TimeoutExpired`. Turn both into your own `CommandError` so callers catch one type. Do the cheap check (empty command) before calling the runner at all.
```python
if not argv:
    raise ValueError("empty command")
try:
    proc = runner(argv, capture_output=True, text=True, timeout=timeout)
except subprocess.TimeoutExpired as exc:
    raise CommandError(f"{shlex.join(argv)} timed out") from exc
if check and proc.returncode != 0:
    raise CommandError(f"{shlex.join(argv)} exited with {proc.returncode}", proc.returncode, proc.stderr)
```
With `check=False` a failure is returned as a result instead.

--- fill #card-bdc86d0587705a2b
Complete the `except` so a hung command becomes a `CommandError`.
```python
try:
    proc = runner(argv, capture_output=True, text=True, timeout=timeout)
except subprocess.___ as exc:
    raise CommandError(f"{shlex.join(argv)} timed out") from exc
```
answer: TimeoutExpired
> `subprocess.run` raises `TimeoutExpired` when the timeout passes. `from exc` keeps the original cause in the traceback.

--- teach #card-6748b6b9e9bd51da
### Parse the output, guard the empty case
`query_osquery` is small because `run_command` already handled errors: build the argv, run it, `json.loads` the stdout. `json.loads("")` raises, so treat empty or whitespace-only output as no rows.
```python
def query_osquery(sql, runner=subprocess.run):
    out = run_command(["osqueryi", "--json", sql], runner=runner).stdout
    return json.loads(out) if out.strip() else []
```

--- quiz #card-37ea01dee0fa565b
The fake runner returns stdout `"  \n"`. What should `query_osquery` return?
- [ ] Raise `CommandError`
- [x] `[]`
- [ ] `None`
> Blank output means no rows. `json.loads` on it would raise, so the `out.strip()` guard returns an empty list.

--- exercise 10.4 #card-80b6980121f05d46

--- recap #card-52ebfbd48f985216
- `subprocess.run(argv_list, capture_output=True, text=True, timeout=...)`; never `shell=True`.
- `shlex.split` turns a command string into argv; `shlex.join` for messages.
- Take `runner=subprocess.run` as a parameter; tests pass a fake that returns `CompletedProcess`.
- Translate non-zero exits and `TimeoutExpired` into one `CommandError`.
