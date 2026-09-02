"""Reference solutions for fleet_diff."""
from typing import Dict, Iterable, List, Optional, Set


def _serials(source: Iterable[str]) -> Set[str]:
    # A set comprehension does the deduplication; the `if` drops blanks after stripping.
    return {s.strip().upper() for s in source if s.strip()}


# Best practice: normalise each source into a set once, then every bucket is a single
# set expression. Sorting at the end gives the deterministic output the spec wants.
def fleet_diff(
    mdm: Iterable[str],
    inventory: Iterable[str],
    purchased: Optional[Iterable[str]] = None,
) -> Dict[str, List[str]]:
    m = _serials(mdm)
    i = _serials(inventory)
    p = _serials(purchased) if purchased is not None else set()
    return {
        "only_mdm": sorted(m - i),
        "only_inventory": sorted(i - m),
        "both": sorted(m & i),
        "neither": sorted(p - (m | i)),
    }


# Clever: the same thing with the method forms, which accept any iterable and read as
# English. Handy when a teammate does not remember which operator is which.
def fleet_diff_methods(
    mdm: Iterable[str],
    inventory: Iterable[str],
    purchased: Optional[Iterable[str]] = None,
) -> Dict[str, List[str]]:
    m, i = _serials(mdm), _serials(inventory)
    p = _serials(purchased or [])
    return {
        "only_mdm": sorted(m.difference(i)),
        "only_inventory": sorted(i.difference(m)),
        "both": sorted(m.intersection(i)),
        "neither": sorted(p.difference(m.union(i))),
    }
