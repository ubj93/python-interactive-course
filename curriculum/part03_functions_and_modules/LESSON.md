# Part 3 · Functions and modules

> **What you will be able to do:** design a function's signature on purpose (which
> arguments, which defaults, what comes back), pass functions around as values, keep
> private state in a closure, and lay out a script as a module that can be both
> imported and run. About ninety minutes with the exercises.

## Why this part matters

Every tool you write for a fleet starts as a script and ends up imported by another
script. The difference between a script that survives that transition and one that
has to be rewritten is almost entirely about functions: clear inputs, clear outputs,
no hidden global state. Interviewers test this by asking you to "make it reusable",
"add an option without breaking callers", or "let me swap out the thing that does the
network call." All three are signature-design questions.

## 1. Anatomy of a function

```python
def days_since_checkin(last_seen: str, today: str) -> int:
    """Return whole days between two ISO dates (today - last_seen)."""
    from datetime import date
    return (date.fromisoformat(today) - date.fromisoformat(last_seen)).days
```

- `def` binds a name to a function object. The name is a variable like any other.
- The docstring (first statement, a string) is what `help()` shows and what a reader
  looks at before the body. One line saying what comes back is enough for small
  functions; add `Args:`/`Returns:` sections when the behaviour has corners.
- `return` hands a value back and ends the call. No `return` means `None`.
- Type hints are documentation. Python does not check them, but reviewers and editors
  do, and they force you to decide what the function accepts.

### Returning more than one thing

Return a tuple; the caller unpacks it.

```python
>>> def parse_version(s: str):
...     major, _, rest = s.partition(".")
...     return int(major), rest
>>> major, rest = parse_version("14.5.1")
>>> major, rest
(14, '5.1')
```

Two or three related values as a tuple is fine. Beyond that, return a dict, a
`namedtuple`, or a dataclass (Part 8), so the caller uses names instead of positions.

## 2. Parameters: positional, keyword, default

```python
def build_command(package: str, action: str = "install", verbose: bool = False):
    ...

build_command("zoom")                          # positional; defaults fill the rest
build_command("zoom", "remove")                # positional in order
build_command("zoom", verbose=True)            # keyword; skips `action`
build_command(package="zoom", action="update") # all keyword, any order
```

Rules that matter:

- Positional arguments must come before keyword arguments in a call.
- Parameters with defaults must come after those without in the definition.
- A default is evaluated **once**, when `def` runs, not on every call.

That last rule is the mutable-default trap, the single most-asked Python gotcha:

```python
>>> def add_target(host, targets=[]):      # WRONG
...     targets.append(host)
...     return targets
>>> add_target("a")
['a']
>>> add_target("b")
['a', 'b']          # the same list, shared across calls
```

Use `None` as the default and create the list inside:

```python
def add_target(host, targets=None):
    if targets is None:
        targets = []
    targets.append(host)
    return targets
```

### Keyword-only and positional-only

A bare `*` in the parameter list means "everything after this must be passed by
keyword." Use it for boolean flags and options, so calls read
`run(cmd, check=True)` instead of `run(cmd, True)`.

```python
def run(cmd: list, *, check: bool = False, timeout: float = 30.0): ...
```

A `/` marks parameters before it as positional-only (Python 3.8+). You will see it in
built-ins (`len(obj, /)`); you will rarely write it.

## 3. Collecting arguments: `*args` and `**kwargs`

```python
>>> def log(level, *parts):
...     print(level, "-", " ".join(str(p) for p in parts))
>>> log("INFO", "checked in", "mbp-j-doe", 3)
INFO - checked in mbp-j-doe 3
```

`*parts` collects extra positional arguments into a **tuple**. `**options` collects
extra keyword arguments into a **dict**:

```python
>>> def retry_policy(**overrides):
...     policy = {"max_attempts": 3, "base_delay": 1.0}
...     policy.update(overrides)
...     return policy
>>> retry_policy(max_attempts=5)
{'max_attempts': 5, 'base_delay': 1.0}
```

The names `args` and `kwargs` are convention, not syntax; pick descriptive ones when
it helps. The same stars unpack in the other direction at the call site:

```python
>>> argv = ["pkgctl", "install", "zoom"]
>>> print(*argv)                  # print("pkgctl", "install", "zoom")
>>> opts = {"check": True, "timeout": 5}
>>> run(argv, **opts)             # run(argv, check=True, timeout=5)
```

**When to use `**kwargs`:** forwarding options you do not interpret to another
function, or accepting a genuinely open set of keys. **When not to:** when the keys
are known. `def retry_policy(*, max_attempts=3, base_delay=1.0)` is better than
`**overrides` there because Python then rejects typos (`max_attemps=5`) for free and
editors can autocomplete the names. Interviewers ask "what happens if I pass a key
you don't know?" and the honest answer with `**kwargs` is "nothing, unless I check."

## 4. Scope: where a name is looked up

Python resolves a name by looking in four places, in order: **L**ocal (the current
function), **E**nclosing (any function this one is defined inside), **G**lobal (the
module), **B**uilt-in (`len`, `print`). LEGB.

```python
>>> threshold = 0.8                  # global
>>> def is_hot(load):
...     return load > threshold      # reads the global: fine
```

Reading an outer name works. **Assigning** to a name inside a function makes it
local for the whole function, which produces the famous error:

```python
>>> count = 0
>>> def bump():
...     count += 1                   # UnboundLocalError: count is local here, and unset
```

`global count` fixes that, and is almost always the wrong fix: global mutable state
makes functions untestable. Return the new value instead, or use a class or a
closure (next section). The exception is module-level constants that are never
reassigned (`UNITS`, `DEFAULTS`), which are fine and idiomatic in ALL_CAPS.

### Mutating is not rebinding

```python
>>> seen = set()
>>> def note(host):
...     seen.add(host)     # mutates the set the global name points at: allowed
>>> def reset():
...     seen = set()       # creates a NEW local `seen`; the global is untouched
```

The first works without any keyword because no name is assigned. The second is a
bug people write when they think they are clearing the global. Say "rebinding
versus mutating" in an interview and you have shown you understand the model.

## 5. Closures and `nonlocal`

A function defined inside another function can see the outer function's variables,
and keeps seeing them after the outer function has returned. That is a closure, and
it is how you make a function with private state.

```python
>>> def make_counter(start=0):
...     current = start
...     def next_value():
...         nonlocal current
...         value = current
...         current += 1
...         return value
...     return next_value
>>> ticket_id = make_counter(100)
>>> ticket_id(), ticket_id(), ticket_id()
(100, 101, 102)
>>> other = make_counter()
>>> other()                      # 0: separate state for each counter
0
```

`nonlocal current` says "the `current` I assign to is the one in the enclosing
function," the same way `global` points at the module. Without it, `current += 1`
would create a local and raise `UnboundLocalError`. If the state is a mutable object
(a list or dict) and you only mutate it, you do not need `nonlocal` at all.

Closures are what decorators (Part 7) are made of. The pattern to remember: an outer
function that takes configuration, defines an inner function that uses it, and
returns the inner function.

### The late-binding trap

```python
>>> checks = [lambda: i for i in range(3)]
>>> [c() for c in checks]
[2, 2, 2]                          # all three see the final value of i
```

A closure captures the *variable*, not the value at the time. Bind the value with a
default argument (`lambda i=i: i`) or a factory function when you need each one frozen.

## 6. Functions are values

You can store a function in a variable, put it in a list or dict, pass it to another
function, and return it from one. Nothing special is needed; just do not add the
parentheses until you want to call it.

```python
>>> steps = [str.strip, str.lower]
>>> value = "  MBP-J-DOE "
>>> for step in steps:
...     value = step(value)
>>> value
'mbp-j-doe'
```

This is how you make behaviour pluggable. A dispatch table replaces an `if/elif`
ladder that grows every sprint:

```python
HANDLERS = {"install": do_install, "remove": do_remove, "update": do_update}
handler = HANDLERS.get(action)
if handler is None:
    raise ValueError(f"unknown action {action!r}")
handler(package)
```

And it is how you inject the risky part for testing: a function that "runs a
command" takes a `runner` argument that defaults to the real thing, and the test
passes a fake. Every network and subprocess exercise in Parts 10 and 11 works that way.

### Higher-order functions and `lambda`

A function that takes or returns a function is a higher-order function. `sorted`
with `key`, `map`, `filter`, and your own `compose` are examples.

```python
>>> compose = lambda f, g: (lambda x: f(g(x)))
>>> clean = compose(str.lower, str.strip)
>>> clean("  MBP-J-DOE ")
'mbp-j-doe'
```

`lambda` makes a one-expression anonymous function. Use it for tiny keys and
adapters; anything with a name worth saying or more than one line gets a `def`.
`callable(x)` tells you whether `x` can be called; validate with it when the
function accepts callbacks, so a misplaced string fails at definition time rather
than mid-pipeline.

## 7. Docstrings and type hints

```python
from typing import Callable, Dict, List, Optional, Union

def apply_pipeline(value: str, steps: List[Callable[[str], Optional[str]]]) -> Optional[str]:
    """Apply each step in order; stop and return None if any step returns None."""
```

| Hint | Means |
|---|---|
| `List[str]` | a list of strings (3.9: `list[str]` also works) |
| `Dict[str, int]` | keys are strings, values ints |
| `Tuple[int, str]` | exactly two items, an int and a str |
| `Optional[str]` | `str` or `None` |
| `Union[str, bool]` | either type (`str \| bool` needs 3.10, avoid) |
| `Callable[[int], str]` | a function taking one int and returning a str |
| `Any` | anything; a hint that you did not decide |

Hints on the public functions, a one-line docstring saying what comes back, and the
edge cases in the docstring's second paragraph: that is the standard a reviewer at a
well-run shop expects. The exercises in this course model it.

## 8. Modules and imports

A module is a `.py` file. Importing it runs it once, top to bottom, and binds the
names it defines.

```python
import json                      # json.dumps(...)
from pathlib import Path         # Path("x")
import subprocess as sp          # sp.run(...)
from typing import List, Optional
```

- `from x import *` pulls unknown names into your namespace; never in real code.
- Imports go at the top of the file: standard library, then third-party, then your
  own modules, each group alphabetical. Tools enforce this; interviewers notice it.
- Importing your own module twice does not run it twice; Python caches it in
  `sys.modules`.
- A folder with an `__init__.py` is a package; `from course.catalog import Part`
  walks the folder tree. The tests in this course do `from exercise import ...`,
  which works because the harness runs with the exercise folder as the current
  directory, and the current directory is on `sys.path`.

### The `__main__` guard

```python
def main(argv: List[str]) -> int:
    ...
    return 0

if __name__ == "__main__":
    import sys
    raise SystemExit(main(sys.argv[1:]))
```

When Python runs a file directly, `__name__` is `"__main__"`. When another file
imports it, `__name__` is the module name. The guard means the script's side effects
(parsing arguments, printing, exiting) only happen when it is *run*, so a test or
another tool can import `main` and call it with a fake `argv`. Every script you hand
to a reviewer should have this shape: functions at the top, one `main`, the guard at
the bottom, no code at module level except constants.

## Gotchas interviewers probe

- **Mutable defaults** (`def f(xs=[])`). Use `None` and create inside.
- **`**kwargs` swallows typos.** Prefer explicit keyword-only parameters when the
  option names are known.
- **Assignment makes a name local.** `UnboundLocalError` on `count += 1` inside a
  function; fix with `nonlocal` (closure) or by returning a value, not `global`.
- **Forgetting to return.** A function that only prints returns `None`; the caller
  gets nothing to test.
- **Calling versus referencing.** `steps = [str.strip()]` calls with no argument and
  crashes; `[str.strip]` stores the function.
- **Late binding in loops.** Lambdas in a loop all see the loop variable's final value.
- **`None` versus falsy.** A pipeline that stops "when a step returns a falsy value"
  stops on `0` and `""`; say `is None` when you mean `None`.

## Interview notes for this part

- **Design the signature first, out loud.** "It takes the package name positionally,
  the action with a default of install, and the flags keyword-only so calls read
  clearly." Then write the body. Interviewers score the signature.
- **Ask what the caller can pass.** Can `n` be negative? Can `steps` be empty? Is
  `None` a legal input or a bug? Decide, document in the docstring, and enforce with
  a `ValueError`/`TypeError` at the top.
- **Prefer injecting a function over monkey-patching.** "The command runner is a
  parameter, so the test can pass a fake." That sentence lands well in every CPE loop
  because it is exactly how they test their own tooling.
- **The trap:** reaching for `global` when the interviewer says "remember something
  between calls." Offer a closure, a class, or an explicit state argument; explain that
  global state makes the function untestable and unsafe to reuse.

## Exercises

Run `course list 3`, then `course show 3.1`. Edit, run `course run 3.1`, repeat.

1. `build_command` · defaults and keyword arguments; a list of argv strings
2. `retry_policy` · `**kwargs` with validation and defaults
3. `parse_flags` · `*args` of `--key=value` / `--flag` into a dict
4. `compose` · a higher-order function; `compose(f, g)(x) == f(g(x))`
5. `apply_pipeline` · a list of callables applied in order, early stop on `None`
6. `make_counter` · closures with private state and `nonlocal`
