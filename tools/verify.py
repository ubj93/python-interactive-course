#!/usr/bin/env python3
"""Verify the curriculum: every exercise is well-formed, its solution passes, its stub fails.

Usage: python tools/verify.py [part-or-exercise ...] [--quiet]
Exit code 1 on any problem. Run in CI and before committing new content.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from course.catalog import KYU_XP, all_exercises, find_exercise, find_part, load_catalog, total_xp  # noqa: E402
from course.runner import run_code_card, run_solution, run_tests  # noqa: E402
from course.lessons import load_lessons, validate_lesson, validate_card_ids  # noqa: E402

FORBIDDEN_IMPORTS = re.compile(r"^\s*(?:import|from)\s+(requests|numpy|pandas|pytest|yaml|httpx|aiohttp)\b", re.M)
NETWORK_CALLS = re.compile(r"urllib\.request\.urlopen\(|socket\.create_connection\(|http\.client\.HTTPS?Connection\(")


def check_exercise(ex, problems: list, quiet: bool) -> None:
    tag = f"[{ex.id} {ex.dir.name}]"

    def bad(msg: str) -> None:
        problems.append(f"{tag} {msg}")

    for name in ("exercise.py", "test_exercise.py", "solution.py", "meta.json"):
        if not (ex.dir / name).exists():
            bad(f"missing {name}")
    if problems and problems[-1].startswith(tag) and "missing" in problems[-1]:
        return

    meta = ex.meta
    if "title" not in meta:
        bad("meta.json needs a title")
    if ex.kyu not in KYU_XP:
        bad(f"kyu must be one of {sorted(KYU_XP)}")
    if not ex.hints:
        bad("meta.json needs at least one hint")
    if not ex.tags:
        bad("meta.json needs tags")
    if not ex.description():
        bad("exercise.py needs a module docstring with the problem statement")

    for f in (ex.exercise_file, ex.test_file, ex.solution_file):
        src = f.read_text(encoding="utf-8")
        m = FORBIDDEN_IMPORTS.search(src)
        if m:
            bad(f"{f.name} imports third-party module '{m.group(1)}' (stdlib only)")
        if NETWORK_CALLS.search(src):
            bad(f"{f.name} performs a real network call")
    if "solution" in ex.test_file.read_text(encoding="utf-8"):
        bad("test_exercise.py must not reference solution.py")

    stub = run_tests(ex)
    if stub.ok:
        bad("the unmodified stub passes all tests; tests are not meaningful")
    elif stub.crashed:
        bad(f"harness crashed on stub: {stub.crashed[:200]}")
    elif not stub.tests and not stub.import_error:
        bad("no tests were collected")

    sol = run_solution(ex)
    if not sol.ok:
        details = sol.import_error or sol.crashed or "; ".join(
            f"{t.name}: {t.message}" for t in sol.tests if t.status != "pass"
        )
        if sol.timed_out:
            details = "timed out"
        bad(f"solution.py fails: {details[:600]}")
    if not quiet:
        state = "ok " if (not sol.ok or stub.ok) is False else "BAD"
        print(f"  {state} {ex.id:<5} {ex.title:<40} {ex.kyu} kyu  {len(sol.tests)} tests")


def main(argv: list) -> int:
    quiet = "--quiet" in argv
    refs = [a for a in argv if not a.startswith("--")]
    catalog = load_catalog()
    if not catalog:
        print("no curriculum found")
        return 1
    problems: list = []
    refs = [a for a in argv if not a.startswith("--")]

    # Structural checks across the catalog
    ids = [e.id for e in all_exercises(catalog)]
    if len(ids) != len(set(ids)):
        problems.append("duplicate exercise ids")
    problems.extend(validate_card_ids([lesson for part in catalog for lesson in load_lessons(part)]))
    lesson_xp = 0
    for part in catalog:
        if not part.lesson_file.exists():
            problems.append(f"[part {part.num}] missing LESSON.md")
        lessons = load_lessons(part)
        if not lessons:
            problems.append(f"[part {part.num}] missing lessons/ (guided lesson cards)")
        else:
            nums = [l.num for l in lessons]
            if nums != list(range(1, len(nums) + 1)):
                problems.append(f"[part {part.num}] lesson numbers must be 01..N without gaps (got {nums})")
            referenced = {}
            for l in lessons:
                problems.extend(validate_lesson(l, part))
                if not refs or any(find_part(catalog, r) is part for r in refs if find_part(catalog, r)):
                    for idx, c in enumerate(l.cards, 1):
                        if c.kind != "code":
                            continue
                        ok = run_code_card(c, c.starter + c.solution + "\n")
                        if not ok.ok:
                            why = ok.import_error or "; ".join(f"{t.doc}: {t.message}" for t in ok.tests if t.status != "pass")
                            problems.append(f"[lesson {l.id}] card {idx} (code): solution does not pass: {why[:300]}")
                        if run_code_card(c, c.starter).ok:
                            problems.append(f"[lesson {l.id}] card {idx} (code): the starter alone already passes; the check is not meaningful")
                for eid in l.exercise_ids:
                    referenced.setdefault(eid, []).append(l.id)
                lesson_xp += l.xp
            for e in part.exercises:
                users = referenced.get(e.id, [])
                if not users:
                    problems.append(f"[part {part.num}] exercise {e.id} is not reached by any lesson")
                elif len(users) > 1:
                    problems.append(f"[part {part.num}] exercise {e.id} is used by several lessons: {users}")
        nums = [e.num for e in part.exercises]
        if nums != list(range(1, len(nums) + 1)):
            problems.append(f"[part {part.num}] exercise numbers must be 01..N without gaps (got {nums})")

    exercises = all_exercises(catalog)
    if refs:
        chosen = []
        for r in refs:
            p = find_part(catalog, r)
            if p:
                chosen.extend(p.exercises)
                continue
            e = find_exercise(catalog, r)
            if e:
                chosen.append(e)
            else:
                problems.append(f"unknown reference '{r}'")
        exercises = chosen

    for ex in exercises:
        check_exercise(ex, problems, quiet)

    print()
    n_lessons = sum(len(load_lessons(p)) for p in catalog)
    print(f"{len(exercises)} exercises checked · {n_lessons} lessons · {len(catalog)} parts · {total_xp(catalog) + lesson_xp} total xp")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print("  - " + p)
        return 1
    print("all good")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
