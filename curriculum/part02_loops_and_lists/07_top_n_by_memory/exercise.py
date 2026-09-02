"""Rank devices by memory.

The hardware refresh report needs the machines with the most RAM. Each record
is a dict with a "hostname" and a "memory_gb". Write `top_n_by_memory(devices, n)`
that returns a list of the `n` hostnames with the largest memory, biggest first.

Rules:
- ties on memory are broken by hostname in ascending (alphabetical) order
- if n is larger than the number of devices, return every hostname (still sorted)
- if n is 0 or negative, return []
- a record with no "memory_gb" key, or with memory_gb None, counts as 0 GB
- do not reorder or modify the input list; use sorted(), not list.sort()

Examples:
    >>> fleet = [
    ...     {"hostname": "nuc-01", "memory_gb": 16},
    ...     {"hostname": "mbp-j-doe", "memory_gb": 32},
    ...     {"hostname": "mbp-a-kim", "memory_gb": 32},
    ...     {"hostname": "win-lab-01", "memory_gb": 8},
    ... ]
    >>> top_n_by_memory(fleet, 3)
    ['mbp-a-kim', 'mbp-j-doe', 'nuc-01']
    >>> top_n_by_memory(fleet, 0)
    []
"""
from typing import Any, Dict, List


def top_n_by_memory(devices: List[Dict[str, Any]], n: int) -> List[str]:
    raise NotImplementedError("write top_n_by_memory")
