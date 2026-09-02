"""Tail a log file.

Write `tail_lines(path, n=10)` that returns the last `n` lines of a text file
(UTF-8) as a list of strings without their trailing newline, oldest first, like
`tail -n`. The file may be far bigger than memory, so do not read it all: iterate
it and keep only the newest `n` lines with a `collections.deque(maxlen=n)`.

Rules:
- lines are returned without the trailing "\\n" (and without "\\r" on CRLF files);
  other whitespace is left alone
- a final line with no newline still counts as a line
- if the file has fewer than `n` lines, return all of them
- n == 0 returns []
- n < 0 raises ValueError
- an empty file returns []
- `path` may be a str or a pathlib.Path; a missing file raises FileNotFoundError
- do not call read() or readlines() on the file (the last test checks this)

Examples:
    given agent.log containing five lines "l1" .. "l5":
    >>> tail_lines("agent.log", 2)
    ['l4', 'l5']
    >>> tail_lines("agent.log", 10)
    ['l1', 'l2', 'l3', 'l4', 'l5']
"""
from collections import deque
from pathlib import Path
from typing import List, Union


def tail_lines(path: Union[str, Path], n: int = 10) -> List[str]:
    raise NotImplementedError("write tail_lines")
