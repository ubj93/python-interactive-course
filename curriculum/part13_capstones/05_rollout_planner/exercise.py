"""Rollout planner: rings, percentages, blockers and holds.

We push an OS update in rings. Each ring has a list of cumulative percentage
targets, one per day; rings run one after another in the order given. Devices
that cannot take the update yet are skipped and listed with a reason.

Inputs:

    devices = [{"serial": "C02ABC", "ring": "Canary", "os_version": "14.4.1", "blockers": []}, ...]
    rings   = [("canary", [100]), ("early", [50, 100]), ("broad", [10, 40, 100])]
    holds   = {"14.4.1"}                     # os versions the update is paused for
    start   = date(2024, 6, 3)               # calendar date of day 1

skip_reason(device, ring_names, holds) -> str or None
- ring labels are compared stripped and lowercased; os versions stripped
- first matching reason: "blocked: <blockers sorted, joined by ', '>" when the
  device has blockers; "hold: <os_version>" when its os_version is in holds;
  "unknown ring: <ring>" when its ring is not in ring_names (empty ring gives
  "unknown ring: "); None when the device is eligible

partition_devices(devices, ring_names, holds) -> (dict, list)
- {ring_name: sorted list of eligible serials} with a key for EVERY ring name
  (possibly empty), and the skipped list [{"serial", "reason"}] sorted by serial
- serials are stripped and uppercased; a serial seen before is skipped with
  reason "duplicate" (the first row is the one that counts)

cumulative_targets(n, pcts) -> list of ints
- target for each day = ceil(n * pct / 100) using integer arithmetic, so 3
  devices at 10% gives 1 and 0 devices gives 0
- raise ValueError when pcts is empty, not non-decreasing, or does not end at 100

plan_rollout(devices, rings, holds, start) -> dict
- {"days": [...], "skipped": [...]}; one entry per ring per percentage, numbered
  from day 1, dates consecutive from `start` (no weekend logic):
  {"day": 1, "date": "2024-06-03", "ring": "canary", "serials": [...]}
- a day's serials are the ring's next slice: from the previous day's cumulative
  target up to today's, in sorted serial order; days with no new devices still
  appear with an empty list

Examples:
    >>> cumulative_targets(7, [10, 40, 100])
    [1, 3, 7]
    >>> skip_reason({"serial": "A", "ring": "broad", "os_version": "14.4.1", "blockers": ["low_disk", "on_battery"]}, ["broad"], {"14.4.1"})
    'blocked: low_disk, on_battery'
"""
from datetime import date, timedelta
from typing import Dict, Iterable, List, Optional, Set, Tuple


def skip_reason(device: dict, ring_names: Iterable[str], holds: Set[str]) -> Optional[str]:
    raise NotImplementedError("write skip_reason")


def partition_devices(devices: List[dict], ring_names: Iterable[str], holds: Set[str]) -> Tuple[Dict[str, List[str]], List[Dict[str, str]]]:
    raise NotImplementedError("write partition_devices")


def cumulative_targets(n: int, pcts: List[int]) -> List[int]:
    raise NotImplementedError("write cumulative_targets")


def plan_rollout(devices: List[dict], rings: List[Tuple[str, List[int]]], holds: Set[str], start: date) -> dict:
    raise NotImplementedError("write plan_rollout")
