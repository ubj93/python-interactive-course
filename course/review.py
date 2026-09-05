"""One review queue and untimed reattempts, separate from lifetime achievement."""
from __future__ import annotations

import copy
import datetime as dt
import re

from .practice import CONFIDENCES, NOTE_LIMIT, new_practice, normalize_practice, update_practice
from .timestamps import local_day, timestamp

INTERVALS = (1, 3, 7, 30)


def queue_state(value=None) -> dict:
    if value is None:
        return {"version": 1, "items": {}}
    if not isinstance(value, dict) or type(value.get("version")) is not int or value["version"] != 1 or not isinstance(value.get("items"), dict):
        raise ValueError("Saved review queue is unsupported. Export a backup before repairing its review_queue field")
    result = copy.deepcopy(value)
    for ex_id, row in result["items"].items():
        if not isinstance(ex_id, str) or not re.fullmatch(r"[0-9]+\.[0-9]+", ex_id) or not isinstance(row, dict):
            raise ValueError("Invalid saved review item; keep a progress backup before repairing it")
        if row.get("confidence") not in CONFIDENCES or not isinstance(row.get("mistake_note"), str) or len(row["mistake_note"]) > NOTE_LIMIT:
            raise ValueError("Invalid saved review reflection; keep a progress backup before repairing it")
        if type(row.get("interval_days")) is not int or row["interval_days"] not in INTERVALS:
            raise ValueError("Invalid saved review interval")
        date = row.get("next_review")
        try:
            if not isinstance(date, str) or dt.date.fromisoformat(date).isoformat() != date:
                raise ValueError()
        except ValueError:
            raise ValueError("Invalid saved review date")
        if not isinstance(row.get("sources"), list) or any(not isinstance(source, str) for source in row["sources"]):
            raise ValueError("Invalid saved review sources")
    return result


def reflect_queue(value, ex_id, confidence, note, interval=None, source="exercise", now=None, preserve_schedule=False) -> dict:
    queue = queue_state(value)
    if not isinstance(ex_id, str) or not re.fullmatch(r"[0-9]+\.[0-9]+", ex_id):
        raise ValueError("Choose a course exercise")
    if confidence not in CONFIDENCES or not isinstance(note, str) or len(note) > NOTE_LIMIT:
        raise ValueError("Choose confident or needs-review and keep the note to 500 characters")
    row = queue["items"].get(ex_id, {})
    same_confidence = row.get("confidence") == confidence
    explicit_interval = interval is not None
    interval = (row["interval_days"] if same_confidence else 1 if confidence == "needs_review" else 3) if interval is None else interval
    if type(interval) is not int or interval not in INTERVALS:
        raise ValueError("Choose a review interval of 1, 3, 7 or 30 days")
    try:
        due = row["next_review"] if preserve_schedule and same_confidence and not explicit_interval else (dt.date.fromisoformat(local_day(now)) + dt.timedelta(days=interval)).isoformat()
    except (ValueError, OverflowError):
        raise ValueError("The next review date is outside the supported calendar")
    sources = row.get("sources", [])
    if source not in sources:
        sources.append(source)
    row.update(confidence=confidence, mistake_note=note, interval_days=interval,
               next_review=due, sources=sources, reflected_at=timestamp(now))
    queue["items"][ex_id] = row
    return queue


def queue_rows(value=None, today=None, due_only=False, available=None) -> list:
    queue = queue_state(value)
    today = today or local_day()
    rows = [{**row, "id": ex_id, "due": row["next_review"] <= today}
            for ex_id, row in queue["items"].items()
            if (available is None or ex_id in available) and (not due_only or row["next_review"] <= today)]
    return sorted(rows, key=lambda row: (not row["due"], row["confidence"] != "needs_review", row["next_review"], tuple(map(int, row["id"].split(".")))))


class ReviewProgress:
    """Persistence methods shared by the CLI and diagnostic reflection hook."""
    def _save_review(self, **fields):
        before = self.data
        self.data = {**before, **fields}
        try:
            self.save()
        except OSError:
            self.data = before
            raise

    def reflect_exercise(self, ex_id, confidence, note, interval=None, source="exercise", now=None):
        queue = reflect_queue(self.data.get("review_queue"), ex_id, confidence, note, interval, source, now)
        self._save_review(review_queue=queue)
        return copy.deepcopy(queue["items"][ex_id])

    def review_state(self):
        state = normalize_practice(self.data.get("review_session"))
        return state if state and state["kind"] == "review" else None

    def start_review(self, ids, new=False):
        raw, state = self.data.get("review_session"), self.review_state()
        if not new and raw is not None:
            if state is None:
                raise ValueError("Saved review round is invalid. Export it, or use `course review new` to archive it")
            return state
        state = new_practice(ids, "review")
        history = self.data.get("review_history", [])
        history = copy.deepcopy(history if isinstance(history, list) else [history])
        if raw is not None:
            history.append(copy.deepcopy(raw))
        self._save_review(review_session=state, review_history=history)
        return copy.deepcopy(state)

    def update_review(self, ex_id, action, session_id, interval=None, **fields):
        state = self.review_state()
        if state is None or state["id"] != session_id:
            raise ValueError("The review round changed; this result was not added to another round")
        state = update_practice(state, ex_id, action, **fields)
        updates = {"review_session": state}
        if action == "reflect":
            updates["review_queue"] = reflect_queue(self.data.get("review_queue"), ex_id,
                fields.get("confidence"), fields.get("note"), interval, "review", fields.get("now"))
            state["reflections"][ex_id]["interval_days"] = updates["review_queue"]["items"][ex_id]["interval_days"]
        self._save_review(**updates)
        return copy.deepcopy(state)

    def finish_review(self):
        state = self.review_state()
        if state is None:
            raise ValueError("There is no supported review round to finish")
        history = self.data.get("review_history", [])
        history = copy.deepcopy(history if isinstance(history, list) else [history])
        history.append(state)
        self._save_review(review_session=None, review_history=history)
        return state
