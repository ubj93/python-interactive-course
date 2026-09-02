"""Write and read a JSON report.

A compliance script builds a report as a nested dict and needs to save it in a
form that is stable under `diff` and readable by humans. Write two functions.

`write_report_json(path, report)` writes `report` to `path` as UTF-8 JSON:
- indent=2 and sort_keys=True so the file is pretty and deterministic
- ensure_ascii=False so "Zürich" is written as-is, not as "Z\\u00fcrich"
- exactly one newline at the end of the file
- values JSON cannot encode are converted with a `default=` function:
  datetime and date become their .isoformat() string, sets become sorted
  lists, pathlib.Path becomes str(path); anything else raises TypeError
- returns None; `path` may be a str or a pathlib.Path

`read_report_json(path)` reads the file back (UTF-8) with json.load and returns
the parsed object. A missing file raises FileNotFoundError.

Note the round-trip is lossy on purpose: the datetime comes back as a string and
the set as a list. That is what the tests expect.

Examples:
    >>> write_report_json("r.json", {"b": 1, "a": {"z": True, "y": None}})
    >>> print(open("r.json", encoding="utf-8").read(), end="")
    {
      "a": {
        "y": null,
        "z": true
      },
      "b": 1
    }
    >>> read_report_json("r.json")
    {'a': {'y': None, 'z': True}, 'b': 1}
"""
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Union


def write_report_json(path: Union[str, Path], report: Any) -> None:
    raise NotImplementedError("write write_report_json")


def read_report_json(path: Union[str, Path]) -> Any:
    raise NotImplementedError("write read_report_json")
