# Defaults and keyword arguments

--- teach
### Defaults make arguments optional
A parameter with `= value` in the `def` gets that value when the caller leaves it out. Parameters with defaults must come after those without.
```python
def build_command(package, action="install", verbose=False):
    ...

build_command("zoom")                 # action="install", verbose=False
build_command("zoom", "remove")       # positional, in order
```
The first call gives one argument; the other two fall back to their defaults.

--- teach
### Keyword arguments name what you pass
Write `name=value` in the call to set one parameter and skip the ones before it. Keyword arguments can come in any order, but positional ones must come first.
```python
build_command("zoom", verbose=True)              # skips action
build_command(package="zoom", action="update")   # all by name
```
`build_command(verbose=True, "zoom")` is a syntax error: positional after keyword.

--- predict
What does this print?
```python
def label(host, prefix="mbp", sep="-"):
    return prefix + sep + host

print(label("doe", sep="_"))
```
answer: mbp_doe
> `prefix` keeps its default "mbp"; `sep` is set by keyword to "_". Keywords let you skip a parameter in the middle.

--- teach
### The mutable-default trap
A default is evaluated once, when `def` runs, not once per call. A default `[]` is therefore a single list shared by every call: whatever one caller appends, the next caller sees.
```python
>>> def add_target(host, targets=[]):      # WRONG
...     targets.append(host)
...     return targets
>>> add_target("a")
['a']
>>> add_target("b")
['a', 'b']
```
The fix: default to `None` and create the list inside the function, so each call gets a fresh one.
```python
def add_target(host, targets=None):
    if targets is None:
        targets = []
```

--- code
Write the body of `add_target`: when `targets` is None create a new list, append `host`, and return the list. Then print `add_target("a")` and `add_target("b")` on separate lines.
```python
def add_target(host, targets=None):
```
expect: ['a']\n['b']
check: add_target("x") == ["x"]
solution:     if targets is None:
solution:         targets = []
solution:     targets.append(host)
solution:     return targets
solution: print(add_target("a"))
solution: print(add_target("b"))
> Each call that omits `targets` creates its own fresh list, so the second call prints `['b']`, not `['a', 'b']`. The body lines are indented; the two prints are not.

--- quiz
Why is `def build_command(package, extra_args=[])` wrong?
- [ ] Lists are not allowed as defaults
- [x] The same list object is reused by every call that omits `extra_args`
- [ ] The default is recreated on every call, which is slow
> Defaults are created once, at `def` time. A mutable default like `[]` is shared across calls. Use `None` and create the list inside.

--- teach
### Validate first, then build
Check the inputs at the top and `raise ValueError` for anything unacceptable; the rest of the function can then assume clean input. Build the result as a fresh list and grow it with `append` (one item) and `extend` (all items of another sequence). `str(30)` is `"30"`: every element of an argv list must be text.
```python
if action not in ACTIONS:
    raise ValueError(f"unknown action {action!r}")
argv = ["pkgctl", action, package]
if timeout is not None:
    argv.extend(["--timeout", str(timeout)])
```
Test `timeout is not None`, not `if timeout:`, because `0` is a valid timeout. `!r` in the f-string shows the value with quotes: `unknown action 'purge'`.

--- code
Build `argv` as `pkgctl`, the action, the package, then `--timeout` and its value as a string only when `timeout` is not None.
```python
action = "remove"
package = "zoom"
timeout = 30
```
check: argv == ["pkgctl", "remove", "zoom", "--timeout", "30"]
solution: argv = ["pkgctl", action, package]
solution: if timeout is not None:
solution:     argv.extend(["--timeout", str(timeout)])
> Start from a fresh three-item list, then `extend` with both the flag and `str(timeout)`. Every element stays a string, and the `is not None` test keeps a timeout of 0 working.

--- fill
Complete the line so both `--timeout` and its value are added to `argv`.
```python
argv.___(["--timeout", str(timeout)])
```
answer: extend
> `extend` adds every item of the given list. `append` would add the whole two-item list as a single element.

--- predict
What does this print?
```python
argv = ["pkgctl", "install"]
argv.append(["zoom", "--verbose"])
print(len(argv))
```
answer: 3
> `append` adds one item, here a whole list, so `argv` has three elements. `extend` would have made it four.

--- exercise 3.1

--- recap
- `param=value` in a `def` makes the argument optional; defaults come last.
- `name=value` in a call sets a parameter by name and can skip others.
- Never default to `[]` or `{}`; use `None` and create inside.
- Validate at the top with `ValueError`; `append` one item, `extend` many.
