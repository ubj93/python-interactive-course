"""Reference solutions for os_family."""
from typing import Optional


# Best practice: normalise once, then test in priority order with early returns.
def os_family(os_string: Optional[str]) -> str:
    s = (os_string or "").strip().lower()
    if not s:
        return "other"
    if s.startswith(("ios", "ipados")):
        return "ios"
    if "mac" in s or "os x" in s:
        return "mac"
    if "windows" in s:
        return "windows"
    if any(k in s for k in ("linux", "ubuntu", "debian", "fedora", "rhel", "centos")):
        return "linux"
    return "other"


# Clever: a rules table. Same logic, data-driven; easy to extend without touching control flow.
RULES = [
    ("ios", ("ios", "ipados")),
    ("mac", ("mac", "os x")),
    ("windows", ("windows",)),
    ("linux", ("linux", "ubuntu", "debian", "fedora", "rhel", "centos")),
]


def os_family_table(os_string: Optional[str]) -> str:
    s = (os_string or "").strip().lower()
    for family, keywords in RULES:
        if family == "ios":
            if s.startswith(keywords):
                return family
        elif any(k in s for k in keywords):
            return family
    return "other"
