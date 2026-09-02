"""Parse command-line style flags.

A tiny launcher script receives options as separate strings, the way
sys.argv delivers them. Write `parse_flags(*args)` that accepts any number
of positional string arguments and returns a dict:

- "--key=value"  gives  {"key": "value"}   (value is always a string)
- "--flag"       gives  {"flag": True}

Rules:
- split on the FIRST "=" only: "--url=http://x?a=b" gives {"url": "http://x?a=b"}
- "--key=" (nothing after the equals) gives {"key": ""}
- hyphens inside the key become underscores: "--dry-run" gives {"dry_run": True}
- if the same key appears more than once, the last one wins
- no arguments gives {}
- an argument that does not start with "--", or that has an empty key
  ("--" on its own, "--=x"), raises ValueError

Examples:
    >>> parse_flags("--verbose", "--target=mbp-j-doe", "--dry-run")
    {'verbose': True, 'target': 'mbp-j-doe', 'dry_run': True}
    >>> parse_flags("--retries=3", "--retries=5")
    {'retries': '5'}
    >>> parse_flags()
    {}
"""
from typing import Dict, Union


def parse_flags(*args: str) -> Dict[str, Union[str, bool]]:
    raise NotImplementedError("write parse_flags")
