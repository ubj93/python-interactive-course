"""Deep-merge configuration dictionaries.

Our agent config is layered: a base config, an OS-specific overlay, then a
per-site overlay. Write `merge_configs(*configs)` that merges any number of
nested dicts, left to right, and returns a NEW dict.

Rules:
- when a key is in several configs and both values are dicts, merge them
  recursively
- otherwise the later value wins: a list replaces a list (lists are never
  merged item by item), a scalar replaces a dict, a dict replaces a scalar,
  and an explicit None in a later config replaces an earlier value
- keys keep first-seen order: keys from the first config come first, new keys
  from later configs are appended
- the inputs are not modified, and the result must not share nested dicts or
  lists with the inputs: changing the result afterwards leaves the inputs alone
- called with no arguments, return {}
- any argument that is not a dict raises TypeError

Examples:
    >>> base = {"agent": {"interval": 60, "tags": ["base"]}, "site": "hq"}
    >>> over = {"agent": {"interval": 30, "debug": True}}
    >>> merge_configs(base, over)
    {'agent': {'interval': 30, 'tags': ['base'], 'debug': True}, 'site': 'hq'}
    >>> merge_configs({"a": {"b": 1}}, {"a": 2})
    {'a': 2}
"""
from typing import Any, Dict


def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    raise NotImplementedError("write merge_configs")
