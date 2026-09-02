"""Reference solution for config_drift."""
from typing import Any, Dict, Iterable, List


def is_ignored(path: str, ignore: Iterable[str]) -> bool:
    # The "+ ." matters: "dock.apps" must ignore "dock.apps.1" but not "dock.apps_extra".
    return any(path == prefix or path.startswith(prefix + ".") for prefix in ignore)


def _record(path: str, kind: str, expected: Any, actual: Any) -> Dict[str, Any]:
    return {"path": path, "kind": kind, "expected": expected, "actual": actual}


def _join(path: str, key: Any) -> str:
    return f"{path}.{key}" if path else str(key)


# Best practice: one recursive function with three shapes (dict/dict, list/list,
# everything else). Recursing on shared keys and emitting leaf records keeps the
# ignore/sort concerns out of the walk entirely.
def diff_values(expected: Any, actual: Any, path: str = "") -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if isinstance(expected, dict) and isinstance(actual, dict):
        for key, value in expected.items():
            if key in actual:
                out.extend(diff_values(value, actual[key], _join(path, key)))
            else:
                out.append(_record(_join(path, key), "missing", value, None))
        for key, value in actual.items():
            if key not in expected:
                out.append(_record(_join(path, key), "extra", None, value))
    elif isinstance(expected, list) and isinstance(actual, list):
        for i in range(max(len(expected), len(actual))):
            if i >= len(actual):
                out.append(_record(_join(path, i), "missing", expected[i], None))
            elif i >= len(expected):
                out.append(_record(_join(path, i), "extra", None, actual[i]))
            else:
                out.extend(diff_values(expected[i], actual[i], _join(path, i)))
    elif type(expected) is not type(actual) or expected != actual:
        # `type(...) is not type(...)` is the whole reason True vs 1 counts as drift:
        # == alone says they are equal.
        out.append(_record(path, "changed", expected, actual))
    return out


def config_drift(expected: Dict[str, Any], actual: Dict[str, Any], ignore: Iterable[str] = ()) -> List[Dict[str, Any]]:
    prefixes = list(ignore)
    records = [r for r in diff_values(expected, actual) if not is_ignored(r["path"], prefixes)]
    return sorted(records, key=lambda r: tuple(r["path"].split(".")))
