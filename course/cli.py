"""Command-line interface: ``python -m course <command>`` (or ``./course.py``)."""
from __future__ import annotations

import argparse
import datetime as dt
import random
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

from . import __version__, ui
from .catalog import ROOT, Exercise, Part, all_exercises, find_exercise, find_part, load_catalog, total_xp
from .progress import BADGES, RANKS, Progress
from .runner import RunResult, run_tests


class App:
    def __init__(self) -> None:
        self.catalog = load_catalog()
        self.progress = Progress()
        self.total_xp = total_xp(self.catalog)

    # ------------------------------------------------------------ helpers
    def resolve(self, ref: Optional[str]) -> Exercise:
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
            return self.daily_exercise()
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
            print(f"  {part.num:>2}. {part.title:<42} {ui.bar(s / t if t else 0, 16)} {s:>2}/{t:<2} {ui.dim(f'{exp}/{txp} xp')}")
        nxt = self.next_unsolved()
        print()
        if nxt:
            print(f"  Up next: {ui.bold(nxt.id)} {nxt.title}   →  {ui.cyan('course next')}")
        else:
            print("  " + ui.green("All exercises solved. 🎓"))
        print(ui.dim("  Commands: list · show · run · hint · solution · lesson · daily · interview · watch · badges"))
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
        print(f"  File   {ui.bold(self.rel(ex.exercise_file))}")
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
        ex = self.resolve(args.exercise)
        return self.run_once(ex, verbose=args.verbose)

    def run_once(self, ex: Exercise, verbose: bool = False) -> int:
        print(ui.heading(f"Running tests · {ex.id} {ex.title}"))
        t0 = time.time()
        res = run_tests(ex)
        elapsed = time.time() - t0
        self.print_result(res, verbose=verbose)
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
        print(ui.dim(f"Watching {self.rel(ex.exercise_file)} — save the file to re-run. Ctrl-C to stop."))
        last = None
        try:
            while True:
                try:
                    mtime = ex.exercise_file.stat().st_mtime
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
        ex = self.resolve(args.exercise)
        try:
            stub = subprocess.run(
                ["git", "show", f"HEAD:{ex.exercise_file.relative_to(ROOT).as_posix()}"],
                capture_output=True, text=True, cwd=str(ROOT), check=True,
            ).stdout
        except (subprocess.CalledProcessError, OSError, ValueError):
            self.die("Could not read the original stub from git. Restore exercise.py manually.")
        ex.exercise_file.write_text(stub, encoding="utf-8")
        self.progress.forget(ex.id)
        print(ui.green(f"  Restored {self.rel(ex.exercise_file)} to the original stub."))
        return 0

    def daily_exercise(self) -> Exercise:
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
        session = p.data.get("interview")
        if args.finish or (session and not args.new):
            if not session:
                print("No mock interview in progress. Start one with `course interview`.")
                return 0
            return self.report_interview(session, final=args.finish)
        exs = [e for e in all_exercises(self.catalog) if e.part_num >= args.min_part and not p.is_solved(e.id)]
        if len(exs) < args.count:
            exs = [e for e in all_exercises(self.catalog) if e.part_num >= args.min_part]
        rng = random.Random()
        picks = rng.sample(exs, min(args.count, len(exs)))
        picks.sort(key=lambda e: (-e.kyu, e.part_num, e.num))
        deadline = dt.datetime.now() + dt.timedelta(minutes=args.minutes)
        p.data["interview"] = {
            "ids": [e.id for e in picks],
            "started": dt.datetime.now().replace(microsecond=0).isoformat(),
            "deadline": deadline.replace(microsecond=0).isoformat(),
            "solved_before": [e.id for e in picks if p.is_solved(e.id)],
        }
        p.save()
        print(ui.heading(f"Mock interview · {len(picks)} problems · {args.minutes} minutes"))
        print("  Talk out loud, state assumptions, write the brute force first, then improve it.\n")
        for e in picks:
            print(self.ex_line(e))
        print(f"\n  Deadline {ui.bold(deadline.strftime('%H:%M'))}.  Work them with `course show <id>` / `course run <id>`.")
        print(f"  Check the clock with {ui.cyan('course interview')}, finish with {ui.cyan('course interview --finish')}.")
        return 0

    def report_interview(self, session: dict, final: bool) -> int:
        p = self.progress
        ids = session["ids"]
        deadline = dt.datetime.fromisoformat(session["deadline"])
        left = deadline - dt.datetime.now()
        solved = [i for i in ids if p.is_solved(i) and i not in session.get("solved_before", [])]
        print(ui.heading("Mock interview"))
        for i in ids:
            ex = find_exercise(self.catalog, i)
            if ex:
                print(self.ex_line(ex))
        mins = int(left.total_seconds() // 60)
        if left.total_seconds() > 0:
            print(f"\n  ⏱ {mins} min left")
        else:
            print(ui.red(f"\n  ⏱ Time is up ({-mins} min over)"))
        if final:
            print(f"\n  Result: {ui.bold(f'{len(solved)}/{len(ids)}')} passed"
                  + (ui.green(" inside the time limit") if left.total_seconds() > 0 else ui.red(" over time")))
            if len(solved) == len(ids) and left.total_seconds() > 0 and p.award_badge("interviewer"):
                print(ui.magenta("  🎤 Badge unlocked: aced a mock interview"))
            p.data["interview"] = None
            p.save()
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
        print(ui.dim(f"Interactive Python with {self.rel(ex.exercise_file)} loaded. exit() to leave."))
        return subprocess.call([sys.executable, "-i", str(ex.exercise_file)], cwd=str(ex.dir))

    def cmd_path(self, args) -> int:
        ex = self.resolve(args.exercise)
        print(ex.exercise_file)
        return 0


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
    s = sub.add_parser("list", help="list exercises"); s.add_argument("part", nargs="?"); s.add_argument("-u", "--unsolved", action="store_true")
    s = sub.add_parser("show", help="show an exercise's problem statement"); s.add_argument("exercise", nargs="?")
    sub.add_parser("next", help="show the next unsolved exercise")
    s = sub.add_parser("run", help="run the tests (default: last exercise touched)"); s.add_argument("exercise", nargs="?"); s.add_argument("-v", "--verbose", action="store_true", help="full tracebacks")
    s = sub.add_parser("watch", help="re-run tests whenever exercise.py changes"); s.add_argument("exercise", nargs="?"); s.add_argument("--exit-on-pass", action="store_true")
    s = sub.add_parser("hint", help="reveal the next hint (costs 25%% of the exercise's XP)"); s.add_argument("exercise", nargs="?")
    s = sub.add_parser("solution", help="show reference solutions (after passing)"); s.add_argument("exercise", nargs="?"); s.add_argument("--force", action="store_true")
    s = sub.add_parser("lesson", help="read a part's lesson"); s.add_argument("part", nargs="?")
    sub.add_parser("daily", help="today's kata (+5 xp bonus)")
    s = sub.add_parser("interview", help="timed mock interview"); s.add_argument("--count", type=int, default=3); s.add_argument("--minutes", type=int, default=45); s.add_argument("--min-part", type=int, default=9); s.add_argument("--new", action="store_true"); s.add_argument("--finish", action="store_true")
    sub.add_parser("badges", help="list badges")
    s = sub.add_parser("reset", help="restore an exercise to its original stub"); s.add_argument("exercise")
    s = sub.add_parser("repl", help="open an interactive Python with the exercise loaded"); s.add_argument("exercise", nargs="?")
    s = sub.add_parser("path", help="print the path to exercise.py"); s.add_argument("exercise", nargs="?")
    return ap


def main(argv: Optional[List[str]] = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    if args.no_color:
        ui.enable_color(False)
    app = App()
    if not app.catalog:
        App.die("No curriculum found. Run from the repository root.")
    cmd = args.cmd or "status"
    handler = getattr(app, f"cmd_{cmd}")
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
