"""Remove duplicate hostnames, keeping the first of each.

Several inventory exports are concatenated into one list of hostnames and the
same machine shows up more than once, sometimes with different casing or with
stray whitespace. Write `dedupe_preserve_order(hostnames)` that returns a new
list with duplicates removed.

Rules:
- two entries are duplicates when they are equal after stripping surrounding
  whitespace and lowercasing ("MBP-J-DOE" and " mbp-j-doe " are the same)
- keep the FIRST occurrence, exactly as it was written (do not clean it)
- keep the original order of first occurrences
- an empty list gives an empty list
- do not modify the input list

set(hostnames) is not enough: sets forget the order, and they would treat
"MBP-J-DOE" and "mbp-j-doe" as different.

Examples:
    >>> dedupe_preserve_order(["mbp-j-doe", "win-lab-01", "MBP-J-DOE", "nuc-01", "win-lab-01"])
    ['mbp-j-doe', 'win-lab-01', 'nuc-01']
    >>> dedupe_preserve_order([" nuc-01", "nuc-01 "])
    [' nuc-01']
"""
from typing import List


def dedupe_preserve_order(hostnames: List[str]) -> List[str]:
    raise NotImplementedError("write dedupe_preserve_order")
