# Any number of arguments

--- teach #card-957e1db38fa35a9e
### `*args` collects extra positional arguments
One star before a parameter gathers every positional argument into a tuple. The caller passes values separated by commas, as many as they like, and the function sees one tuple. Walk it with `for`.
```python
>>> def count_args(*args):
...     return len(args)
>>> count_args("--verbose", "--force")
2
>>> count_args()
0
```
The star works the other way at a call site too: `print(*argv)` passes each item of `argv` as its own argument.

--- code #card-db79369a33705de7
Define `count_flags(*args)` that returns how many of its arguments start with `--`. Then print `count_flags("--a", "b", "--c")`.
```python
# your code here
```
expect: 2
check: count_flags() == 0
solution: def count_flags(*args):
solution:     n = 0
solution:     for a in args:
solution:         if a.startswith("--"):
solution:             n += 1
solution:     return n
solution: print(count_flags("--a", "b", "--c"))
> `args` is a tuple of everything passed, so the count pattern from Part 2 walks it. With no arguments the tuple is empty and the count stays 0.

--- predict #card-ef70caf6e8135da0
What does this print?
```python
def first(*args):
    return args[0]

print(first("--dry-run", "--force"))
```
answer: --dry-run
> `args` is the tuple `("--dry-run", "--force")`, and `[0]` is its first item.

--- teach #card-84f41852bfd257fb
### Split on the first `=` only
`partition(sep)` cuts a string at the first `sep` and always gives three pieces: before, the separator, after. When the separator is absent, the result is the whole string, `""`, `""`, which is easy to test. A value containing another `=` stays whole.
```python
>>> "url=http://x?a=b".partition("=")
('url', '=', 'http://x?a=b')
>>> "verbose".partition("=")
('verbose', '', '')
>>> "note=".partition("=")
('note', '=', '')
```
The last one is an empty value, which is different from no value: the middle piece tells them apart.

--- code #card-e6f8098c06215d35
Unpack `arg` with `partition` into `key`, `sep` and `value`, so `key` is `url` and `value` is the whole address.
```python
arg = "url=http://x/?a=b"
```
check: key == "url"
check: value == "http://x/?a=b"
solution: key, sep, value = arg.partition("=")
> `partition("=")` cuts at the first `=` only and returns three pieces; unpacking names them. The `=` inside the address stays in `value`.

--- predict #card-cbbbcdcbc7d353ad
What does this print?
```python
key, sep, value = "expr=a=b".partition("=")
print(value)
```
answer: a=b
> `partition` cuts at the first `=` only. Everything after it, including the second `=`, is the value.

--- teach #card-34c236213a785296
### Strip the prefix, fix the key, fill a dict
Every valid argument starts with `--`; `arg.startswith("--")` checks that, and `arg[2:]` removes the two dashes. `replace("-", "_")` turns `dry-run` into `dry_run`. An empty key after all that is an error. Writing `result[key] = value` into a dict overwrites any earlier value, so "last one wins" is automatic.
```python
result = {}
for arg in args:
    if not arg.startswith("--"):
        raise ValueError(f"bad argument {arg!r}")
    key, sep, value = arg[2:].partition("=")
    key = key.replace("-", "_")
    if not key:
        raise ValueError(f"bad argument {arg!r}")
    if sep:
        result[key] = value
    else:
        result[key] = True
return result
```
`if sep:` is true when an `=` was found, even with an empty value after it.

--- code #card-e36c69c4166c5801
Set `key` to the dict key for `arg`: drop the leading `--`, take the part before `=`, and turn hyphens into underscores.
```python
arg = "--max-retry-count=2"
```
check: key == "max_retry_count"
solution: key, sep, value = arg[2:].partition("=")
solution: key = key.replace("-", "_")
> `arg[2:]` is `max-retry-count=2`; `partition` keeps the part before `=`; `replace` fixes the hyphens.

--- fill #card-ca1dafbbe98b51bf
Complete the line so `--dry-run` becomes the key `dry_run`.
```python
key = key.replace("-", ___)
```
answer: "_"|'_'
> `replace(old, new)` swaps every hyphen for an underscore. The `--` prefix was already sliced off with `[2:]`, so it is not affected.

--- quiz #card-acc12795c78855fe
`parse_flags("--debug=no", "--debug")` should give `{'debug': True}`. Why does the plain `result[key] = ...` assignment do that already?
- [x] Assigning to an existing dict key replaces its value
- [ ] Dicts keep every value in a list
- [ ] `parse_flags` sorts the arguments first
> A dict holds one value per key. Writing to a key that exists overwrites it, so the last assignment in the loop is the one that survives.

--- exercise 3.3 #card-ebb5b77a819a5481

--- recap #card-a969b35ab1e65657
- `*args` gathers positional arguments into a tuple.
- `s.partition("=")` splits at the first separator into (before, sep, after).
- `arg[2:]` drops the `--`; `replace("-", "_")` fixes the key.
- Assigning to a dict key overwrites: last one wins.
