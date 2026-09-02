"""Command-line arguments for a device report tool.

Every internal tool starts life as a script with a few flags. Write
`build_parser()` that returns an `argparse.ArgumentParser` with prog name
"devreport", and `parse_args(argv)` that parses an explicit list of strings and
returns the resulting `argparse.Namespace`. Never read `sys.argv` yourself: the
tests (and any caller) pass the list in, which is what makes the parser testable.

The interface:

- positional `serial`: required, one device serial number
- `--format`: one of "table", "json", "csv"; default "table"
- `--days`: an int, default 30; how far back to look
- `--tag`: may be repeated; every value is collected into a list stored as
  `tags`; the default is an empty list
- `-v` / `--verbose`: boolean flag, default False
- `--online` and `--offline`: boolean flags that are mutually exclusive

Rules:
- argparse reports usage errors by printing to stderr and raising SystemExit.
  Do not catch it. The tests check that a missing serial, an unknown --format,
  a non-integer --days, and --online together with --offline all raise SystemExit.
- Parsing twice must not leak state: two calls to parse_args each get their own
  tags list.

Examples:
    >>> ns = parse_args(["C02XG1234ABC", "--days", "7", "--tag", "lab", "--tag", "loaner"])
    >>> ns.serial, ns.days, ns.tags, ns.format, ns.verbose
    ('C02XG1234ABC', 7, ['lab', 'loaner'], 'table', False)
    >>> parse_args(["C02XG1234ABC", "-v", "--format", "json", "--online"]).online
    True
"""
import argparse
from typing import List


def build_parser() -> argparse.ArgumentParser:
    raise NotImplementedError("write build_parser")


def parse_args(argv: List[str]) -> argparse.Namespace:
    raise NotImplementedError("write parse_args")
