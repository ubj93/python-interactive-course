"""Reference solutions for group_by_department."""
from typing import Any, Dict, List


# Best practice: normalise the key, skip what the spec says to skip, then
# setdefault(key, []).append(...) creates the group on first sight and reuses it after.
def group_by_department(devices: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    groups: Dict[str, List[str]] = {}
    for device in devices:
        hostname = device.get("hostname")
        if hostname is None:
            continue
        department = (device.get("department") or "").strip() or "unassigned"
        groups.setdefault(department, []).append(hostname)
    return groups


# Clever: defaultdict(list) removes the setdefault call. Convert back to a plain dict
# at the end so a caller's typo in a key lookup raises instead of inserting an empty group.
def group_by_department_defaultdict(devices: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    from collections import defaultdict

    groups: Dict[str, List[str]] = defaultdict(list)
    for device in devices:
        if device.get("hostname") is None:
            continue
        department = (device.get("department") or "").strip() or "unassigned"
        groups[department].append(device["hostname"])
    return dict(groups)
