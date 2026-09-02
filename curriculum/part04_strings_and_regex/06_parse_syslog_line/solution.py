"""Reference solutions for parse_syslog_line and parse_syslog."""
import re
from typing import Dict, Iterable, List, Optional, Union

Parsed = Dict[str, Union[str, int, None]]

# re.VERBOSE lets the pattern carry its own documentation. The process class excludes
# '[' and ':' so the first of either ends the name; the message is "the rest".
SYSLOG = re.compile(
    r"""
    (?P<timestamp>[A-Z][a-z]{2}\ [\ \d]\d\ \d\d:\d\d:\d\d)\ +
    (?P<host>\S+)\ +
    (?P<process>[\w.-]+)
    (?:\[(?P<pid>\d+)\])?
    :\ ?
    (?P<message>.*)
    """,
    re.VERBOSE,
)


# Best practice: fullmatch, groupdict, then fix up the one field whose type is not str.
def parse_syslog_line(line: str) -> Optional[Parsed]:
    m = SYSLOG.fullmatch(line.rstrip("\n"))
    if not m:
        return None
    parsed: Parsed = m.groupdict()
    parsed["pid"] = int(m.group("pid")) if m.group("pid") else None
    return parsed


# Best practice: reuse the single-line parser; a comprehension with a walrus keeps it short.
def parse_syslog(lines: Iterable[str]) -> List[Parsed]:
    return [p for line in lines if (p := parse_syslog_line(line)) is not None]


# Clever: no regex. The timestamp is fixed-width, then split(maxsplit) does the rest.
# Fragile (it trusts the width) but shows that the shape is mostly positional.
def parse_syslog_line_split(line: str) -> Optional[Parsed]:
    line = line.rstrip("\n")
    if len(line) < 16 or not re.fullmatch(r"[A-Z][a-z]{2} [ \d]\d \d\d:\d\d:\d\d", line[:15]):
        return None
    rest = line[16:]
    parts = rest.split(" ", 2)
    if len(parts) < 2:
        return None
    host, tag = parts[0], parts[1]
    message = parts[2] if len(parts) == 3 else ""
    if not tag.endswith(":"):
        return None
    tag = tag[:-1]
    name, _, pid_text = tag.partition("[")
    pid: Optional[int] = None
    if pid_text:
        if not pid_text.endswith("]") or not pid_text[:-1].isdigit():
            return None
        pid = int(pid_text[:-1])
    if not re.fullmatch(r"[\w.-]+", name):
        return None
    return {"timestamp": line[:15], "host": host, "process": name, "pid": pid, "message": message}
