"""Read a hostname list from a file.

Help-desk keeps a plain text file with one hostname per line. People also leave
blank lines and comments in it. Write `read_hostnames(path)` that opens the file
(UTF-8), and returns the hostnames as a list of strings, in file order.

Rules:
- strip leading and trailing whitespace from every line (spaces, tabs, \\r\\n)
- skip lines that are empty after stripping
- skip comment lines: the first non-blank character is '#' (indented comments too)
- keep everything else exactly as written after stripping (no lowercasing)
- `path` may be a str or a pathlib.Path
- an empty file returns []
- a missing file raises FileNotFoundError (let `open` raise it, do not catch it)

Examples:
    given hosts.txt containing:
        # lab machines
        mbp-j-doe

          win-lab-01
        #win-lab-02 (retired)

    >>> read_hostnames("hosts.txt")
    ['mbp-j-doe', 'win-lab-01']
"""
from pathlib import Path
from typing import List, Union


def read_hostnames(path: Union[str, Path]) -> List[str]:
    raise NotImplementedError("write read_hostnames")
