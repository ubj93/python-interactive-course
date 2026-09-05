"""Untimed practice rounds with independent attempts, reflections and drafts.

The JSON shape is shared with docs/practice.js. Unknown fields survive a round
trip; invalid known fields make a round unavailable rather than inventing results.
"""
from __future__ import annotations

import copy
import re
import uuid
from typing import Optional

from .timestamps import parse_timestamp, timestamp

DIAGNOSTIC_IDS = ("1.2", "1.3", "2.1", "2.2", "3.1", "5.1")
SESSION_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}")
CONFIDENCES = ("confident", "needs_review")
NOTE_LIMIT = 500


def new_practice(ids, kind: str, now=None) -> dict:
    state = {"version": 1, "id": uuid.uuid4().hex, "kind": kind,
             "started": timestamp(now), "ids": list(ids), "attempts": [],
             "reflections": {}, "drafts": {}, "last_exercise": None}
    if normalize_practice(state) is None:
        raise ValueError("Invalid practice round")
    return state


def normalize_practice(value) -> Optional[dict]:
    if not isinstance(value, dict) or type(value.get("version")) is not int or value["version"] != 1:
        return None
    if not isinstance(value.get("id"), str) or not SESSION_ID.fullmatch(value["id"]):
        return None
    if not isinstance(value.get("kind"), str) or not value["kind"]:
        return None
    ids = value.get("ids")
    if not isinstance(ids, list) or not ids or any(not isinstance(i, str) or not re.fullmatch(r"[0-9]+\.[0-9]+", i) for i in ids) or len(set(ids)) != len(ids):
        return None
    started = parse_timestamp(value.get("started"))
    if started is None or value.get("last_exercise") not in [None] + ids:
        return None
    attempts, reflections, drafts = value.get("attempts"), value.get("reflections"), value.get("drafts")
    if not isinstance(attempts, list) or not isinstance(reflections, dict) or not isinstance(drafts, dict):
        return None
    result = copy.deepcopy(value)
    result["started"] = timestamp(started)
    result["last_exercise"] = value.get("last_exercise")
    for attempt in result["attempts"]:
        if not isinstance(attempt, dict) or attempt.get("exercise_id") not in ids or type(attempt.get("passed")) is not bool:
            return None
        at = parse_timestamp(attempt.get("at"))
        if at is None or at < started:
            return None
        attempt["at"] = timestamp(at)
    for ex_id, reflection in result["reflections"].items():
        if ex_id not in ids or not isinstance(reflection, dict) or reflection.get("confidence") not in (None,) + CONFIDENCES:
            return None
        if not isinstance(reflection.get("mistake_note", ""), str) or len(reflection.get("mistake_note", "")) > NOTE_LIMIT:
            return None
        help_at = reflection.get("help_at")
        if help_at is not None:
            parsed = parse_timestamp(help_at)
            if parsed is None or parsed < started:
                return None
            reflection["help_at"] = timestamp(parsed)
    if any(ex_id not in ids or not isinstance(code, str) for ex_id, code in drafts.items()):
        return None
    return result


def normalize_diagnostic(value) -> Optional[dict]:
    state = normalize_practice(value)
    return state if state and state["kind"] == "diagnostic" and state["ids"] == list(DIAGNOSTIC_IDS) else None


def practice_summary(value) -> Optional[list]:
    state = normalize_practice(value)
    if state is None:
        return None
    rows = []
    for ex_id in state["ids"]:
        attempts = [a for a in state["attempts"] if a["exercise_id"] == ex_id]
        latest = max(enumerate(attempts), key=lambda pair: (pair[1]["at"], pair[0]))[1] if attempts else None
        reflection = state["reflections"].get(ex_id, {})
        rows.append({"id": ex_id, "outcome": "not_attempted" if latest is None else "passed" if latest["passed"] else "not_passed",
                     "attempts": len(attempts), "confidence": reflection.get("confidence"),
                     "mistake_note": reflection.get("mistake_note", ""), "help_used": bool(reflection.get("help_at"))})
    return rows


def diagnostic_summary(value) -> Optional[list]:
    state = normalize_diagnostic(value)
    return practice_summary(state) if state else None


def update_practice(value, ex_id, action, *, passed=None, confidence=None, note=None, code=None, now=None) -> dict:
    """Return a changed copy; a rejected action never mutates the original."""
    state = normalize_practice(value)
    if state is None or ex_id not in state["ids"]:
        raise ValueError("Invalid practice round or exercise")
    at = timestamp(now)
    if parse_timestamp(at) < parse_timestamp(state["started"]):
        raise ValueError("The clock is earlier than this practice round")
    if action == "attempt":
        if type(passed) is not bool:
            raise ValueError("A practice attempt needs a test outcome")
        state["attempts"].append({"exercise_id": ex_id, "at": at, "passed": passed})
    elif action == "reflect":
        if confidence not in (None,) + CONFIDENCES or not isinstance(note, str) or len(note) > NOTE_LIMIT:
            raise ValueError("Choose confident or needs-review and keep the note to 500 characters")
        reflection = state["reflections"].setdefault(ex_id, {})
        reflection.update(confidence=confidence, mistake_note=note)
    elif action == "help":
        reflection = state["reflections"].setdefault(ex_id, {})
        if not reflection.get("help_at"):
            reflection["help_at"] = at
    elif action not in ("open", "draft"):
        raise ValueError("Unknown practice action")
    if code is not None:
        if not isinstance(code, str):
            raise ValueError("The practice draft must be text")
        state["drafts"][ex_id] = code
    state["last_exercise"] = ex_id
    return state
