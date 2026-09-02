"""Extract IPv4 addresses from text.

Support engineers paste whole chunks of log output into tickets. Write
`extract_ips(text)` that returns every valid IPv4 address found in the text, as a
list of strings, in the order they appear. Keep duplicates.

An address is four groups of 1 to 3 digits separated by dots, and:
- every group must be in the range 0..255
- a group may not have a leading zero unless it is exactly "0" ("010" is invalid)
- the address must not be immediately preceded or followed by a digit or a dot,
  so "10.1.2.3.4" contains no address and neither does "1234.1.2.3"
- anything else may surround it: "10.0.0.5:443", "(10.0.0.5)", "ip=10.0.0.5,"

Use a regular expression to find candidates and plain Python to check the
ranges; do not try to encode 0..255 in the pattern.

Examples:
    >>> extract_ips("connected to 10.0.0.5:443 from 192.168.1.20")
    ['10.0.0.5', '192.168.1.20']
    >>> extract_ips("bad 256.1.1.1 and 10.1.2.3.4")
    []
    >>> extract_ips("")
    []
"""
import re
from typing import List


def extract_ips(text: str) -> List[str]:
    raise NotImplementedError("write extract_ips")
