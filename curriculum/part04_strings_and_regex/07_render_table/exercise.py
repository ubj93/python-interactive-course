"""Render a plain-text table.

Reports go into Slack and tickets as monospace text. Write
`render_table(headers, rows)` that returns a string like this:

    hostname    os       disk%
    ----------  -------  -----
    mbp-j-doe   macOS     83.5
    win-lab-01  Windows      7

Rules:
- `headers` is a list of column names; `rows` is a list of lists, one per row,
  each with exactly len(headers) cells; a row of the wrong length raises ValueError
- cells are rendered with str(); None is rendered as "-"
- the width of a column is the longest rendered cell in it, header included
- ints and floats are right-aligned; everything else (str, None, bool) is
  left-aligned. bool is a subclass of int in Python; treat it as text here
- the second line is a separator: for every column, '-' repeated to its width
- columns are joined with two spaces; every line has trailing whitespace removed
- lines are joined with "\\n" and there is no trailing newline
- with no rows the result is just the header line and the separator
- an empty headers list raises ValueError

Examples:
    >>> print(render_table(["host", "ram"], [["mbp-1", 16], ["win-lab-01", 8]]))
    host        ram
    ----------  ---
    mbp-1        16
    win-lab-01    8
"""
from typing import Any, List, Sequence


def render_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    raise NotImplementedError("write render_table")
