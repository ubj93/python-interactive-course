"""Curated, explicitly completed activities; independent of course mastery and XP."""
from __future__ import annotations

import copy
import json
from pathlib import Path

from .timestamps import timestamp
from .practice import diagnostic_summary


def catalog() -> dict:
    return json.loads(Path(__file__).with_name("refresher.json").read_text(encoding="utf-8"))


def activities() -> list:
    return [activity for session in catalog()["sessions"] for activity in session["activities"]]


def state(value=None) -> dict:
    """Read a copy without changing progress or inferring completion from results."""
    ids = [activity["id"] for activity in activities()]
    if value is None:
        return {"version": 1, "path_id": "interview-refresher", "next_activity": ids[0], "activities": {}, "mock_sessions": {}}
    if not isinstance(value, dict) or type(value.get("version")) is not int or value.get("version") != 1 or value.get("path_id") != "interview-refresher" or not isinstance(value.get("activities"), dict):
        raise ValueError("The saved refresher path is not supported. Keep a backup before repairing or replacing its refresher field.")
    result = copy.deepcopy(value)
    result.setdefault("mock_sessions", {})
    if not isinstance(result["mock_sessions"], dict):
        raise ValueError("The saved refresher mock links are invalid. Keep a backup before repairing them.")
    pending = [id for id in ids if status(result, id) == "pending"]
    if result.get("next_activity") not in pending:
        result["next_activity"] = pending[0] if pending else None
    return result


def status(saved: dict, id: str) -> str:
    item = saved["activities"].get(id)
    return item.get("status") if isinstance(item, dict) and item.get("status") in ("done", "skipped") else "pending"


def update(value, action: str, id: str = None, note: str = None) -> dict:
    saved = state(value)
    ids = [activity["id"] for activity in activities()]
    id = id or saved["next_activity"]
    if id not in ids:
        raise ValueError("Choose an activity ID from `course refresher list`.")
    if action not in ("open", "done", "skip", "revisit", "note"):
        raise ValueError("Choose open, done, skip, revisit or note.")
    item = saved["activities"].get(id)
    item = dict(item) if isinstance(item, dict) else {}
    item["updated_at"] = timestamp()
    if action == "note":
        item["note"] = str(note or "")
    elif action in ("done", "skip", "revisit"):
        item["status"] = {"done": "done", "skip": "skipped", "revisit": "pending"}[action]
    saved["activities"][id] = item
    if action in ("open", "revisit") and status(saved, id) == "pending":
        saved["next_activity"] = id
    elif action in ("done", "skip"):
        after = ids.index(id) + 1
        saved["next_activity"] = next((candidate for candidate in ids[after:] + ids[:after] if status(saved, candidate) == "pending"), None)
    return saved


def weak_areas(diagnostic) -> list:
    """Suggest lessons from the validated diagnostic's latest outcomes and reports."""
    results = diagnostic_summary(diagnostic)
    if results is None:
        return []
    lessons_by_id = catalog()["diagnostic_lessons"]
    rows = []
    for result in results:
        id = result["id"]
        if id not in lessons_by_id:
            continue
        reasons = []
        if result["outcome"] == "not_passed":
            reasons.append("Latest diagnostic run did not pass")
        if result["confidence"] == "needs_review":
            reasons.append("You marked this for review")
        if result["help_used"]:
            reasons.append("You used diagnostic help")
        note = result["mistake_note"].strip()
        if note:
            reasons.append("You recorded a mistake note")
        if reasons:
            rows.append({"id": id, "lessons": lessons_by_id[id], "reasons": reasons, "note": note})
    return rows
