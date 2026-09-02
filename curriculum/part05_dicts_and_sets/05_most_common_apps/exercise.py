"""Find the most widely installed apps.

An app-inventory export gives, per device, the list of application names found
on it. Write `most_common_apps(installs, k)` that returns the k most widely
installed apps as a list of (app, device_count) tuples.

Rules:
- `installs` maps a device serial to a list of app names
- an app counts ONCE per device even if it appears several times in that
  device's list (multiple copies, several versions)
- sort by device count descending; ties are broken by app name ascending
  (plain string comparison, so "Chrome" sorts before "chrome")
- return at most k entries; fewer when there are fewer distinct apps
- k <= 0, or no installs at all, gives []
- do not modify the input

Examples:
    >>> installs = {
    ...     "C02A": ["Slack", "Chrome", "Slack"],
    ...     "C02B": ["Chrome", "Zoom"],
    ...     "C02C": ["Zoom", "Chrome"],
    ... }
    >>> most_common_apps(installs, 2)
    [('Chrome', 3), ('Zoom', 2)]
    >>> most_common_apps(installs, 10)
    [('Chrome', 3), ('Zoom', 2), ('Slack', 1)]
"""
from typing import Dict, List, Tuple


def most_common_apps(installs: Dict[str, List[str]], k: int) -> List[Tuple[str, int]]:
    raise NotImplementedError("write most_common_apps")
