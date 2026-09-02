"""Count log levels in an agent log.

The MDM agent writes one event per line. The level is the first token in square
brackets, right after the timestamp:

    2024-05-01 10:00:01 [INFO] mdmclient: checking in
    2024-05-01 10:00:02 [WARN] mdmclient: profile com.corp.wifi missing
    2024-05-01 10:00:03 [ERROR] mdmclient: push token rejected [ERROR 403]

Write `count_log_levels(path)` that reads the file (UTF-8) one line at a time and
returns a dict with exactly the keys "ERROR", "WARN" and "INFO", in that order,
mapping to how many lines carry that level. Missing levels count 0, so an empty
file returns {"ERROR": 0, "WARN": 0, "INFO": 0}.

Rules:
- only the FIRST bracketed token on a line counts; "[ERROR 403]" later in the
  message above does not make that line count twice
- "[WARNING]" counts as "WARN"
- levels are uppercase; "[error]" and "[Info]" are ignored
- lines with no bracketed token, or with an unknown level such as "[DEBUG]", are
  ignored
- lines may have leading whitespace before the timestamp
- the log can be large: iterate the file, do not read() or readlines() it
- `path` may be a str or a pathlib.Path; a missing file raises FileNotFoundError

Examples:
    >>> count_log_levels("agent.log")     # the three lines above
    {'ERROR': 1, 'WARN': 1, 'INFO': 1}
"""
from pathlib import Path
from typing import Dict, Union


def count_log_levels(path: Union[str, Path]) -> Dict[str, int]:
    raise NotImplementedError("write count_log_levels")
