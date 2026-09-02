"""Reference solutions for top_n_by_memory."""
from typing import Any, Dict, List


# Best practice: one sorted() call with a tuple key. Negating the memory sorts it
# descending while the hostname stays ascending, so no reverse=True is needed. Slicing
# with a negative n gives [] on its own, but the guard says the intent out loud.
def top_n_by_memory(devices: List[Dict[str, Any]], n: int) -> List[str]:
    if n <= 0:
        return []
    ranked = sorted(devices, key=lambda d: (-(d.get("memory_gb") or 0), d["hostname"]))
    return [d["hostname"] for d in ranked[:n]]


# Clever: two passes that lean on sort stability. Sort by the secondary key first, then
# by the primary; equal memory keeps the hostname order from pass one. This is the way
# to go when the secondary key is a string that has to run *descending*.
def top_n_by_memory_two_pass(devices: List[Dict[str, Any]], n: int) -> List[str]:
    if n <= 0:
        return []
    by_name = sorted(devices, key=lambda d: d["hostname"])
    ranked = sorted(by_name, key=lambda d: d.get("memory_gb") or 0, reverse=True)
    return [d["hostname"] for d in ranked[:n]]
