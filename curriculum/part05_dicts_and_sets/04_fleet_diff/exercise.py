"""Diff the fleet across three sources.

Three systems each claim to know which devices we own: the MDM, the asset
inventory, and purchasing's list of every serial ever bought. Write
`fleet_diff(mdm, inventory, purchased=None)` that reconciles them and returns a
dict with four keys, each a SORTED list of serials:

- "only_mdm":       in the MDM but not in the inventory
- "only_inventory": in the inventory but not in the MDM
- "both":           in the MDM and in the inventory
- "neither":        in the purchased list but in neither the MDM nor the inventory;
                    an empty list when `purchased` is None

Rules:
- the inputs are iterables of serial strings (lists, sets, tuples, generators)
- serials are normalised before comparing: surrounding whitespace stripped and
  uppercased, so " c02a " and "C02A" are the same device
- duplicates in an input count once
- blank serials (empty after stripping) are ignored
- the output lists contain the normalised serials

Use set operations; do not write nested loops.

Examples:
    >>> fleet_diff(["C02A", "C02B"], ["c02b", "C02C"], ["C02A", "C02B", "C02C", "C02D"])
    {'only_mdm': ['C02A'], 'only_inventory': ['C02C'], 'both': ['C02B'], 'neither': ['C02D']}
"""
from typing import Dict, Iterable, List, Optional


def fleet_diff(
    mdm: Iterable[str],
    inventory: Iterable[str],
    purchased: Optional[Iterable[str]] = None,
) -> Dict[str, List[str]]:
    raise NotImplementedError("write fleet_diff")
