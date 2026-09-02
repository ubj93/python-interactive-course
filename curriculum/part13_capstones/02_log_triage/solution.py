"""Reference solution for log_triage."""
import json
import re
from collections import Counter
from typing import Dict, List, Optional, Tuple

RULES: List[Tuple[str, str]] = [
    ("auth", "permission denied"),
    ("auth", "unauthorized"),
    ("network", "could not resolve"),
    ("network", "connection refused"),
    ("network", "timed out"),
    ("disk", "no space left"),
    ("disk", "read-only file system"),
    ("install", "install failed"),
    ("install", "signature"),
]

# Named groups make the parse self-documenting; the pid is optional so both
# "munki[123]:" and "jamf:" match. Anchors keep partial lines from half-matching.
SYSLOG = re.compile(
    r"^[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+"
    r"(?P<host>\S+)\s+(?P<process>[^\s\[:]+)(?:\[\d+\])?:\s*(?P<message>.*)$"
)


# Best practice: try the cheap, specific check first (does it look like JSON?),
# fall back to the regex, and return None for everything else. Never raise on junk:
# a log parser that crashes on one bad line is worse than one that skips it.
def parse_line(line: str) -> Optional[Dict[str, str]]:
    line = line.strip()
    if not line:
        return None
    if line.startswith("{"):
        try:
            obj = json.loads(line)
        except ValueError:
            return None
        if not isinstance(obj, dict) or not isinstance(obj.get("host"), str) or not isinstance(obj.get("message"), str):
            return None
        return {
            "host": obj["host"].strip().lower(),
            "process": str(obj.get("process") or "").strip(),
            "message": obj["message"].strip(),
        }
    m = SYSLOG.match(line)
    if not m:
        return None
    return {"host": m["host"].lower(), "process": m["process"], "message": m["message"].strip()}


def classify(message: str, rules: List[Tuple[str, str]] = RULES) -> Optional[str]:
    text = message.lower()
    for error_class, needle in rules:
        if needle.lower() in text:
            return error_class
    return None


def count_offenders(records: List[Dict[str, str]], rules: List[Tuple[str, str]] = RULES) -> Dict[Tuple[str, str], int]:
    counts: Counter = Counter()
    for rec in records:
        error_class = classify(rec["message"], rules)
        if error_class is not None:
            counts[(rec["host"], error_class)] += 1
    return dict(counts)


# Sort once with a composite key instead of Counter.most_common, whose tie order
# is insertion order and therefore depends on the input, not on the spec.
def top_offenders(counts: Dict[Tuple[str, str], int], n: int) -> List[Tuple[str, str, int]]:
    rows = [(host, error_class, count) for (host, error_class), count in counts.items()]
    rows.sort(key=lambda r: (-r[2], r[0], r[1]))
    return rows[:n]


def log_triage(text: str, n: int = 3, rules: List[Tuple[str, str]] = RULES) -> List[Tuple[str, str, int]]:
    records = [rec for rec in map(parse_line, text.splitlines()) if rec is not None]
    return top_offenders(count_offenders(records, rules), n)
