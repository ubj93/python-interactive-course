"""Flatten a nested dict to dotted keys, and back.

Configuration profiles nest several levels deep, but diff tools, CSV exports
and osquery-style queries want one flat row of "a.b.c" keys. Write both
directions.

`flatten_dict(d, sep=".")`
- every path from the root to a leaf becomes one key: the path's keys joined
  by `sep`
- a leaf is anything that is not a dict: numbers, strings, None, lists (a list
  is a leaf; do not expand it)
- an EMPTY dict is also a leaf: {"a": {}} flattens to {"a": {}}
- keys are strings; keys keep the order in which they are visited (depth-first,
  in the order of the input)
- {} flattens to {}

`unflatten_dict(flat, sep=".")`
- splits each key on `sep` and rebuilds the nesting
- a key that is both a leaf and a prefix of another key is a conflict:
  {"a": 1, "a.b": 2} raises ValueError
- {} unflattens to {}

For any nested dict d without conflicting keys and without separators inside
its keys, unflatten_dict(flatten_dict(d)) == d.

Examples:
    >>> flatten_dict({"payload": {"wifi": {"ssid": "corp", "hidden": False}}, "name": "Base"})
    {'payload.wifi.ssid': 'corp', 'payload.wifi.hidden': False, 'name': 'Base'}
    >>> unflatten_dict({"a.b": 1, "a.c": 2, "d": 3})
    {'a': {'b': 1, 'c': 2}, 'd': 3}
    >>> flatten_dict({"a": {"b": 1}}, sep="/")
    {'a/b': 1}
"""
from typing import Any, Dict


def flatten_dict(d: Dict[str, Any], sep: str = ".") -> Dict[str, Any]:
    raise NotImplementedError("write flatten_dict")


def unflatten_dict(flat: Dict[str, Any], sep: str = ".") -> Dict[str, Any]:
    raise NotImplementedError("write unflatten_dict")
