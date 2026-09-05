"""Command-line interface: ``python -m course <command>`` (or ``./course.py``)."""
from __future__ import annotations

import argparse
import datetime as dt
import math
import random
import re
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from typing import List, Optional

from . import __version__, ui
from .catalog import ROOT, Exercise, Part, all_exercises, find_exercise, find_part, load_catalog, total_xp
from .progress import BADGES, RANKS, Progress
from . import backup as backup_mod
from .lessons import CARD_XP, Card, Lesson, find_lesson, load_all_lessons
from .runner import RunResult, run_code_card, run_learner
from .workspace import Workspace, recovery_copy
from .timestamps import parse_timestamp, utc_now
from .sessions import normalize_session, session_summary


class App:
    def __init__(self) -> None:
        self.catalog = load_catalog()
        self.workspace = Workspace()
        self.progress = Progress()
        self.lessons = load_all_lessons(self.catalog)
        self.total_xp = total_xp(self.catalog) + sum(l.xp for ls in self.lessons.values() for l in ls)

    # ------------------------------------------------------------ helpers
    def resolve(self, ref: Optional[str], *, record_selection: bool = True) -> Exercise:
        if ref in (None, "", "last"):
            ref = self.progress.data.get("last")
            if not ref:
                ref = "next"
        if ref == "next":
            ex = self.next_unsolved()
            if ex is None:
                self.die("Every exercise is solved. Run `course interview` for a fresh mock round.")
            return ex
        if ref == "daily":
            return self.daily_exercise(record_selection=record_selection)
        ex = find_exercise(self.catalog, ref)
        if ex is None:
            self.die(f"No exercise matches '{ref}'. Try `course list`.")
        return ex

    def next_unsolved(self, after: Optional[Exercise] = None) -> Optional[Exercise]:
        exs = all_exercises(self.catalog)
        start = 0
        if after is not None:
            for i, e in enumerate(exs):
                if e.id == after.id:
                    start = i + 1
                    break
        for e in exs[start:] + exs[:start]:
            if not self.progress.is_solved(e.id):
                return e
        return None

    @staticmethod
    def die(msg: str, code: int = 2) -> None:
        print(ui.red(msg), file=sys.stderr)
        raise SystemExit(code)

    def rel(self, p: Path) -> str:
        try:
            return str(p.relative_to(Path.cwd()))
        except ValueError:
            return str(p)

    def status_mark(self, ex: Exercise) -> str:
        if self.progress.is_solved(ex.id):
            return ui.green("✔")
        if self.progress.attempts(ex.id):
            return ui.yellow("…")
        return ui.dim("○")

    def ex_line(self, ex: Exercise, show_part: bool = True) -> str:
        kyu = ui.kyu_color(ex.kyu, f"{ex.kyu} kyu")
        xp = ui.dim(f"{ex.xp:>4} xp")
        tags = ui.dim(" ".join(f"#{t}" for t in ex.tags[:3]))
        return f"  {self.status_mark(ex)} {ex.id:<5} {ex.title:<34} {kyu:<8} {xp}  {tags}"

    # ------------------------------------------------------------ commands
    def cmd_status(self, args) -> int:
        p = self.progress
        kyu, title, frac, need = p.rank(self.total_xp)
        print(ui.heading(f"Python for Client Platform Engineering · v{__version__}"))
        print(f"  Rank     {ui.kyu_color(kyu, ui.bold(f'{kyu} kyu'))}  {ui.bold(title)}")
        print(f"  XP       {ui.bold(str(p.xp))} / {self.total_xp}   {ui.bar(frac)}  {frac*100:4.1f}%")
        if need:
            print(f"  Next     {ui.dim(f'{need} xp to reach the next rank')}")
        streak = p.streak()
        flame = "🔥" if streak else "  "
        print(f"  Streak   {flame} {streak} day{'s' if streak != 1 else ''}   {ui.dim(f'{p.solved_today()} solved today')}")
        solved = len(p.data["solved"])
        total = len(all_exercises(self.catalog))
        print(f"  Solved   {solved} / {total} exercises")
        badges = p.data["badges"]
        if badges:
            print("  Badges   " + " ".join(BADGES[b][0] for b in badges if b in BADGES) + ui.dim(f"  ({len(badges)}/{len(BADGES)})"))
        daily = p.today_daily()
        if daily:
            ex = find_exercise(self.catalog, daily["id"])
            if ex:
                mark = ui.green("done") if daily.get("done") else ui.yellow("open")
                print(f"  Daily    {ex.id} {ex.title} [{mark}]")
        print(ui.heading("Parts"))
        for part in self.catalog:
            s, t, exp, txp = p.part_stats(part)
            ls = self.lessons.get(part.num, [])
            ldone = sum(1 for l in ls if p.lesson_progress(l)[2])
            lbl = f"{ldone}/{len(ls)} lessons · {s}/{t} exercises"
            print(f"  {part.num:>2}. {part.title:<38} {ui.bar(ldone / len(ls) if ls else (s / t if t else 0), 14)} {lbl:<28} {ui.dim(f'{exp}/{txp} xp')}")
        print()
        lesson = self.next_lesson()
        if lesson:
            done, total, _ = self.progress.lesson_progress(lesson)
            where = f" (card {done + 1}/{total})" if done else ""
            print(f"  Continue learning: {ui.bold(f'Lesson {lesson.id}')} {lesson.title}{where}   →  {ui.cyan('course learn')}")
        nxt = self.next_unsolved()
        if nxt:
            print(f"  Next exercise:     {ui.bold(nxt.id)} {nxt.title}   →  {ui.cyan('course next')}")
        elif not lesson:
            print("  " + ui.green("Everything complete. 🎓"))
        print(ui.dim("  Commands: learn · list · show · run · hint · solution · lesson · daily · interview · watch · badges · backup"))
        return 0

    def cmd_list(self, args) -> int:
        parts: List[Part] = self.catalog
        if args.part:
            part = find_part(self.catalog, args.part)
            if part is None:
                self.die(f"No part '{args.part}'.")
            parts = [part]
        for part in parts:
            s, t, exp, txp = self.progress.part_stats(part)
            print(ui.heading(f"Part {part.num} · {part.title}   {s}/{t} solved · {exp}/{txp} xp"))
            for ex in part.exercises:
                if args.unsolved and self.progress.is_solved(ex.id):
                    continue
                print(self.ex_line(ex))
        print()
        return 0

    def cmd_show(self, args) -> int:
        ex = self.resolve(args.exercise)
        self.progress.touch(ex)
        self.progress.save()
        self.print_exercise(ex)
        return 0

    def print_exercise(self, ex: Exercise) -> None:
        part = next(p for p in self.catalog if p.num == ex.part_num)
        print(ui.heading(f"{ex.id} · {ex.title}"))
        meta = [ui.kyu_color(ex.kyu, f"{ex.kyu} kyu"), f"{ex.xp} xp", f"Part {part.num}: {part.title}"]
        if ex.time_limit_min:
            meta.append(f"⏱ {ex.time_limit_min} min")
        if ex.tags:
            meta.append(" ".join("#" + t for t in ex.tags))
        print("  " + ui.dim(" · ").join(meta))
        print()
        print(ui.wrap(ex.description()))
        print()
        hints = self.progress.hints_used(ex.id)
        print(f"  File   {ui.bold(self.rel(self.workspace.ensure(ex)))}")
        print(f"  Tests  {self.rel(ex.test_file)}")
        print(f"  Hints  {hints}/{len(ex.hints)} revealed   {ui.dim(f'course hint {ex.id}')}")
        print(f"  Run    {ui.cyan(f'course run {ex.id}')}   {ui.dim(f'or: course watch {ex.id}')}")
        for i in range(hints):
            print(ui.yellow(f"\n  Hint {i + 1}: ") + ex.hints[i])
        print()

    def cmd_next(self, args) -> int:
        ex = self.next_unsolved()
        if ex is None:
            print(ui.green("All exercises solved. Try `course interview`."))
            return 0
        self.progress.touch(ex)
        self.progress.save()
        self.print_exercise(ex)
        return 0

    def cmd_run(self, args) -> int:
        ex = self.resolve(args.exercise, record_selection=not args.scratch)
        return self.run_once(ex, verbose=args.verbose, scratch=args.scratch)

    def run_once(self, ex: Exercise, verbose: bool = False, scratch: bool = False) -> int:
        print(ui.heading(f"Running tests · {ex.id} {ex.title}"))
        t0 = time.time()
        answer = self.workspace.ensure(ex, scratch=scratch)
        res = run_learner(ex, self.workspace, answer)
        elapsed = time.time() - t0
        self.print_result(res, verbose=verbose)
        if scratch:
            label = f"All {res.total} tests passed" if res.ok else "Keep practising"
            print(ui.green(f"  {label}") if res.ok else ui.yellow(f"  {label}"))
            print(ui.dim("  Scratch practice: saved answers and progress are unchanged."))
            return 0 if res.ok else 1
        summary = self.progress.record_run(ex, res.ok)
        if res.ok:
            print(ui.green(ui.bold(f"\n  ✔ All {res.total} tests passed")) + ui.dim(f"  ({elapsed:.2f}s)"))
            if summary["already_solved"]:
                print(ui.dim("  Already solved earlier; no additional XP."))
            else:
                notes = f"  ({', '.join(summary['notes'])})" if summary["notes"] else ""
                print(ui.bold(ui.yellow(f"  +{summary['xp']} xp")) + ui.dim(notes))
                if summary["daily_bonus"]:
                    print(ui.yellow(f"  +{summary['daily_bonus']} xp daily kata bonus"))
                self.print_rank_change()
                for b in summary["new_badges"]:
                    icon, desc = BADGES[b]
                    print(ui.magenta(f"  {icon} Badge unlocked: {desc}"))
                if self.all_solved():
                    if self.progress.award_badge("graduate"):
                        print(ui.magenta("  🎓 Badge unlocked: completed the whole course"))
            print(f"\n  Compare with reference solutions:  {ui.cyan(f'course solution {ex.id}')}")
            nxt = self.next_unsolved(after=ex)
            if nxt:
                print(f"  Next up: {ui.bold(nxt.id)} {nxt.title}   →  {ui.cyan(f'course show {nxt.id}')}")
            return 0
        failed = res.total - res.passed
        print(ui.red(ui.bold(f"\n  ✘ {res.passed}/{res.total} tests passed")) + ui.dim(f"  ({elapsed:.2f}s, attempt {self.progress.attempts(ex.id)})"))
        remaining = len(ex.hints) - self.progress.hints_used(ex.id)
        if remaining:
            print(ui.dim(f"  Stuck? {remaining} hint{'s' if remaining > 1 else ''} available: course hint {ex.id}"))
        return 1

    def print_result(self, res: RunResult, verbose: bool = False) -> None:
        if res.timed_out:
            print(ui.red("  ⏱ Timed out. Infinite loop? Each run is limited to a few seconds."))
            return
        if res.crashed:
            print(ui.red("  Harness crashed:\n") + res.crashed)
            return
        if res.import_error:
            print(ui.red("  Your exercise.py could not be imported:\n"))
            print(_indent(_short_tb(res.import_error)))
            return
        if not res.tests:
            print(ui.yellow("  No tests found."))
            return
        for t in res.tests:
            label = t.doc or t.name
            print(f"  {ui.status_icon(t.status)} {label}")
            if t.status in ("fail", "error"):
                msg = t.traceback if verbose else _short_tb(t.traceback or t.message)
                print(_indent(msg, "      "))
        if res.stdout.strip():
            print(ui.dim("\n  ── your output ──"))
            print(_indent(res.stdout.rstrip(), "  │ "))

    def print_rank_change(self) -> None:
        kyu, title, frac, need = self.progress.rank(self.total_xp)
        prev_xp = self.progress.xp - self.progress.data["solved"][self.progress.data["last"]]["xp"]
        prev_kyu = RANKS[0][1]
        for f, k, _ in RANKS:
            if (prev_xp / self.total_xp if self.total_xp else 0) >= f - 1e-9:
                prev_kyu = k
        if kyu < prev_kyu:
            print(ui.magenta(ui.bold(f"  ★ Rank up! You are now {kyu} kyu · {title}")))
        elif need:
            print(ui.dim(f"  {need} xp to the next rank"))

    def all_solved(self) -> bool:
        return all(self.progress.is_solved(e.id) for e in all_exercises(self.catalog))

    def cmd_watch(self, args) -> int:
        ex = self.resolve(args.exercise)
        self.progress.touch(ex)
        self.progress.save()
        answer = self.workspace.ensure(ex)
        print(ui.dim(f"Watching {self.rel(answer)} — save the file to re-run. Ctrl-C to stop."))
        last = answer.stat().st_mtime_ns
        try:
            while True:
                try:
                    mtime = answer.stat().st_mtime_ns
                except OSError:
                    mtime = None
                if mtime != last:
                    last = mtime
                    print("\033[2J\033[H" if sys.stdout.isatty() else "")
                    if self.run_once(ex) == 0 and args.exit_on_pass:
                        return 0
                time.sleep(0.5)
        except KeyboardInterrupt:
            print()
            return 0

    def cmd_hint(self, args) -> int:
        ex = self.resolve(args.exercise)
        if not ex.hints:
            print("No hints for this exercise.")
            return 0
        used = self.progress.hints_used(ex.id)
        for i in range(used):
            print(ui.yellow(f"  Hint {i + 1}: ") + ex.hints[i])
        if self.progress.is_solved(ex.id):
            for i in range(used, len(ex.hints)):
                print(ui.yellow(f"  Hint {i + 1}: ") + ex.hints[i])
            return 0
        hint = self.progress.reveal_hint(ex)
        if hint is None:
            print(ui.dim("  No more hints. Read the tests: they are the spec."))
        else:
            print(ui.yellow(f"  Hint {used + 1}: ") + hint)
            left = len(ex.hints) - used - 1
            print(ui.dim(f"  ({left} left · each hint reduces the XP for this exercise by 25%)"))
        return 0

    def cmd_solution(self, args) -> int:
        ex = self.resolve(args.exercise)
        if not self.progress.is_solved(ex.id):
            if not args.force:
                print(ui.yellow(f"  {ex.id} is not solved yet. Peeking now cuts its XP to 10%."))
                print(ui.dim(f"  If you really want it: course solution {ex.id} --force"))
                return 1
            self.progress.mark_peeked(ex)
        print(ui.heading(f"Reference solutions · {ex.id} {ex.title}"))
        print(ui.dim(f"  {self.rel(ex.solution_file)}\n"))
        print(ex.solution_file.read_text(encoding="utf-8"))
        return 0

    def cmd_lesson(self, args) -> int:
        part = find_part(self.catalog, args.part) if args.part else None
        if args.part and part is None:
            self.die(f"No part '{args.part}'.")
        if part is None:
            nxt = self.next_unsolved()
            part = next(p for p in self.catalog if p.num == (nxt.part_num if nxt else self.catalog[-1].num))
        text = part.lesson_file.read_text(encoding="utf-8")
        ui.page(text + f"\n\nExercises: course list {part.num}\n")
        return 0

    def cmd_reset(self, args) -> int:
        ex = self.resolve(args.exercise, record_selection=not args.scratch)
        path, saved = self.workspace.reset(ex, scratch=args.scratch)
        if not args.scratch:
            if self.progress.path.exists():
                progress_copy = recovery_copy(self.progress.path)
                print(ui.dim(f"  Previous progress saved to {progress_copy}"))
            self.progress.forget(ex.id)
        print(ui.green(f"  Restored {self.rel(path)} to the original starter."))
        if saved:
            print(ui.dim(f"  Previous answer saved to {saved}"))
        return 0

    def cmd_migrate_answers(self, args) -> int:
        selected = [self.resolve(args.exercise)] if args.exercise else all_exercises(self.catalog)
        candidates = [ex for ex in self.workspace.legacy_answers(self.catalog) if ex in selected]
        if args.restore_starters and not args.apply:
            self.die("Use --apply with --restore-starters after reviewing the migration preview.")
        if not candidates:
            print("No uncommitted curriculum answer candidates found. Migration requires git history.")
            return 0
        print("Local curriculum changes may be learner answers or author edits. Review them before applying:")
        for ex in candidates:
            print(f"  {ex.id}: {ex.exercise_file} → {self.workspace.answer_path(ex)}")
        if not args.apply:
            print("Preview only. Use --apply to copy these edits; add --restore-starters to restore their committed starters.")
            return 0
        result = self.workspace.migrate(candidates, restore_starters=args.restore_starters)
        for path in result["copied"]:
            print(ui.green(f"  Copied answer → {path}"))
        for path in result["conflicts"]:
            print(ui.yellow(f"  Existing answer preserved → {path}"))
        for path in result["recoveries"]:
            print(f"  Legacy recovery copy → {path}")
        for path in result["restored"]:
            print(f"  Restored committed starter → {path}")
        return 0

    def daily_exercise(self, *, record_selection: bool = True) -> Exercise:
        today = self.progress.today_daily()
        if today:
            ex = find_exercise(self.catalog, today["id"])
            if ex:
                return ex
        pool = [e for e in all_exercises(self.catalog) if not self.progress.is_solved(e.id)]
        if not pool:
            pool = all_exercises(self.catalog)
        # Prefer exercises near the learner's frontier: the earliest unsolved part and the next one.
        frontier = min(e.part_num for e in pool)
        near = [e for e in pool if e.part_num in (frontier, frontier + 1)]
        rng = random.Random(dt.date.today().isoformat())
        ex = rng.choice(near or pool)
        if record_selection:
            self.progress.set_daily(ex.id)
        return ex

    def cmd_daily(self, args) -> int:
        ex = self.daily_exercise()
        self.progress.touch(ex)
        self.progress.save()
        d = self.progress.today_daily() or {}
        state = ui.green("done ✔") if d.get("done") else ui.yellow("open · +5 xp bonus when passed")
        print(ui.heading(f"Daily kata · {dt.date.today():%A %d %B}  [{state}]"))
        self.print_exercise(ex)
        return 0

    def cmd_interview(self, args) -> int:
        p = self.progress
        if getattr(args, "last", False):
            if args.finish or args.new:
                print("Use --last by itself to review the previous result.")
                return 2
            recent = normalize_session(p.data.get("last_interview"))
            if recent and recent["status"] == "finished":
                return self.report_interview(recent, final=False)
            print("No saved interview result yet. Finish a round with `course interview --finish`.")
            return 0
        if args.finish and args.new:
            print("Choose either --finish or --new.")
            return 2
        if not args.new:
            session = p.active_interview()
            if session:
                return self.report_interview(session, final=args.finish)
            if p.data.get("interview") is not None:
                return self.report_interview(p.data["interview"], final=False)
            recent = normalize_session(p.data.get("last_interview"))
            if recent and recent["status"] == "finished":
                return self.report_interview(recent, final=False)
            if args.finish:
                print("No mock interview in progress. Start one with `course interview`.")
                return 0
        if args.count <= 0 or args.minutes <= 0:
            print("Choose a positive problem count and duration.")
            return 2
        exs = [e for e in all_exercises(self.catalog) if e.part_num >= args.min_part and not p.is_solved(e.id)]
        if len(exs) < args.count:
            exs = [e for e in all_exercises(self.catalog) if e.part_num >= args.min_part]
        if not exs:
            print("No exercises match this round. Choose an earlier --min-part.")
            return 2
        rng = random.Random()
        picks = rng.sample(exs, min(args.count, len(exs)))
        picks.sort(key=lambda e: (-e.kyu, e.part_num, e.num))
        try:
            session = p.start_interview([e.id for e in picks], args.minutes)
        except ValueError as error:
            print(str(error))
            return 2
        print(ui.heading(f"Mock interview · {len(picks)} problems · {args.minutes} minutes"))
        print("  Talk out loud, state assumptions, write the brute force first, then improve it.\n")
        for e in picks:
            print(f"  ○ {e.id:<5} {e.title} · awaiting a fresh passing attempt")
        print(f"\n  Deadline {ui.bold(_local_time(session['deadline'], '%H:%M'))}.  Work them with `course show <id>` / `course run <id>`.")
        print(f"  Check the clock with {ui.cyan('course interview')}, finish with {ui.cyan('course interview --finish')}.")
        return 0

    def report_interview(self, session: dict, final: bool) -> int:
        p = self.progress
        session = normalize_session(session)
        if session is None or session["kind"] != "interview":
            print("This mock interview has invalid saved data. Start a new round with `course interview --new`.")
            return 1
        had_badge = "interviewer" in p.data["badges"]
        if final and session["status"] == "active":
            active = p.active_interview()
            if active is None or active["id"] != session["id"]:
                print("This round is no longer active. Run `course interview` to see the current round.")
                return 1
            session = p.finish_interview()
            if session is None:
                print("This round cannot finish before its start or latest attempt. Check the device clock.")
                return 1
        summary = session_summary(session)
        finished = session["status"] == "finished"
        print(ui.heading("Mock interview · results" if finished else "Mock interview"))
        if session.get("legacy"):
            print("  This older round did not save session attempts. Only fresh runs since migration count.\n")
        for row in summary["results"]:
            ex = find_exercise(self.catalog, row["id"])
            title = ex.title if ex else "Exercise unavailable in this catalog"
            state = "passed on time" if row["on_time"] else "passed late" if row["passed_at"] else "not passed"
            mark = "✔" if row["passed_at"] else "…" if row["attempts"] else "○"
            print(f"  {mark} {row['id']:<5} {title} · {row['attempts']} attempt(s) · {state}")
        print(f"\n  Result: {summary['passed']}/{summary['total']} passed · {summary['on_time']}/{summary['total']} on time")
        if finished:
            when = _local_time(session["finished_at"], "%Y-%m-%d %H:%M:%S %Z")
            print(f"  Finished {when}. This result is saved; start another with `course interview --new`.")
        else:
            seconds = (parse_timestamp(session["deadline"]) - utc_now()).total_seconds()
            print(f"  ⏱ {math.ceil(seconds / 60)} min left" if seconds > 0 else "  ⏱ Time is up. Later passes are recorded as late.")
            print("  Finish and save this result with `course interview --finish`.")
        if not had_badge and "interviewer" in p.data["badges"]:
            print(ui.magenta("  🎤 Badge unlocked: aced a mock interview"))
        return 0

    def cmd_badges(self, args) -> int:
        print(ui.heading("Badges"))
        earned = self.progress.data["badges"]
        for name, (icon, desc) in BADGES.items():
            when = earned.get(name)
            mark = ui.green(f"{icon} {desc}") + ui.dim(f"  ({when})") if when else ui.dim(f"🔒 {desc}")
            print("  " + mark)
        print()
        return 0

    def cmd_repl(self, args) -> int:
        ex = self.resolve(args.exercise)
        print(ui.dim(f"Interactive Python with {self.rel(self.workspace.ensure(ex))} loaded. exit() to leave."))
        with self.workspace.grading_copy(ex) as candidate:
            return subprocess.call([sys.executable, "-i", str(candidate.exercise_file)], cwd=str(candidate.dir))

    # ------------------------------------------------------------ guided lessons
    def all_lessons(self) -> List[Lesson]:
        return [l for p in self.catalog for l in self.lessons.get(p.num, [])]

    def next_lesson(self, after: Optional[Lesson] = None) -> Optional[Lesson]:
        ls = self.all_lessons()
        start = 0
        if after is not None:
            for i, l in enumerate(ls):
                if l.id == after.id:
                    start = i + 1
                    break
        for l in ls[start:]:
            if not self.progress.lesson_progress(l)[2]:
                return l
        return None

    def resolve_lesson(self, ref: Optional[str]) -> Lesson:
        if ref in (None, "", "next"):
            last = self.progress.data.get("last_lesson")
            if last:
                l = find_lesson(self.lessons, last)
                if l and not self.progress.lesson_progress(l)[2]:
                    return l
            l = self.next_lesson()
            if l is None:
                self.die("Every lesson is complete. Try `course interview` or `course daily`.")
            return l
        l = find_lesson(self.lessons, ref)
        if l is None:
            part = find_part(self.catalog, ref)
            if part and self.lessons.get(part.num):
                for cand in self.lessons[part.num]:
                    if not self.progress.lesson_progress(cand)[2]:
                        return cand
                return self.lessons[part.num][0]
            self.die(f"No lesson matches '{ref}'. Try `course learn --list`.")
        return l

    def cmd_learn(self, args) -> int:
        if args.list:
            return self.list_lessons()
        lesson = self.resolve_lesson(args.lesson)
        part = next(p for p in self.catalog if p.num == lesson.part_num)
        if args.show:
            self.print_lesson_static(lesson)
            return 0
        if not sys.stdin.isatty():
            self.print_lesson_static(lesson)
            return 0
        return self.run_lesson(lesson, part, restart=args.restart)

    def list_lessons(self) -> int:
        for part in self.catalog:
            ls = self.lessons.get(part.num, [])
            if not ls:
                continue
            print(ui.heading(f"Part {part.num} · {part.title}"))
            for l in ls:
                done, total, complete = self.progress.lesson_progress(l)
                mark = ui.green("✔") if complete else (ui.yellow("…") if done else ui.dim("○"))
                ex = ", ".join(l.exercise_ids)
                print(f"  {mark} {l.id:<5} {l.title:<40} {ui.dim(f'{total} cards · ends in exercise {ex}')}")
        print()
        return 0

    def render_card_body(self, body: str) -> str:
        """Markdown-lite for the terminal: headlines bold, code fences indented, inline code plain."""
        out = []
        in_fence = False
        for line in body.splitlines():
            if line.startswith("```"):
                in_fence = not in_fence
                out.append("")
                continue
            if in_fence:
                out.append("      " + line)
                continue
            if line.startswith("### "):
                out.append("  " + ui.bold(line[4:]))
                continue
            if line.startswith("- "):
                out.append("   • " + line[2:].replace("`", ""))
                continue
            out.append(ui.wrap(line.replace("`", "")) if line.strip() else "")
        return "\n".join(out)

    def print_lesson_static(self, lesson: Lesson) -> None:
        print(ui.heading(f"Lesson {lesson.id} · {lesson.title}"))
        for i, c in enumerate(lesson.cards, 1):
            print(ui.dim(f"  ── {i}/{len(lesson.cards)} {c.kind} ──"))
            if c.kind == "exercise":
                ex = find_exercise(self.catalog, c.exercise_id or "")
                print(f"  Exercise {c.exercise_id}: {ex.title if ex else '?'}   →  course show {c.exercise_id}")
            else:
                print(self.render_card_body(c.body))
                if c.kind == "quiz":
                    for j, o in enumerate(c.options):
                        print(f"     {chr(97 + j)}) {o}")
            print()

    def run_lesson(self, lesson: Lesson, part: Part, restart: bool = False) -> int:
        p = self.progress
        if restart:
            p.restart_lesson(lesson)
        print(ui.heading(f"Lesson {lesson.id} · {lesson.title}   {ui.dim(f'Part {part.num}: {part.title}')}"))
        print(ui.dim("  Enter continues · answers are a letter or text · q quits (progress is saved)\n"))
        earned = 0
        start = 0
        for i in range(len(lesson.cards)):
            if not p.card_state(lesson.id, i)["done"]:
                start = i
                break
        else:
            start = len(lesson.cards)
        if start and start < len(lesson.cards):
            print(ui.dim(f"  Resuming at card {start + 1} of {len(lesson.cards)}.\n"))
        i = start
        while i < len(lesson.cards):
            card = lesson.cards[i]
            print(ui.dim(f"  ── {i + 1}/{len(lesson.cards)} ──"))
            try:
                result = self.play_card(lesson, i, card)
            except (KeyboardInterrupt, EOFError):
                print("\n" + ui.dim("  Saved. Come back with `course learn`."))
                return 0
            if result == "quit":
                print(ui.dim("  Saved. Come back with `course learn`."))
                return 0
            if isinstance(result, int):
                earned += result
            i += 1
        done, total, complete = p.lesson_progress(lesson)
        if complete:
            print(ui.green(ui.bold(f"\n  ✔ Lesson {lesson.id} complete")) + ui.dim(f"  (+{earned} xp from cards this session)"))
        else:
            missing = [e for e in lesson.exercise_ids if not p.is_solved(e)]
            print(ui.yellow(f"\n  Cards done. Finish exercise {', '.join(missing)} to complete the lesson: course run {missing[0]}"))
        nxt = self.next_lesson(after=lesson)
        if nxt:
            print(f"  Next: {ui.bold(f'Lesson {nxt.id}')} {nxt.title}   →  {ui.cyan('course learn')}")
        return 0

    def play_card(self, lesson: Lesson, i: int, card: Card):
        p = self.progress
        if card.kind in ("teach", "recap"):
            print(self.render_card_body(card.body))
            ans = input(ui.dim("\n  [Enter] continue  [q] quit › ")).strip().lower()
            if ans == "q":
                return "quit"
            p.record_card(lesson.id, i, checkable=False)
            print()
            return 0
        if card.kind == "exercise":
            ex = find_exercise(self.catalog, card.exercise_id or "")
            if ex is None:
                return 0
            p.touch(ex)
            p.save()
            print(ui.bold(f"  Put it together: exercise {ex.id} · {ex.title}") + ui.dim(f"  ({ex.kyu} kyu, {ex.xp} xp)"))
            print(ui.wrap(ex.description().split("\n\n")[1] if "\n\n" in ex.description() else ex.description()))
            print(f"\n  Edit  {ui.bold(self.rel(self.workspace.ensure(ex)))}")
            while True:
                if p.is_solved(ex.id):
                    print(ui.green(f"  ✔ {ex.id} solved"))
                    p.record_card(lesson.id, i, checkable=False)
                    return 0
                ans = input(ui.dim("  [r] run tests  [d] full description  [h] hint  [s] skip for now  [q] quit › ")).strip().lower()
                if ans == "r":
                    self.run_once(ex)
                elif ans == "d":
                    self.print_exercise(ex)
                elif ans == "h":
                    hint = p.reveal_hint(ex)
                    print(ui.yellow(f"  Hint: {hint}") if hint else ui.dim("  No more hints."))
                elif ans == "s":
                    print(ui.dim(f"  Skipped. Come back with `course run {ex.id}`."))
                    return 0
                elif ans == "q":
                    return "quit"
        if card.kind == "code":
            return self.play_code_card(lesson, i, card)
        # checkable cards
        print(self.render_card_body(card.body))
        if card.kind == "quiz":
            for j, o in enumerate(card.options):
                print(f"     {ui.bold(chr(97 + j) + ')')} {o}")
            prompt = "  your answer (letter) › "
        else:
            prompt = "  your answer › "
        tries = 0
        while True:
            ans = input(ui.dim("\n" + prompt)).strip()
            if ans.lower() == "q":
                return "quit"
            if not ans:
                continue
            tries += 1
            ok = card.check(ans)
            xp = p.record_card(lesson.id, i, checkable=True, correct=ok)
            if ok:
                print(ui.green("  ✔ Correct") + (ui.yellow(f"  +{xp} xp") if xp else ""))
                if card.explanation:
                    print(ui.wrap(card.explanation.replace("`", "")))
                print()
                return xp
            if tries == 1:
                print(ui.red("  ✘ Not quite. Try once more."))
                continue
            right = card.options[card.correct] if card.kind == "quiz" and card.correct is not None else card.answers[0]
            print(ui.red("  ✘ Not this time.") + f"  The answer is: {ui.bold(right)}")
            if card.explanation:
                print(ui.wrap(card.explanation.replace("`", "")))
            print()
            return 0

    def play_code_card(self, lesson: Lesson, i: int, card: Card):
        p = self.progress
        print(ui.wrap(card.prompt.replace("`", "")))
        starter = card.starter
        if starter.strip():
            print(ui.dim("\n  Starter (already there, do not retype it):"))
            for line in starter.rstrip("\n").splitlines():
                print("      " + line)
        print(ui.dim("\n  Type your Python below. Empty line runs it. `q` quits, `s` shows the solution."))
        fails = 0
        while True:
            lines: List[str] = []
            while True:
                try:
                    raw = input(ui.dim("  » " if not lines else "  … "))
                except EOFError:
                    return "quit"
                if not lines and raw.strip().lower() == "q":
                    return "quit"
                if not lines and raw.strip().lower() == "s":
                    print(ui.yellow("  Solution:"))
                    for sl in card.solution.splitlines():
                        print("      " + sl)
                    if card.explanation:
                        print(ui.wrap(card.explanation.replace("`", "")))
                    p.record_card(lesson.id, i, checkable=True, correct=False)
                    p.record_card(lesson.id, i, checkable=True, correct=False)
                    print()
                    return 0
                if raw.strip() == "" and lines:
                    break
                if raw.strip() == "" and not lines:
                    continue
                lines.append(raw)
            code = starter + "\n".join(lines) + "\n"
            res = run_code_card(card, code)
            if res.ok:
                xp = p.record_card(lesson.id, i, checkable=True, correct=True)
                if res.stdout.strip():
                    print(ui.dim("  output: ") + res.stdout.strip().replace("\n", "\n          "))
                print(ui.green("  ✔ It runs and does the job") + (ui.yellow(f"  +{xp} xp") if xp else ""))
                if card.explanation:
                    print(ui.wrap(card.explanation.replace("`", "")))
                print()
                return xp
            fails += 1
            p.record_card(lesson.id, i, checkable=True, correct=False)
            if res.import_error:
                print(ui.red("  ✘ Python could not run that:"))
                print(_indent(_short_tb(res.import_error), "      "))
            elif res.timed_out:
                print(ui.red("  ✘ Timed out (infinite loop?)"))
            else:
                for t in res.tests:
                    if t.status != "pass":
                        print(ui.red(f"  ✘ {t.doc or t.name}"))
                        print(_indent(_short_tb(t.traceback or t.message, keep_frames=0), "      "))
                if res.stdout.strip():
                    print(ui.dim("  your output: ") + res.stdout.strip().replace("\n", "\n               "))
            if fails >= 2:
                print(ui.yellow("  Here is one way to do it:"))
                for sl in card.solution.splitlines():
                    print("      " + sl)
                if card.explanation:
                    print(ui.wrap(card.explanation.replace("`", "")))
                print(ui.dim("  Type it yourself to run it, or press Enter twice to move on."))
                fails = 0
                p.data["cards"][f"{lesson.id}:{i}"]["done"] = True
                p.save()
                # one more round: if they just press Enter, move on
                try:
                    raw = input(ui.dim("  » "))
                except EOFError:
                    return 0
                if raw.strip() == "":
                    print()
                    return 0
                lines = [raw]
                while True:
                    raw = input(ui.dim("  … "))
                    if raw.strip() == "":
                        break
                    lines.append(raw)
                res = run_code_card(card, starter + "\n".join(lines) + "\n")
                print((ui.green("  ✔ It runs and does the job") if res.ok else ui.red("  ✘ Still not quite; moving on.")) + "\n")
                return 0
            print(ui.dim("  Try again."))

    def cmd_backup(self, args) -> int:
        dest = Path(args.to).expanduser() if args.to else None
        path, n, has_progress = backup_mod.backup(self.catalog, self.progress.path, dest, workspace=self.workspace)
        print(ui.green(f"  Backed up to {path}"))
        print(f"  progress file: {'included' if has_progress else 'none yet'}   learner files: {n}")
        legacy = len(backup_mod.inspect(path).get("legacy_recoveries", []))
        if legacy:
            print(ui.yellow(f"  Included {legacy} changed or unverified curriculum file(s) as recovery copies; workspace answers remain separate."))
            print(ui.dim("  Review course migrate-answers before restoring curriculum starters."))
        if not has_progress and n == 0:
            print(ui.dim("  (nothing to back up yet: no progress and no workspace files)"))
        return 0

    def cmd_restore(self, args) -> int:
        archive = Path(args.archive).expanduser()
        if not archive.exists():
            self.die(f"No such file: {archive}")
        try:
            manifest = backup_mod.inspect(archive)
        except (KeyError, ValueError, OSError, zipfile.BadZipFile) as e:
            self.die(f"Not a course backup: {e}")
        print(ui.heading(f"Restore · {archive.name}"))
        print(f"  made {manifest.get('created')} with course v{manifest.get('course_version')}")
        print(f"  progress: {'yes' if manifest.get('progress') else 'no'}   answer/workspace files: {len(manifest.get('exercises', []))}")
        if args.list:
            for rel in manifest.get("exercises", []):
                print("    " + rel)
            return 0
        try:
            result = backup_mod.restore(
                archive, self.progress.path, force=args.force,
                exercises_only=args.exercises_only, progress_only=args.progress_only,
                catalog=self.catalog, workspace=self.workspace,
            )
        except (ValueError, OSError, zipfile.BadZipFile) as e:
            self.die(str(e))
        if result["progress"]:
            print(ui.green(f"  Restored progress → {result['progress']}"))
        for rel in result["exercises"]:
            print(ui.green(f"  Restored {rel}"))
        for rel in result["skipped"]:
            print(ui.yellow(f"  Skipped {rel} (not in this course version)"))
        for path in result.get("recoveries", []):
            print(ui.dim(f"  Previous file saved to {path}"))
        return 0

    def cmd_path(self, args) -> int:
        ex = self.resolve(args.exercise, record_selection=not args.scratch)
        print(self.workspace.ensure(ex, scratch=args.scratch))
        return 0


def _local_time(value: str, pattern: str) -> str:
    """Show local time when representable, otherwise retain the valid UTC instant."""
    instant = parse_timestamp(value)
    if instant is None:
        return "invalid saved time"
    try:
        return instant.astimezone().strftime(pattern)
    except (ValueError, OverflowError, OSError):
        return instant.isoformat(timespec="seconds").replace("+00:00", "Z")


def _short_tb(tb: str, keep_frames: int = 3) -> str:
    """Keep only the frames inside the learner's files plus the final exception line."""
    lines = tb.rstrip().splitlines()
    if not lines:
        return ""
    # Split into header, frames (File ... + following indented lines), and the exception tail.
    frames = []
    tail = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("  File "):
            frame = [line]
            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                frame.append(lines[i])
                i += 1
            frames.append(frame)
            continue
        if not line.startswith("Traceback (most recent call last)"):
            tail.append(line)
        i += 1
    keep = [f for f in frames if "/unittest/" not in f[0] and "harness.py" not in f[0]]
    keep = keep[-keep_frames:]
    exc = "\n".join(tail).strip()
    if exc.startswith("NotImplementedError"):
        return "not implemented yet: " + exc.partition(":")[2].strip()
    out = []
    for f in keep:
        head = re.sub(r'^\s*File "(?:.*/)?([^/"]+)", line (\d+)(?:, in (.+))?$',
                      lambda m: f"{m.group(1)}:{m.group(2)}" + (f" in {m.group(3)}" if m.group(3) else ""), f[0])
        out.append(head)
        out.extend("    " + l.strip() for l in f[1:] if l.strip())
    out.append(exc)
    return "\n".join(out)


def _indent(text: str, prefix: str = "    ") -> str:
    return "\n".join(prefix + l for l in text.splitlines())


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="course", description="Interactive Python course for CPE interviews.")
    ap.add_argument("--no-color", action="store_true", help="disable ANSI colors")
    ap.add_argument("--version", action="version", version=f"course {__version__}")
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("status", help="dashboard: rank, xp, streak, progress per part")
    s = sub.add_parser("learn", help="guided lesson: bite-sized cards with checks, ending in an exercise"); s.add_argument("lesson", nargs="?", help="lesson id like 1.2, a part number, or 'next'"); s.add_argument("--list", action="store_true", help="list lessons and progress"); s.add_argument("--show", action="store_true", help="print all cards without the interactive checks"); s.add_argument("--restart", action="store_true", help="forget answers for this lesson and start over")
    s = sub.add_parser("list", help="list exercises"); s.add_argument("part", nargs="?"); s.add_argument("-u", "--unsolved", action="store_true")
    s = sub.add_parser("show", help="show an exercise's problem statement"); s.add_argument("exercise", nargs="?")
    sub.add_parser("next", help="show the next unsolved exercise")
    s = sub.add_parser("run", help="run the tests (default: last exercise touched)"); s.add_argument("exercise", nargs="?"); s.add_argument("-v", "--verbose", action="store_true", help="full tracebacks"); s.add_argument("--scratch", action="store_true", help="grade a separate practice copy without changing progress")
    s = sub.add_parser("watch", help="re-run tests whenever exercise.py changes"); s.add_argument("exercise", nargs="?"); s.add_argument("--exit-on-pass", action="store_true")
    s = sub.add_parser("hint", help="reveal the next hint (costs 25%% of the exercise's XP)"); s.add_argument("exercise", nargs="?")
    s = sub.add_parser("solution", help="show reference solutions (after passing)"); s.add_argument("exercise", nargs="?"); s.add_argument("--force", action="store_true")
    s = sub.add_parser("lesson", help="read a part's lesson"); s.add_argument("part", nargs="?")
    sub.add_parser("daily", help="today's kata (+5 xp bonus)")
    s = sub.add_parser("interview", help="timed mock interview"); s.add_argument("--count", type=int, default=3); s.add_argument("--minutes", type=int, default=45); s.add_argument("--min-part", type=int, default=9); s.add_argument("--new", action="store_true"); s.add_argument("--finish", action="store_true"); s.add_argument("--last", action="store_true", help="review the most recently finished round")
    sub.add_parser("badges", help="list badges")
    s = sub.add_parser("reset", help="reset a learner answer, keeping recovery copies"); s.add_argument("exercise"); s.add_argument("--scratch", action="store_true", help="reset only the scratch practice copy")
    s = sub.add_parser("migrate-answers", help="preview or copy legacy edits out of curriculum"); s.add_argument("exercise", nargs="?"); s.add_argument("--apply", action="store_true", help="copy legacy edits, preserving conflicting saved answers"); s.add_argument("--restore-starters", action="store_true", help="with --apply, restore committed curriculum starters after saving recovery copies")
    s = sub.add_parser("repl", help="open an interactive Python with the exercise loaded"); s.add_argument("exercise", nargs="?")
    s = sub.add_parser("path", help="print the learner answer path, initializing it if needed"); s.add_argument("exercise", nargs="?"); s.add_argument("--scratch", action="store_true", help="print a separate practice copy")
    s = sub.add_parser("backup", help="zip progress and learner workspace (default: ~/course-backups/)"); s.add_argument("--to", help="file or directory to write the zip to")
    s = sub.add_parser("restore", help="restore a backup zip"); s.add_argument("archive"); s.add_argument("--force", action="store_true", help="overwrite existing progress or answers after saving recovery copies"); s.add_argument("--list", action="store_true", help="show contents without restoring"); s.add_argument("--exercises-only", action="store_true"); s.add_argument("--progress-only", action="store_true")
    return ap


def main(argv: Optional[List[str]] = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    if args.no_color:
        ui.enable_color(False)
    try:
        app = App()
    except (OSError, ValueError) as e:
        App.die(str(e))
    if not app.catalog:
        App.die("No curriculum found. Run from the repository root.")
    cmd = args.cmd or "status"
    handler = getattr(app, "cmd_" + cmd.replace("-", "_"))
    try:
        return int(handler(args) or 0)
    except KeyboardInterrupt:
        print()
        return 130
    except BrokenPipeError:
        try:
            sys.stdout.close()
        except OSError:
            pass
        return 0
    except (OSError, ValueError) as e:
        App.die(str(e))
