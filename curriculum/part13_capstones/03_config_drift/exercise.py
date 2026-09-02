"""Config drift: expected vs actual.

A compliance job pulls the effective configuration of every endpoint (a nested
dict decoded from a plist or JSON) and compares it with the expected baseline.
Write a path-addressed diff that a human can read and a ticket can quote.

A drift record is a dict:

    {"path": "security.firewall.stealth", "kind": "changed", "expected": True, "actual": False}

Rules:
- paths are dotted; list positions are numeric segments ("dock.apps.1"); the
  root has path "" and is always a dict on both sides
- dicts: a key in expected but not actual -> "missing" (actual is None); a key
  in actual but not expected -> "extra" (expected is None); shared keys recurse
- lists are compared positionally: index i present on one side only is
  "missing" or "extra"; shared positions recurse
- anything else (scalars, or a dict/list against a non-container or against a
  container of the other kind) is "changed" when the values differ; values are
  equal only when they have the same type AND compare equal, so 1 and 1.0, or
  True and 1, are drift
- `ignore` is an iterable of path prefixes: a record is dropped when its path
  equals a prefix or starts with prefix + "."
- output sorted by path, compared as the tuple of dotted segments, i.e. plain
  string comparison per segment ("apps.10" sorts before "apps.2")

is_ignored(path, ignore) -> bool
diff_values(expected, actual, path="") -> list of records, any order, no ignore
config_drift(expected, actual, ignore=()) -> list of records, filtered, sorted

Examples:
    >>> config_drift({"a": 1, "b": {"c": 2}}, {"a": 1, "b": {"c": 3, "d": 4}})
    [{'path': 'b.c', 'kind': 'changed', 'expected': 2, 'actual': 3}, {'path': 'b.d', 'kind': 'extra', 'expected': None, 'actual': 4}]
    >>> is_ignored("dock.apps.1", ["dock.apps"])
    True
    >>> is_ignored("dock.apps_extra", ["dock.apps"])
    False
"""
from typing import Any, Dict, Iterable, List


def is_ignored(path: str, ignore: Iterable[str]) -> bool:
    raise NotImplementedError("write is_ignored")


def diff_values(expected: Any, actual: Any, path: str = "") -> List[Dict[str, Any]]:
    raise NotImplementedError("write diff_values")


def config_drift(expected: Dict[str, Any], actual: Dict[str, Any], ignore: Iterable[str] = ()) -> List[Dict[str, Any]]:
    raise NotImplementedError("write config_drift")
