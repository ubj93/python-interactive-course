"""Portable browser backup envelopes and validation shared by CLI import paths.

The CLI changes nested progress while retaining browser drafts and unknown
metadata. Draft keys are opaque storage identifiers, never filesystem paths.
"""
from __future__ import annotations

import copy
import datetime as dt
import math
import re

from .timestamps import parse_timestamp

FORMAT = "python-cpe-course-backup"
VERSION = 1
DRAFT_PREFIX = "cpe-course-draft:"
MAX_SAFE_INTEGER = 9007199254740991
_ENVELOPE_FIELDS = frozenset(("format", "progress", "drafts", "exported_at"))


def _number(value) -> bool:
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _counter(value) -> bool:
    return _number(value) and 0 <= value <= MAX_SAFE_INTEGER and int(value) == value


def _json_value(value) -> None:
    """Reject values that JSON writers would lose or silently turn into null."""
    if value is None or isinstance(value, (str, bool)):
        return
    if type(value) in (int, float):
        if not _number(value):
            raise ValueError("Backup numbers must be finite")
    elif isinstance(value, list):
        for item in value:
            _json_value(item)
    elif isinstance(value, dict) and all(isinstance(key, str) for key in value):
        for item in value.values():
            _json_value(item)
    else:
        raise ValueError("Backup fields must contain JSON values")


def _day(value) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        return False
    try:
        dt.date.fromisoformat(value)
        return True
    except ValueError:
        return False


def validate_progress(value, allow_partial=False) -> None:
    if not isinstance(value, dict):
        raise ValueError("Invalid progress data: expected a JSON object")
    if "xp" not in value and not allow_partial:
        raise ValueError("Progress must include xp")
    if "xp" in value and (not _number(value["xp"]) or not 0 <= value["xp"] <= MAX_SAFE_INTEGER):
        raise ValueError("Progress xp must be a nonnegative finite number within the safe range")
    if "version" in value and (not _counter(value["version"]) or value["version"] != 1):
        raise ValueError("Unsupported progress version")
    maps = ("solved", "attempts", "hints", "opened", "badges", "daily", "cards", "card_reward_history")
    for name in maps:
        if name in value and not isinstance(value[name], dict):
            raise ValueError(f"Progress {name} must be an object")
    for name in ("solved", "daily", "cards"):
        if any(not isinstance(item, dict) for item in value.get(name, {}).values()):
            raise ValueError(f"Progress {name} entries must be objects")
    for name in ("attempts", "hints"):
        if any(not _counter(item) for item in value.get(name, {}).values()):
            raise ValueError(f"Progress {name} counters must be nonnegative safe integers")
    # Invalid opened timestamps, including nonstrings, are kept as opaque JSON;
    # elapsed-time parsing treats them as unknown and withholds timing bonuses.
    for name in ("badges",):
        if any(not isinstance(item, str) for item in value.get(name, {}).values()):
            raise ValueError(f"Progress {name} entries must be strings")
    if any(type(item) is not bool for item in value.get("card_reward_history", {}).values()):
        raise ValueError("Card reward history entries must be booleans")
    for item in value.get("solved", {}).values():
        if "xp" in item and (not _number(item["xp"]) or not 0 <= item["xp"] <= MAX_SAFE_INTEGER):
            raise ValueError("Solved exercise xp must be nonnegative and finite")
    for item in value.get("cards", {}).values():
        if "tries" in item and not _counter(item["tries"]):
            raise ValueError("Card tries must be a nonnegative safe integer")
        if "done" in item and type(item["done"]) is not bool:
            raise ValueError("Card done must be a boolean")
        if "correct" in item and item["correct"] is not None and type(item["correct"]) is not bool:
            raise ValueError("Card correct must be a boolean or null")
    for item in value.get("daily", {}).values():
        if "done" in item and type(item["done"]) is not bool:
            raise ValueError("Daily done must be a boolean")
        if "id" in item and not isinstance(item["id"], str):
            raise ValueError("Daily exercise ID must be a string")
    if "days" in value and (not isinstance(value["days"], list) or any(not _day(day) for day in value["days"])):
        raise ValueError("Progress days must be an array of valid YYYY-MM-DD dates")
    if "peeked" in value and (not isinstance(value["peeked"], list) or any(not isinstance(item, str) for item in value["peeked"])):
        raise ValueError("Progress peeked must be an array of strings")
    for name in ("last", "last_lesson"):
        if name in value and value[name] is not None and not isinstance(value[name], str):
            raise ValueError(f"Progress {name} must be a string or null")


def unpack_progress_document(value, allow_partial_legacy=False) -> tuple:
    """Return independent (progress, envelope-or-None) copies after validation."""
    _json_value(value)
    if not isinstance(value, dict):
        raise ValueError("Invalid progress data: expected a JSON object")
    if not _ENVELOPE_FIELDS.intersection(value):
        validate_progress(value, allow_partial=allow_partial_legacy)
        return copy.deepcopy(value), None
    if value.get("format") != FORMAT or not _counter(value.get("version")) or value["version"] != VERSION:
        raise ValueError("Unsupported browser backup format or version")
    if parse_timestamp(value.get("exported_at")) is None:
        raise ValueError("Browser backup exported_at must be a valid timestamp")
    validate_progress(value.get("progress"))
    drafts = value.get("drafts")
    if not isinstance(drafts, dict) or any(not key.startswith(DRAFT_PREFIX) or len(key) == len(DRAFT_PREFIX) or not isinstance(code, str) for key, code in drafts.items()):
        raise ValueError("Browser backup drafts must map cpe-course-draft: identifiers to text")
    return copy.deepcopy(value["progress"]), copy.deepcopy(value)


def pack_progress_document(progress, wrapper=None) -> dict:
    """Replace only nested progress; leave browser drafts and metadata intact."""
    document = copy.deepcopy(progress) if wrapper is None else {**copy.deepcopy(wrapper), "progress": copy.deepcopy(progress)}
    unpack_progress_document(document, allow_partial_legacy=True)
    return document
