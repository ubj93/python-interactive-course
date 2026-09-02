"""Reference solutions for dedupe_preserve_order."""
from typing import List


# Best practice: the seen-set pattern. The set holds the *normalised* form for fast
# membership tests; the result list holds the original spelling in first-seen order.
def dedupe_preserve_order(hostnames: List[str]) -> List[str]:
    seen = set()
    unique = []
    for host in hostnames:
        key = host.strip().lower()
        if key not in seen:
            seen.add(key)
            unique.append(host)
    return unique


# Clever: a dict keyed by the normalised name. setdefault only stores a value the first
# time a key appears, and dicts keep insertion order, so .values() is the answer.
def dedupe_preserve_order_dict(hostnames: List[str]) -> List[str]:
    first = {}
    for host in hostnames:
        first.setdefault(host.strip().lower(), host)
    return list(first.values())
