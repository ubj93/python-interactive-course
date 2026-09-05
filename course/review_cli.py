"""Saved review queue and independent scratch reattempts in the terminal."""
from . import ui
from .catalog import all_exercises, find_exercise
from .practice import practice_summary
from .progress import Progress
from .review import queue_rows
from .runner import run_learner


def reflection(app, args):
    ex = find_exercise(app.catalog, args.exercise)
    if ex is None:
        raise ValueError("Choose an existing course exercise")
    row = app.progress.reflect_exercise(ex.id, args.confidence.replace("-", "_"), args.note, args.interval)
    print(f"Reflection saved for {ex.id}. Next review: {row['next_review']} ({row['interval_days']} days).")
    print("Open the queue with `course review`; practise anytime with `course review new " + ex.id + "`.")
    return 0


def summary(app, state):
    rows = practice_summary(state)
    if rows is None:
        print("Unsupported archived review. The original is preserved in your progress export.")
        return
    print(ui.heading("Review round · untimed"))
    print(f"  Started {state['started']} · {len(rows)} exercise(s)")
    for row in rows:
        print(f"  {row['id']} · {row['outcome'].replace('_', ' ')} · {row['attempts']} attempt(s) · confidence: {(row['confidence'] or 'not recorded').replace('_', ' ')}")
        if row["mistake_note"]:
            print("    " + row["mistake_note"])
    print("  Outcomes belong to this round. They do not change original passes, XP or hint usage.")


def command(app, args):
    action = args.action
    if action == "history":
        history = app.progress.data.get("review_history", [])
        for old in history if isinstance(history, list) else [history]:
            summary(app, old)
        return 0
    if action == "finish":
        summary(app, app.progress.finish_review())
        print("Round saved. Confidence and review dates change only when you record a reflection.")
        return 0
    available = {ex.id for ex in all_exercises(app.catalog)}
    if args.exercise and args.exercise not in available:
        raise ValueError("Choose an existing course exercise")
    rows = queue_rows(app.progress.data.get("review_queue"))
    active = app.progress.review_state()
    if action == "list":
        print(ui.heading("Review queue · practise at your pace"))
        print("Needs review defaults to 1 day; confident to 3 days. You can choose 7 or 30 days, or practise anytime.")
        for row in rows:
            label = "ready to revisit" if row["due"] else "planned"
            title = find_exercise(app.catalog, row["id"])
            print(f"  {row['id']} {title.title if title else '(unavailable exercise)'} · {row['confidence'].replace('_', ' ')} · {row['next_review']} · {label}")
            if row["mistake_note"]:
                print("    " + row["mistake_note"])
        if not rows:
            print("No reflections saved yet. After any exercise: course reflect <id> --confidence needs-review --note 'what to practise'.")
        if active:
            summary(app, active)
        elif app.progress.data.get("review_session") is not None:
            print("An unsupported saved round is preserved. Export a backup before starting `course review new <id>`.")
        print("Resume or begin due work: course review start · Manual fresh round: course review new <id>")
        return 0
    ids = [args.exercise] if args.exercise else [row["id"] for row in rows if row["due"] and row["id"] in available]
    if not ids and (action == "new" or app.progress.data.get("review_session") is None):
        print("No reviews are due. Practise anytime with `course review new <id>`.")
        return 0
    state = app.progress.start_review(ids, new=action == "new")
    if args.exercise and args.exercise not in state["ids"]:
        raise ValueError("That exercise is outside the active review. Use `course review new " + args.exercise + "` for a fresh round")
    if action in ("start", "new"):
        summary(app, state)
        print("Resume: course review show · Run: course review run · Help: course review help · Finish: course review finish")
        return 0
    ex_id = args.exercise or state["last_exercise"] or next((row["id"] for row in practice_summary(state) if not row["attempts"]), state["ids"][0])
    ex = find_exercise(app.catalog, ex_id)
    if ex is None:
        raise ValueError("This saved review exercise is unavailable. Its work is preserved; choose `course review new <id>`")
    sid = state["id"]
    if action == "reflect":
        if args.confidence is None:
            raise ValueError("Use --confidence confident or --confidence needs-review")
        app.progress.update_review(ex_id, "reflect", sid, confidence=args.confidence.replace("-", "_"), note=args.note, interval=args.interval)
        row = app.progress.data["review_queue"]["items"][ex_id]
        print(f"Reflection saved. Next review: {row['next_review']}.")
        return 0
    if action == "help":
        app.progress.update_review(ex_id, "help", sid)
        for hint in ex.hints:
            print(ui.wrap(hint))
        for lessons in app.lessons.values():
            for lesson in lessons:
                if ex_id in lesson.exercise_ids:
                    print(f"  Optional lesson: course learn {lesson.id} --show")
        return 0
    answer = app.workspace.ensure_practice(ex, sid, state["drafts"].get(ex_id))
    app.progress.update_review(ex_id, "open", sid)
    if action == "path":
        print(answer)
        return 0
    if action == "show":
        print(ui.heading(f"Review · {ex.id} {ex.title}"))
        print(ui.wrap(ex.description()))
        print(f"\n  Edit this round's scratch copy: {answer}")
        print(f"  Run: course review run {ex.id} · Help: course review help {ex.id}")
        print(f"  Reflect: course review reflect {ex.id} --confidence needs-review --note 'what to practise'")
        return 0
    if action == "run":
        app.progress.update_review(ex_id, "draft", sid, code=answer.read_text(encoding="utf-8"))
        result = run_learner(ex, app.workspace, answer)
        app.print_result(result, verbose=args.verbose)
        app.progress = Progress(app.progress.path)
        app.progress.update_review(ex_id, "attempt", sid, passed=result.ok)
        print("Review tests passed." if result.ok else "Review tests not yet passing.")
        print(f"Record confidence separately: course review reflect {ex.id} --confidence confident --note ''")
        return 0 if result.ok else 1
    raise ValueError("Unknown review action")
