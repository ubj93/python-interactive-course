"""Group hostnames by department.

Write `group_by_department(devices)` that takes a list of device dicts and
returns a dict mapping each department to the list of hostnames in it.

Rules:
- department is the "department" value with surrounding whitespace stripped;
  the comparison is case-sensitive ("IT" and "it" are different groups)
- a device whose department is missing, None, or blank after stripping goes
  under "unassigned"
- a device without a "hostname" key (or with None as hostname) is skipped
- departments appear in the order they were first seen; hostnames inside a
  group keep the input order, duplicates included
- an empty list gives {}

Build it with a loop and dict.setdefault (or a membership check); leave
collections.defaultdict for later.

Examples:
    >>> group_by_department([
    ...     {"hostname": "mbp-1", "department": "Finance"},
    ...     {"hostname": "mbp-2", "department": " IT "},
    ...     {"hostname": "mbp-3", "department": "Finance"},
    ...     {"hostname": "mbp-4"},
    ... ])
    {'Finance': ['mbp-1', 'mbp-3'], 'IT': ['mbp-2'], 'unassigned': ['mbp-4']}
"""
from typing import Any, Dict, List


def group_by_department(devices: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    raise NotImplementedError("write group_by_department")
