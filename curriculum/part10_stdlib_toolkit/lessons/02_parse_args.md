# A command line with argparse

--- teach #card-c6e9cf242d0e5625
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

--- predict #card-89746b3b80605ef7
What does this print?
```python
import argparse
parser = argparse.ArgumentParser(prog="devreport")
parser.add_argument("serial")
print(parser.parse_args(["C02X"]).serial)
```
answer: C02X
> The one positional argument takes the one string in the list, and the Namespace exposes it as `.serial`.

--- teach #card-2d82cdc422d85cd4
### Options with `type`, `choices` and `default`
Arguments starting with `--` are options. `default` fills in when the option is absent. `type=int` converts the text **and** validates it. `choices` restricts the allowed values. When a value is bad, argparse prints usage to stderr and raises `SystemExit`; you do not write the `try/except`.
```python
parser.add_argument("--format", choices=["table", "json", "csv"], default="table")
parser.add_argument("--days", type=int, default=30)

parser.parse_args(["S1", "--days", "7"]).days      # 7, an int
parser.parse_args(["S1", "--days", "soon"])        # usage error, SystemExit
```

--- code #card-92c8fe6ecff75bf1
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

--- quiz #card-855f41e834975dc1
`--days` is declared with `type=int`. What happens on `parse_args(["S1", "--days", "soon"])`?
- [ ] `ns.days` is the string `"soon"`
- [ ] Python raises `ValueError`
- [x] argparse prints usage and raises `SystemExit`
> argparse catches the failed conversion and turns it into a usage error. Tests check for `SystemExit`, so let it through.

--- teach #card-c6903f25b19150ec
### Flags and repeatable options
`action="store_true"` makes a flag that is `False` unless present; give it a short and a long name. `action="append"` collects every occurrence into a list, and `dest` names the attribute.
```python
parser.add_argument("-v", "--verbose", action="store_true")
parser.add_argument("--tag", dest="tags", action="append", default=[])

ns = parser.parse_args(["S1", "-v", "--tag", "lab", "--tag", "loaner"])
ns.verbose, ns.tags        # (True, ['lab', 'loaner'])
```

--- predict #card-98894a720695508a
What does this print?
```python
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--tag", dest="tags", action="append", default=[])
print(parser.parse_args(["--tag", "lab", "--tag", "x"]).tags)
```
answer: ['lab', 'x']
> Each `--tag` appends one value, in order, to the list stored under `tags`.

--- teach #card-f50d0d8f7ab557fd
### Options that cannot be combined
A mutually exclusive group holds options of which at most one may be given. Passing two of them is a usage error, handled by argparse.
```python
state = parser.add_mutually_exclusive_group()
state.add_argument("--online", action="store_true")
state.add_argument("--offline", action="store_true")
```
Both attributes still exist on the Namespace; the one not given is `False`.

--- fill #card-0ce54918d6b156ac
Complete the line so `--online` and `--offline` cannot be used together.
```python
state = parser.___()
state.add_argument("--online", action="store_true")
state.add_argument("--offline", action="store_true")
```
answer: add_mutually_exclusive_group
> Arguments added to the group, rather than to the parser, are checked against each other.

--- teach #card-673368b49b055545
### Build the parser in a function, pass argv in
Put the parser inside `build_parser()` so tests can inspect its configuration. The wrapper below builds a fresh parser for each call and takes an explicit argument list, making it easy to test without changing `sys.argv`. A parser can also be reused: the built-in `append` action copies an existing list before adding a value; it does not append into the parser's default list. Only the `if __name__ == "__main__":` block calls `parse_args()` with no argument, which reads `sys.argv`.
```python
def build_parser():
    parser = argparse.ArgumentParser(prog="devreport")
    ...
    return parser

def parse_args(argv):
    return build_parser().parse_args(argv)
```

--- quiz #card-5cff30fc93235159
Why separate `build_parser()` from `parse_args(argv)` in this design?
- [ ] Parsers can only be used once
- [x] Tests can inspect the parser and pass explicit arguments without changing `sys.argv`
- [ ] It makes parsing faster
> The separation makes configuration and parsing easy to test. Reusing a parser is valid: `append` copies the list before adding values. If an option is absent, a returned mutable default may still be shared, so caller code should avoid mutating it.

--- exercise 10.2 #card-8f3e3d72892955d4

--- recap #card-02f1db150f8454a2
- `ArgumentParser` plus `add_argument` describe the interface; `parse_args(list)` returns a Namespace.
- `type=int` converts and validates; `choices` restricts; `default` fills in.
- `action="store_true"` for flags, `action="append"` with `dest` for repeatable options.
- `add_mutually_exclusive_group()` for options that cannot be combined.
- Build the parser in a function and pass `argv` explicitly; usage errors raise `SystemExit`.
