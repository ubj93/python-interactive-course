"""Portable practice sessions: selected exercises, attempt events and frozen results.

An attempt is scoped to one active session. Lifetime exercise progress is never a
source of session credit. The same record shape can support other practice modes.
"""
from __future__ import annotations

import copy
import datetime as dt
import math
import re
import uuid
from typing import Optional

from .timestamps import UTC, parse_timestamp, timestamp, utc_now


def _instant(value: object, legacy: bool = False) -> Optional[dt.datetime]:
    if legacy and isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            return dt.datetime.fromtimestamp(value / 1000, UTC) if math.isfinite(value) else None
        except (ValueError, OverflowError, OSError):
            return None
    return parse_timestamp(value)


def normalize_session(value: object) -> Optional[dict]:
    """Validate imported metadata without ever inferring attempts from solved state.

    Unknown fields survive migration. Invalid records return None; callers retain
    the original data so opening a report cannot silently erase a damaged session.
    """
    if not isinstance(value, dict):
        return None
    ids = value.get("ids")
    if not isinstance(ids, list) or not ids or any(not isinstance(i, str) or not re.fullmatch(r"[1-9]\d*\.[1-9]\d*", i) for i in ids):
        return None
    if len(set(ids)) != len(ids):
        return None
    legacy = "version" not in value and "attempts" not in value
    if not legacy and (isinstance(value.get("version"), bool) or value.get("version") != 1):
        return None
    started, deadline = _instant(value.get("started"), legacy), _instant(value.get("deadline"), legacy)
    if started is None or deadline is None or deadline <= started:
        return None
    status = value.get("status", "active")
    kind = value.get("kind", "interview")
    if status not in ("active", "finished") or not isinstance(kind, str) or not kind:
        return None
    finished = _instant(value.get("finished_at")) if status == "finished" else None
    if status == "finished" and (finished is None or finished < started):
        return None
    raw_attempts = [] if legacy else value.get("attempts")
    if not isinstance(raw_attempts, list):
        return None
    attempts = []
    for event in raw_attempts:
        if not isinstance(event, dict) or event.get("exercise_id") not in ids or type(event.get("passed")) is not bool:
            continue
        at = _instant(event.get("at"))
        if at is None or at < started or (finished is not None and at > finished):
            continue
        attempts.append({"exercise_id": event["exercise_id"], "at": timestamp(at), "passed": event["passed"]})
    result = copy.deepcopy(value)
    result.update(version=1, kind=kind, ids=list(ids), started=timestamp(started), deadline=timestamp(deadline), status=status, attempts=attempts)
    result["id"] = value.get("id") if isinstance(value.get("id"), str) and value["id"] else "legacy-" + result["started"]
    if legacy:
        result["legacy"] = True
    if finished is not None:
        result["finished_at"] = timestamp(finished)
    return result


def new_session(ids: list, minutes: int, kind: str = "interview", now: Optional[dt.datetime] = None) -> dict:
    try:
        valid_duration = not isinstance(minutes, bool) and isinstance(minutes, (int, float)) and math.isfinite(minutes) and minutes > 0
    except OverflowError:
        valid_duration = False
    if not valid_duration:
        raise ValueError("Choose a positive duration.")
    started = now if now is not None else utc_now()
    try:
        deadline = started + dt.timedelta(minutes=minutes)
        session = normalize_session({"version": 1, "id": uuid.uuid4().hex, "kind": kind, "ids": ids, "started": timestamp(started), "deadline": timestamp(deadline), "status": "active", "attempts": []})
    except (OverflowError, ValueError):
        session = None
    if session is None:
        raise ValueError("Choose available exercises and a valid duration.")
    return session


def record_attempt(session: dict, ex_id: str, passed: bool, now: Optional[dt.datetime] = None) -> bool:
    valid = normalize_session(session)
    at = now if now is not None else utc_now()
    if valid is None or valid["status"] != "active" or ex_id not in valid["ids"] or at < parse_timestamp(valid["started"]):
        return False
    session.update(valid)
    session["attempts"].append({"exercise_id": ex_id, "at": timestamp(at), "passed": bool(passed)})
    return True


def session_summary(session: dict) -> Optional[dict]:
    valid = normalize_session(session)
    if valid is None:
        return None
    deadline = parse_timestamp(valid["deadline"])
    rows = []
    for ex_id in valid["ids"]:
        events = [event for event in valid["attempts"] if event["exercise_id"] == ex_id]
        passes = [parse_timestamp(event["at"]) for event in events if event["passed"]]
        first = min(passes) if passes else None
        rows.append({"id": ex_id, "attempts": len(events), "passed_at": timestamp(first) if first is not None else None, "on_time": first is not None and first <= deadline})
    return {"total": len(rows), "passed": sum(row["passed_at"] is not None for row in rows), "on_time": sum(row["on_time"] for row in rows), "results": rows, "started": valid["started"], "deadline": valid["deadline"]}


def finish_session(session: dict, now: Optional[dt.datetime] = None) -> Optional[dict]:
    valid = normalize_session(session)
    if valid is None:
        return None
    if valid["status"] == "finished":
        return valid
    finished = now if now is not None else utc_now()
    latest = max([parse_timestamp(valid["started"])] + [parse_timestamp(event["at"]) for event in valid["attempts"]])
    if finished < latest:
        # A clock rollback must not erase recorded attempts while freezing results.
        return None
    # Freeze independent data; later practice or a new round cannot mutate it.
    valid.update(status="finished", finished_at=timestamp(finished))
    valid["summary"] = session_summary(valid)
    return valid
