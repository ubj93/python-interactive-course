"""Learner progress: XP, ranks, streaks, badges. Persisted as one JSON file."""
from __future__ import annotations

import datetime as dt
import json
import math
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .catalog import ROOT, Exercise, Part
from .timestamps import elapsed_seconds, local_day, timestamp, timestamp_day, utc_now
from .sessions import finish_session, new_session, normalize_session, record_attempt

DEFAULT_PATH = ROOT / ".course_progress.json"

# (fraction of total course XP, kyu rank, title). Codewars-style kyu: 8 is lowest.
RANKS: List[Tuple[float, int, str]] = [
    (0.00, 8, "Help Desk"),
    (0.04, 7, "Ticket Closer"),
    (0.12, 6, "Script Writer"),
    (0.25, 5, "Fleet Wrangler"),
    (0.42, 4, "Automation Engineer"),
    (0.62, 3, "Platform Engineer"),
    (0.82, 2, "Staff CPE"),
    (1.00, 1, "Principal CPE"),
]

BADGES: Dict[str, Tuple[str, str]] = {
    "first_blood": ("🩸", "Passed your first exercise"),
    "hat_trick": ("🎩", "Passed 3 exercises in one day"),
    "clean_sweep": ("🧹", "Passed 10 exercises without using a hint"),
    "first_try": ("🎯", "Passed 5 exercises on the first attempt"),
    "comeback": ("💪", "Passed an exercise after 3 or more failed attempts"),
    "speed_demon": ("⚡", "Passed a 5-kyu-or-harder exercise inside its time limit"),
    "week_streak": ("🔥", "Practised 7 days in a row"),
    "month_streak": ("🌋", "Practised 30 days in a row"),
    "daily_5": ("📅", "Completed 5 daily katas"),
    "interviewer": ("🎤", "Finished a mock interview with every problem passing"),
    "graduate": ("🎓", "Completed every exercise in the course"),
}


def _today() -> str:
    return local_day()


def _now() -> str:
    return timestamp()


class Progress:
    def __init__(self, path: Optional[Path] = None):
        env = os.environ.get("COURSE_PROGRESS")
        self.path = Path(path or env or DEFAULT_PATH)
        self.data = {
            "version": 1,
            "xp": 0,
            "solved": {},      # id -> {passed_at, attempts, hints, seconds, xp}
            "attempts": {},    # id -> int
            "hints": {},       # id -> int hints revealed
            "opened": {},      # id -> iso timestamp of first open
            "peeked": [],      # ids whose solution was shown before passing
            "days": [],        # iso dates with at least one test run
            "badges": {},      # name -> iso date earned
            "daily": {},       # date -> {"id": .., "done": bool}
            "interview": None, # {"ids": [...], "started": iso, "deadline": iso}
            "last_interview": None, # frozen result of the most recently finished round
            "last": None,      # last exercise id touched
            "cards": {},       # "lesson_id:card_index" -> {"done": bool, "correct": bool|None, "tries": int}
            "last_lesson": None,
        }
        self.load()

    # ---- persistence -------------------------------------------------
    def load(self) -> None:
        if self.path.exists():
            try:
                self.data.update(json.loads(self.path.read_text(encoding="utf-8")))
            except json.JSONDecodeError:
                pass
        session = normalize_session(self.data.get("interview"))
        if session is not None:
            self.data["interview"] = session

    def save(self) -> None:
        self.path.write_text(json.dumps(self.data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # ---- queries -----------------------------------------------------
    @property
    def xp(self) -> int:
        return int(self.data["xp"])

    def is_solved(self, ex_id: str) -> bool:
        return ex_id in self.data["solved"]

    def attempts(self, ex_id: str) -> int:
        return int(self.data["attempts"].get(ex_id, 0))

    def hints_used(self, ex_id: str) -> int:
        return int(self.data["hints"].get(ex_id, 0))

    def peeked(self, ex_id: str) -> bool:
        return ex_id in self.data["peeked"]

    def rank(self, total_xp: int) -> Tuple[int, str, float, Optional[int]]:
        """Return (kyu, title, fraction_of_course, xp_needed_for_next_rank)."""
        frac = self.xp / total_xp if total_xp else 0.0
        current = RANKS[0]
        nxt = None
        for i, r in enumerate(RANKS):
            if frac >= r[0] - 1e-9:
                current = r
                nxt = RANKS[i + 1] if i + 1 < len(RANKS) else None
        need = None
        if nxt is not None:
            need = max(0, math.ceil(nxt[0] * total_xp) - self.xp)
        return current[1], current[2], frac, need

    def streak(self) -> int:
        days = sorted(set(self.data["days"]))
        if not days:
            return 0
        today = dt.date.fromisoformat(_today())
        last = dt.date.fromisoformat(days[-1])
        if (today - last).days > 1:
            return 0
        streak = 1
        for a, b in zip(reversed(days[:-1]), reversed(days[1:])):
            if (dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days == 1:
                streak += 1
            else:
                break
        return streak

    def solved_today(self) -> int:
        today = _today()
        return sum(1 for s in self.data["solved"].values() if timestamp_day(s.get("passed_at")) == today)

    def part_stats(self, part: Part) -> Tuple[int, int, int, int]:
        """(solved_count, total_count, earned_xp, total_xp)"""
        solved = [e for e in part.exercises if self.is_solved(e.id)]
        return len(solved), len(part.exercises), sum(e.xp for e in solved), part.total_xp

    # ---- mutations ---------------------------------------------------
    def touch(self, ex: Exercise) -> None:
        self.data["opened"].setdefault(ex.id, _now())
        self.data["last"] = ex.id

    def reveal_hint(self, ex: Exercise) -> Optional[str]:
        n = self.hints_used(ex.id)
        if n >= len(ex.hints):
            return None
        self.data["hints"][ex.id] = n + 1
        self.touch(ex)
        self.save()
        return ex.hints[n]

    def mark_peeked(self, ex: Exercise) -> None:
        if not self.is_solved(ex.id) and ex.id not in self.data["peeked"]:
            self.data["peeked"].append(ex.id)
            self.save()

    def xp_for(self, ex: Exercise, attempts: int, hints: int, seconds: Optional[float], peeked: bool) -> Tuple[int, List[str]]:
        base = ex.xp
        mult = 1.0
        notes: List[str] = []
        if peeked:
            mult *= 0.1
            notes.append("solution peeked ×0.1")
        else:
            if attempts == 1:
                mult *= 1.25
                notes.append("first try ×1.25")
            if hints:
                penalty = max(0.25, 1.0 - 0.25 * hints)
                mult *= penalty
                notes.append(f"{hints} hint{'s' if hints > 1 else ''} ×{penalty:.2f}")
            if ex.time_limit_min and seconds is not None and 0 <= seconds <= ex.time_limit_min * 60:
                mult *= 1.1
                notes.append("inside time limit ×1.1")
        return max(1, int(round(base * mult))), notes

    def record_run(self, ex: Exercise, passed: bool) -> dict:
        """Record one test run. Returns a summary dict (xp gained, new badges...)."""
        self.touch(ex)
        now = utc_now()
        today = local_day(now)
        if today not in self.data["days"]:
            self.data["days"].append(today)
        self.data["attempts"][ex.id] = self.attempts(ex.id) + 1
        session = self.active_interview()
        if session is not None:
            record_attempt(session, ex.id, passed, now)
            self.data["interview"] = session
        summary = {"xp": 0, "notes": [], "new_badges": [], "already_solved": self.is_solved(ex.id), "daily_bonus": 0}
        if passed and not self.is_solved(ex.id):
            attempts = self.attempts(ex.id)
            hints = self.hints_used(ex.id)
            opened = self.data["opened"].get(ex.id)
            seconds = elapsed_seconds(opened, now)
            xp, notes = self.xp_for(ex, attempts, hints, seconds, self.peeked(ex.id))
            self.data["solved"][ex.id] = {
                "passed_at": timestamp(now),
                "attempts": attempts,
                "hints": hints,
                "seconds": int(seconds) if seconds is not None else None,
                "xp": xp,
            }
            self.data["xp"] = self.xp + xp
            summary["xp"] = xp
            summary["notes"] = notes
            daily = self.data["daily"].get(today)
            if daily and daily.get("id") == ex.id and not daily.get("done"):
                daily["done"] = True
                self.data["xp"] = self.xp + 5
                summary["daily_bonus"] = 5
            summary["new_badges"] = self._check_badges(ex, attempts, hints, seconds)
        self.save()
        return summary

    def active_interview(self) -> Optional[dict]:
        session = normalize_session(self.data.get("interview"))
        return session if session and session["kind"] == "interview" and session["status"] == "active" else None

    def start_interview(self, ids: list, minutes: int) -> dict:
        session = new_session(ids, minutes, now=utc_now())
        # Explicitly starting over retains a reviewable result of the old round.
        previous = self.active_interview()
        if previous and self.finish_interview() is None:
            raise ValueError("The current round cannot finish before its start or latest attempt. Check the device clock before starting another round.")
        self.data["interview"] = session
        self.save()
        return session

    def finish_interview(self) -> Optional[dict]:
        session = self.active_interview()
        finished = finish_session(session, utc_now()) if session else None
        if finished is None:
            return None
        self.data["last_interview"] = finished
        self.data["interview"] = None
        summary = finished["summary"]
        if summary["total"] and summary["on_time"] == summary["total"]:
            self._award("interviewer", [])
        self.save()
        return finished

    def _award(self, name: str, new: List[str]) -> None:
        if name not in self.data["badges"]:
            self.data["badges"][name] = _today()
            new.append(name)

    def _check_badges(self, ex: Exercise, attempts: int, hints: int, seconds: Optional[float]) -> List[str]:
        new: List[str] = []
        solved = self.data["solved"]
        self._award("first_blood", new)
        if self.solved_today() >= 3:
            self._award("hat_trick", new)
        if sum(1 for s in solved.values() if not s.get("hints")) >= 10:
            self._award("clean_sweep", new)
        if sum(1 for s in solved.values() if s.get("attempts") == 1) >= 5:
            self._award("first_try", new)
        if attempts >= 4:
            self._award("comeback", new)
        if ex.kyu <= 5 and ex.time_limit_min and seconds is not None and 0 <= seconds <= ex.time_limit_min * 60:
            self._award("speed_demon", new)
        st = self.streak()
        if st >= 7:
            self._award("week_streak", new)
        if st >= 30:
            self._award("month_streak", new)
        if sum(1 for d in self.data["daily"].values() if d.get("done")) >= 5:
            self._award("daily_5", new)
        return new

    def award_badge(self, name: str) -> bool:
        new: List[str] = []
        self._award(name, new)
        if new:
            self.save()
        return bool(new)

    def set_daily(self, ex_id: str) -> None:
        self.data["daily"][_today()] = {"id": ex_id, "done": False}
        self.save()

    def today_daily(self) -> Optional[dict]:
        return self.data["daily"].get(_today())

    # ---- guided lessons -------------------------------------------
    def card_state(self, lesson_id: str, idx: int) -> dict:
        return self.data.setdefault("cards", {}).get(f"{lesson_id}:{idx}", {"done": False, "correct": None, "tries": 0})

    def record_card(self, lesson_id: str, idx: int, checkable: bool, correct: Optional[bool] = None) -> int:
        """Mark a card as seen/answered. Returns xp awarded (only for a correct first try)."""
        key = f"{lesson_id}:{idx}"
        cards = self.data.setdefault("cards", {})
        state = cards.get(key, {"done": False, "correct": None, "tries": 0})
        xp = 0
        today = _today()
        if today not in self.data["days"]:
            self.data["days"].append(today)
        if checkable:
            state["tries"] = int(state.get("tries", 0)) + 1
            if correct and not state["done"]:
                if state["tries"] == 1:
                    xp = 1
                    self.data["xp"] = self.xp + xp
                state["done"] = True
                state["correct"] = True
            elif correct is False and not state["done"]:
                state["correct"] = False
                if state["tries"] >= 2:
                    state["done"] = True  # second miss: move on, no xp
        else:
            state["done"] = True
        cards[key] = state
        self.data["last_lesson"] = lesson_id
        self.save()
        return xp

    def lesson_progress(self, lesson) -> Tuple[int, int, bool]:
        """(cards_done, cards_total, complete) where complete also needs the lesson's exercises solved."""
        done = sum(1 for i in range(len(lesson.cards)) if self.card_state(lesson.id, i)["done"])
        ex_ok = all(self.is_solved(e) for e in lesson.exercise_ids)
        return done, len(lesson.cards), done == len(lesson.cards) and ex_ok

    def forget(self, ex_id: str) -> None:
        """Reset one exercise (keeps XP already earned)."""
        for key in ("attempts", "hints", "opened"):
            self.data[key].pop(ex_id, None)
        if ex_id in self.data["peeked"]:
            self.data["peeked"].remove(ex_id)
        self.save()
