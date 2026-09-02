"""Reference solution for rollout_planner."""
from datetime import date, timedelta
from typing import Dict, Iterable, List, Optional, Set, Tuple


# Best practice: the eligibility policy lives in one function that returns a
# reason string. The caller never re-derives the rule, and a None return is the
# only "go" signal, so adding a fourth reason later touches one place.
def skip_reason(device: dict, ring_names: Iterable[str], holds: Set[str]) -> Optional[str]:
    blockers = sorted(device.get("blockers") or [])
    if blockers:
        return "blocked: " + ", ".join(blockers)
    os_version = (device.get("os_version") or "").strip()
    if os_version in {h.strip() for h in holds}:
        return f"hold: {os_version}"
    ring = (device.get("ring") or "").strip().lower()
    if ring not in set(ring_names):
        return f"unknown ring: {ring}"
    return None


def partition_devices(devices: List[dict], ring_names: Iterable[str], holds: Set[str]) -> Tuple[Dict[str, List[str]], List[Dict[str, str]]]:
    names = list(ring_names)
    by_ring: Dict[str, List[str]] = {name: [] for name in names}
    skipped: List[Dict[str, str]] = []
    seen: Set[str] = set()
    for device in devices:
        serial = (device.get("serial") or "").strip().upper()
        reason = "duplicate" if serial in seen else skip_reason(device, names, holds)
        seen.add(serial)
        if reason is not None:
            skipped.append({"serial": serial, "reason": reason})
        else:
            by_ring[(device.get("ring") or "").strip().lower()].append(serial)
    for serials in by_ring.values():
        serials.sort()
    return by_ring, sorted(skipped, key=lambda s: s["serial"])


# Integer ceil: (a + b - 1) // b. Floats would give 0.30000000000000004 for 3 * 10 / 100
# and, worse, would round differently on different inputs; the plan must be reproducible.
def cumulative_targets(n: int, pcts: List[int]) -> List[int]:
    if not pcts or pcts[-1] != 100 or any(a > b for a, b in zip(pcts, pcts[1:])):
        raise ValueError(f"percentages must be non-decreasing and end at 100: {pcts}")
    return [(n * pct + 99) // 100 for pct in pcts]


def plan_rollout(devices: List[dict], rings: List[Tuple[str, List[int]]], holds: Set[str], start: date) -> dict:
    ring_names = [name for name, _ in rings]
    by_ring, skipped = partition_devices(devices, ring_names, holds)
    days: List[dict] = []
    day = 0
    for name, pcts in rings:
        serials = by_ring[name]
        previous = 0
        for target in cumulative_targets(len(serials), pcts):
            day += 1
            days.append({
                "day": day,
                "date": (start + timedelta(days=day - 1)).isoformat(),
                "ring": name,
                "serials": serials[previous:target],
            })
            previous = target
    return {"days": days, "skipped": skipped}
