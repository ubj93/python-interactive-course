# A command line with argparse

--- teach
### A parser turns a list of strings into a Namespace
`argparse.ArgumentParser` describes the interface of a script. `add_argument("serial")` declares a positional argument: required, given without a flag. `parse_args(argv)` reads a list of strings and returns a `Namespace`, an object with one attribute per argument.
```python
import argparse

parser = argparse.ArgumentParser(prog="devreport")
parser.add_argument("serial")
ns = parser.parse_args(["C02XG1234ABC"])
ns.serial            # 'C02XG1234ABC'
```
`prog` is the name shown in usage messages.

--- predict
What does this print?
```python
import argparse
parser = argparse.ArgumentParser(prog="devreport")
parser.add_argument("serial")
print(parser.parse_args(["C02X"]).serial)
```
answer: C02X
> The one positional argument takes the one string in the list, and the Namespace exposes it as `.serial`.

--- teach
### Options with `type`, `choices` and `default`
Arguments starting with `--` are options. `default` fills in when the option is absent. `type=int` converts the text **and** validates it. `choices` restricts the allowed values. When a value is bad, argparse prints usage to stderr and raises `SystemExit`; you do not write the `try/except`.
```python
parser.add_argument("--format", choices=["table", "json", "csv"], default="table")
parser.add_argument("--days", type=int, default=30)

parser.parse_args(["S1", "--days", "7"]).days      # 7, an int
parser.parse_args(["S1", "--days", "soon"])        # usage error, SystemExit
```

--- code
Add a `--days` option that converts to an `int` with default 30, then print `parser.parse_args(["--days", "7"]).days + 1`.
```python
import argparse
parser = argparse.ArgumentParser(prog="devreport")
```
expect: 8
check: parser.parse_args([]).days == 30
solution: parser.add_argument("--days", type=int, default=30)
solution: print(parser.parse_args(["--days", "7"]).days + 1)
> `type=int` makes the value a number, so `+ 1` gives 8; without it `"7" + 1` would raise `TypeError`. With no `--days` at all, the default 30 fills in.

--- quiz
`--days` is declared with `type=int`. What happens on `parse_args(["S1", "--days", "soon"])`?
- [ ] `ns.days` is the string `"soon"`
- [ ] Python raises `ValueError`
- [x] argparse prints usage and raises `SystemExit`
> argparse catches the failed conversion and turns it into a usage error. Tests check for `SystemExit`, so let it through.

--- teach
### Flags and repeatable options
`action="store_true"` makes a flag that is `False` unless present; give it a short and a long name. `action="append"` collects every occurrence into a list, and `dest` names the attribute.
```python
parser.add_argument("-v", "--verbose", action="store_true")
parser.add_argument("--tag", dest="tags", action="append", default=[])

ns = parser.parse_args(["S1", "-v", "--tag", "lab", "--tag", "loaner"])
ns.verbose, ns.tags        # (True, ['lab', 'loaner'])
```

--- predict
What does this print?
```python
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--tag", dest="tags", action="append", default=[])
print(parser.parse_args(["--tag", "lab", "--tag", "x"]).tags)
```
answer: ['lab', 'x']
> Each `--tag` appends one value, in order, to the list stored under `tags`.

--- teach
### Options that cannot be combined
A mutually exclusive group holds options of which at most one may be given. Passing two of them is a usage error, handled by argparse.
```python
state = parser.add_mutually_exclusive_group()
state.add_argument("--online", action="store_true")
state.add_argument("--offline", action="store_true")
```
Both attributes still exist on the Namespace; the one not given is `False`.

--- fill
Complete the line so `--online` and `--offline` cannot be used together.
```python
state = parser.___()
state.add_argument("--online", action="store_true")
state.add_argument("--offline", action="store_true")
```
answer: add_mutually_exclusive_group
> Arguments added to the group, rather than to the parser, are checked against each other.

--- teach
### Build the parser in a function, pass argv in
Put the parser inside `build_parser()` and call it fresh for every parse. Two reasons: tests can inspect the parser, and the `default=[]` of an `append` option is not shared between parses, so tags cannot leak from one call to the next. Only the `if __name__ == "__main__":` block calls `parse_args()` with no argument, which reads `sys.argv`.
```python
def build_parser():
    parser = argparse.ArgumentParser(prog="devreport")
    ...
    return parser

def parse_args(argv):
    return build_parser().parse_args(argv)
```

--- quiz
Why does `parse_args(argv)` build a new parser on every call?
- [ ] Parsers can only be used once
- [x] So each parse starts from fresh defaults; the `tags` list is not shared between calls
- [ ] It makes parsing faster
> A single parser object keeps its `default=[]` list, and `append` writes into it. A fresh parser per call keeps tests independent.

--- exercise 10.2

--- recap
- `ArgumentParser` plus `add_argument` describe the interface; `parse_args(list)` returns a Namespace.
- `type=int` converts and validates; `choices` restricts; `default` fills in.
- `action="store_true"` for flags, `action="append"` with `dest` for repeatable options.
- `add_mutually_exclusive_group()` for options that cannot be combined.
- Build the parser in a function and pass `argv` explicitly; usage errors raise `SystemExit`.
