"""Read a JSON state file, or fall back to a default.

The agent keeps its state in state.json. On a fresh machine the file does not
exist yet, which is normal. A file that exists but contains broken JSON is not
normal: somebody edited it by hand or a write was interrupted, and silently
starting over would lose data. Write `read_json_or_default(path, default)` that
tells those two situations apart.

Rules:
- the file exists and holds valid JSON: return the parsed value
- the file does not exist (FileNotFoundError): return the default
- the file exists but is empty or whitespace only: return the default (a file
  that was created but never written counts as "no state yet")
- the file exists but holds invalid JSON (json.JSONDecodeError): raise
  ValueError whose message contains the path as text, chained to the original
  with `raise ... from`. Note JSONDecodeError is itself a ValueError; the point
  is the message names the file.
- any other OSError (permission denied, path is a directory) propagates
  unchanged; do not catch OSError or Exception
- whenever the default is returned, return a deep copy (copy.deepcopy) so that
  a caller who mutates the result cannot corrupt the default that the next
  caller receives
- read with encoding="utf-8"; `path` may be a str or a pathlib.Path

Examples:
    >>> read_json_or_default("missing.json", {"devices": []})
    {'devices': []}
    >>> read_json_or_default("state.json", {})      # state.json: {"n": 1}
    {'n': 1}
    >>> read_json_or_default("broken.json", {})     # broken.json: {"n": 
    Traceback (most recent call last):
    ValueError: broken.json: invalid JSON (...)
"""
import copy
import json
from pathlib import Path
from typing import Any, Union


def read_json_or_default(path: Union[str, Path], default: Any) -> Any:
    raise NotImplementedError("write read_json_or_default")
