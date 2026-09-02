"""Parse BSD-style syslog lines.

A macOS fleet forwards lines in the classic syslog shape:

    Jun 12 14:03:22 mbp-j-doe mdmclient[512]: Received push notification
    Jun  2 09:00:01 mbp-j-doe kernel: AppleCamIn::wakeEventHandlerThread
    Jun 12 14:03:23 win-lab-01 com.apple.xpc.launchd[1]: Service exited: reason: crash

Write `parse_syslog_line(line)` that returns a dict with exactly these keys:

- "timestamp": the first 15 characters, "Mon DD HH:MM:SS", exactly as written
  (a single-digit day is padded with a space, "Jun  2 09:00:01"; keep it)
- "host": the hostname, a run of non-whitespace characters
- "process": the process name: everything after the host up to the "[" or ":"
  that ends it; it may contain letters, digits, dots, hyphens and underscores
- "pid": the integer inside the square brackets, or None when there are none
- "message": everything after the ": " that follows the process/pid; it may
  itself contain ": ", and it may be empty

A line that does not have this shape returns None. Use one compiled pattern
with named groups and re.fullmatch; do not split on spaces by hand.

Then write `parse_syslog(lines)` that takes an iterable of lines and returns a
list of the parsed dicts, in order, skipping blank lines and lines that do not
parse. Trailing newlines on the lines must not break parsing.

Examples:
    >>> parse_syslog_line("Jun 12 14:03:22 mbp-j-doe mdmclient[512]: Received push")
    {'timestamp': 'Jun 12 14:03:22', 'host': 'mbp-j-doe', 'process': 'mdmclient', 'pid': 512, 'message': 'Received push'}
    >>> parse_syslog_line("Jun  2 09:00:01 mbp-j-doe kernel: hello")["pid"] is None
    True
    >>> parse_syslog_line("not a syslog line") is None
    True
"""
import re
from typing import Dict, Iterable, List, Optional, Union

Parsed = Dict[str, Union[str, int, None]]


def parse_syslog_line(line: str) -> Optional[Parsed]:
    raise NotImplementedError("write parse_syslog_line")


def parse_syslog(lines: Iterable[str]) -> List[Parsed]:
    raise NotImplementedError("write parse_syslog")
