"""Reference solutions for read_json_or_default."""
import copy
import json
from pathlib import Path
from typing import Any, Union


# Best practice: two small try blocks, one per failure mode. The open() try catches
# only FileNotFoundError so a permission error or a directory still surfaces; the
# json try translates the decode error into one that names the file.
def read_json_or_default(path: Union[str, Path], default: Any) -> Any:
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return copy.deepcopy(default)
    if not text.strip():
        return copy.deepcopy(default)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"{path}: invalid JSON ({e.msg} at line {e.lineno})") from e


# Clever: Path.read_text collapses open+read into one call; the shape is otherwise the
# same. Note it raises the same FileNotFoundError, so the except clause does not change.
def read_json_or_default_pathlib(path: Union[str, Path], default: Any) -> Any:
    p = Path(path)
    try:
        text = p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return copy.deepcopy(default)
    if not text.strip():
        return copy.deepcopy(default)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"{p}: invalid JSON ({e})") from e
