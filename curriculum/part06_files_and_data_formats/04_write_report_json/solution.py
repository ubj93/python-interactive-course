"""Reference solutions for write_report_json and read_report_json."""
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Union


# Best practice: one module-level `default` hook that knows the few types we care about
# and raises TypeError for the rest (json expects that, so unknown values still fail loudly).
def _to_json(value: Any) -> Any:
    if isinstance(value, (datetime, date)):      # datetime is a subclass of date
        return value.isoformat()
    if isinstance(value, set):
        return sorted(value)
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"cannot serialize {type(value).__name__}")


def write_report_json(path: Union[str, Path], report: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True, ensure_ascii=False, default=_to_json)
        f.write("\n")                             # json.dump never adds one


def read_report_json(path: Union[str, Path]) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# Clever: build the text with dumps and let Path.write_text handle the file. Same
# output, and easy to reuse when the destination is not a file (an HTTP body, a test).
def write_report_json_text(path: Union[str, Path], report: Any) -> None:
    text = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False, default=_to_json)
    Path(path).write_text(text + "\n", encoding="utf-8")


def read_report_json_text(path: Union[str, Path]) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))
