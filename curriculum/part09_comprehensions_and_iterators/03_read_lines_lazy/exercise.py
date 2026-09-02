"""Stream cleaned lines from a file.

Hostname lists, allowlists and Munki manifests all use the same loose text
format: one entry per line, blank lines ignored, `#` starts a comment that
runs to the end of the line. The files can be large, and the caller wants to
start processing before the file is fully read. Write `read_lines_lazy(lines)`
as a generator function.

- `lines` is any iterable of strings: an open file object, a list, a
  generator. Do not call `list()`, `readlines()` or `read()` on it; iterate.
- For each line: drop everything from the first `#` onwards, then strip
  whitespace from both ends (this removes the trailing newline too).
- Skip the line if nothing is left. Otherwise yield the cleaned text.
- Laziness is part of the contract: pulling one value with `next()` must read
  only as far as needed. The tests feed an infinite generator.

Examples:
    >>> import io
    >>> text = "# fleet allowlist\\n\\nmbp-j-doe   # jane\\n  win-lab-01\\n\\n"
    >>> list(read_lines_lazy(io.StringIO(text)))
    ['mbp-j-doe', 'win-lab-01']
    >>> gen = read_lines_lazy(["a", "#", "b"])
    >>> next(gen)
    'a'
    >>> next(gen)
    'b'
"""
from typing import Iterable, Iterator


def read_lines_lazy(lines: Iterable[str]) -> Iterator[str]:
    raise NotImplementedError("write read_lines_lazy")
