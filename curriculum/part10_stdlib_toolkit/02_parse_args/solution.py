"""Reference solutions for build_parser / parse_args."""
import argparse
from typing import List


# Best practice: build the parser in a function so every parse gets a fresh one (no shared
# mutable defaults) and tests can inspect it. type=int makes argparse do the conversion
# and the error reporting; choices does the validation.
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="devreport", description="Report on one device.")
    parser.add_argument("serial", help="device serial number")
    parser.add_argument("--format", choices=["table", "json", "csv"], default="table")
    parser.add_argument("--days", type=int, default=30, help="how far back to look")
    parser.add_argument("--tag", dest="tags", action="append", default=[], help="repeatable")
    parser.add_argument("-v", "--verbose", action="store_true")
    state = parser.add_mutually_exclusive_group()
    state.add_argument("--online", action="store_true")
    state.add_argument("--offline", action="store_true")
    return parser


def parse_args(argv: List[str]) -> argparse.Namespace:
    return build_parser().parse_args(argv)


# Clever: a custom `type` callable gives you validation with argparse's own error message.
# Raise argparse.ArgumentTypeError and the user sees "argument --days: ...".
def positive_int(text: str) -> int:
    value = int(text)  # ValueError here also becomes a clean usage error
    if value <= 0:
        raise argparse.ArgumentTypeError(f"must be positive, got {value}")
    return value


def build_parser_validated() -> argparse.ArgumentParser:
    parser = build_parser()
    parser.set_defaults(days=30)
    for action in parser._actions:  # private, but handy in a REPL to tweak an existing parser
        if action.dest == "days":
            action.type = positive_int
    return parser
