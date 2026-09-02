"""Reference solutions for disk_status."""
from typing import Optional


# Best practice: reject bad input first, then thresholds from highest to lowest with early returns.
def disk_status(used_fraction: Optional[float]) -> str:
    if used_fraction is None or not 0 <= used_fraction <= 1:
        return "UNKNOWN"
    if used_fraction >= 0.95:
        return "CRIT"
    if used_fraction >= 0.80:
        return "WARN"
    return "OK"


# Clever: a threshold table makes it trivial to add levels later (and to load them from config).
THRESHOLDS = [(0.95, "CRIT"), (0.80, "WARN")]


def disk_status_table(used_fraction: Optional[float]) -> str:
    if used_fraction is None or not 0 <= used_fraction <= 1:
        return "UNKNOWN"
    for limit, label in THRESHOLDS:
        if used_fraction >= limit:
            return label
    return "OK"
