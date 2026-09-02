"""Reference solutions for merge_configs."""
import copy
from typing import Any, Dict


def _merge_two(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)  # shallow copy keeps base's key order; values are replaced below
    for key, value in override.items():
        existing = result.get(key)
        if isinstance(existing, dict) and isinstance(value, dict):
            result[key] = _merge_two(existing, value)
        else:
            result[key] = value
    return result


# Best practice: reduce the variadic problem to "merge two", recurse only when both sides
# are dicts, and deepcopy once at the end so the caller can mutate the result freely.
def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    for cfg in configs:
        if not isinstance(cfg, dict):
            raise TypeError(f"expected a dict, got {type(cfg).__name__}")
    merged: Dict[str, Any] = {}
    for cfg in configs:
        merged = _merge_two(merged, cfg)
    return copy.deepcopy(merged)


# Clever: functools.reduce expresses "fold left over the configs" directly, and deep-copying
# each value as it is inserted avoids the final pass. Same result, more idiomatic to some eyes.
def merge_configs_reduce(*configs: Dict[str, Any]) -> Dict[str, Any]:
    from functools import reduce

    def merge(acc: Dict[str, Any], cfg: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(cfg, dict):
            raise TypeError(f"expected a dict, got {type(cfg).__name__}")
        out = dict(acc)
        for key, value in cfg.items():
            if isinstance(out.get(key), dict) and isinstance(value, dict):
                out[key] = merge(out[key], value)
            else:
                out[key] = copy.deepcopy(value)
        return out

    return reduce(merge, configs, {})
