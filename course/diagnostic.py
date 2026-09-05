"""CLI flow for the independent fundamentals diagnostic."""
from __future__ import annotations

from . import ui
from .catalog import find_exercise
from .practice import DIAGNOSTIC_IDS, diagnostic_summary
from .progress import Progress
from .runner import run_learner


def _lesson(app, ex_id):
    return next((lesson for lessons in app.lessons.values() for lesson in lessons if ex_id in lesson.exercise_ids), None)


def _summary(app, state):
    rows = diagnostic_summary(state)
    if rows is None:
        print("  Archived round has invalid or unsupported data; the original is kept in your progress export.")
        return
    print(ui.heading("Fundamentals diagnostic · untimed"))
    print(f"  Round {state['id']} · started {state['started']}")
    print("  Outcomes describe this round's latest tests. Confidence is your own reflection.")
    for row in rows:
        ex = find_exercise(app.catalog, row["id"])
        label = row["outcome"].replace("_", " ")
        confidence = (row["confidence"] or "not recorded").replace("_", " ")
        print(f"\n  {row['id']} {ex.title if ex else 'Exercise unavailable'} · {label} · {row['attempts']} attempt(s)")
        print(f"    Confidence: {confidence}" + (" · help used" if row["help_used"] else ""))
        if row["mistake_note"]:
            print(f"    Note: {row['mistake_note']}")
        lesson = _lesson(app, row["id"])
        if lesson:
            print(f"    Revisit if useful: course learn {lesson.id}  ({lesson.title})")
    attempted = sum(row["attempts"] > 0 for row in rows)
    reflected = sum(row["confidence"] is not None for row in rows)
    print(f"\n  {attempted}/6 attempted · {reflected}/6 reflections recorded")


def command(app, args):
    action = args.action
    if action == "history":
        history = app.progress.data.get("diagnostic_history", [])
        if not isinstance(history, list) or not history:
            print("No earlier diagnostic rounds.")
        else:
            for state in history:
                _summary(app, state)
        return 0
    for ex_id in DIAGNOSTIC_IDS:
        if find_exercise(app.catalog, ex_id) is None:
            raise ValueError(f"Diagnostic exercise {ex_id} is unavailable in this catalog")
    state = app.progress.start_diagnostic(new=action == "new")
    if action in ("summary", "new"):
        _summary(app, state)
        print("\n  Attempt first: course diagnostic show <id>")
        print("  Resume: course diagnostic show   ·   Help anytime: course diagnostic help <id>")
        print("  New round: course diagnostic new   ·   Earlier summaries: course diagnostic history")
        return 0
    rows = diagnostic_summary(state)
    ex_id = args.exercise or state["last_exercise"] or next((row["id"] for row in rows if not row["attempts"]), DIAGNOSTIC_IDS[0])
    if ex_id not in DIAGNOSTIC_IDS:
        raise ValueError("Choose one of the diagnostic exercises: " + ", ".join(DIAGNOSTIC_IDS))
    ex = find_exercise(app.catalog, ex_id)
    sid = state["id"]
    if action == "reflect":
        if args.confidence is None:
            raise ValueError("Use --confidence confident or --confidence needs-review")
        app.progress.reflect_diagnostic(ex_id, args.confidence.replace("-", "_"), args.note, sid)
        print("Reflection saved. Review the whole round with `course diagnostic`.")
        return 0
    if action == "help":
        app.progress.request_diagnostic_help(ex_id, sid)
        print(ui.heading(f"Diagnostic help · {ex.id} {ex.title}"))
        for hint in ex.hints:
            print(ui.wrap(hint))
        lesson = _lesson(app, ex_id)
        if lesson:
            print(f"\n  Optional lesson: course learn {lesson.id} --show  ({lesson.title})")
        print(f"  Return to your diagnostic work: course diagnostic show {ex_id}")
        return 0
    answer = app.workspace.ensure_practice(ex, sid, state["drafts"].get(ex_id))
    app.progress.update_diagnostic(ex_id, "open", sid)
    if action == "path":
        print(answer)
        return 0
    if action == "show":
        print(ui.heading(f"Diagnostic · {ex.id} {ex.title}"))
        print("  Try the problem before opening guidance. Help is available whenever you need it.\n")
        print(ui.wrap(ex.description()))
        print(f"\n  Edit: {answer}")
        print(f"  Run: course diagnostic run {ex_id}   ·   Help: course diagnostic help {ex_id}")
        print(f'  Reflect: course diagnostic reflect {ex_id} --confidence needs-review --note "What tripped me up"')
        return 0
    if action == "run":
        code = answer.read_text(encoding="utf-8")
        app.progress.update_diagnostic(ex_id, "draft", sid, code=code)
        result = run_learner(ex, app.workspace, answer)
        app.print_result(result, verbose=args.verbose)
        # A second CLI process may have started a different round while grading.
        app.progress = Progress(app.progress.path)
        app.progress.record_diagnostic_attempt(ex_id, result.ok, sid)
        print("  Diagnostic tests passed." if result.ok else "  Diagnostic tests not yet passing.")
        print(f'  Record your confidence: course diagnostic reflect {ex_id} --confidence confident --note ""')
        print(f"  Or choose needs-review. Help: course diagnostic help {ex_id}   ·   Summary: course diagnostic")
        return 0 if result.ok else 1
    raise ValueError("Unknown diagnostic action")
