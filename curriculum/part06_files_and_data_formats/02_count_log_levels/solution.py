"""Reference solutions for count_log_levels."""
import re
from pathlib import Path
from typing import Dict, Union

LEVELS = ("ERROR", "WARN", "INFO")
ALIASES = {"WARNING": "WARN"}


# Best practice: seed the dict so the keys are always present and ordered, then stream
# the file. str.partition finds the first '[' and the first ']' after it without a regex.
def count_log_levels(path: Union[str, Path]) -> Dict[str, int]:
    counts = {level: 0 for level in LEVELS}
    with open(path, encoding="utf-8") as f:
        for line in f:
            _, opened, rest = line.partition("[")
            if not opened:
                continue
            token, closed, _ = rest.partition("]")
            if not closed:
                continue
            level = ALIASES.get(token, token)
            if level in counts:
                counts[level] += 1
    return counts


# Clever: a compiled regex anchored with re.search finds the first bracketed word; the
# alternation lists the accepted spellings so nothing else can match.
FIRST_LEVEL = re.compile(r"\[(ERROR|WARNING|WARN|INFO)\]")


def count_log_levels_regex(path: Union[str, Path]) -> Dict[str, int]:
    counts = {level: 0 for level in LEVELS}
    with open(path, encoding="utf-8") as f:
        for line in f:
            _, opened, rest = line.partition("[")
            m = FIRST_LEVEL.match("[" + rest) if opened else None
            if m:
                counts[ALIASES.get(m.group(1), m.group(1))] += 1
    return counts
