"""Terminal presentation for the saved interview refresher."""
from . import refresher, ui
from .sessions import new_session

_UNSET = object()


def save(app, saved, interview=_UNSET):
    before = app.progress.data.copy()
    app.progress.data["refresher"] = saved
    if interview is not _UNSET:
        app.progress.data["interview"] = interview
        app.progress.data["legacy_interview_migrated"] = True
    try:
        app.progress.save()
    except OSError:
        app.progress.data = before
        raise


def command(app, args):
    plan = refresher.catalog()
    saved = refresher.state(app.progress.data.get("refresher"))
    all_activities = refresher.activities()
    action = args.action
    id = args.activity or saved["next_activity"]
    activity = next((item for item in all_activities if item["id"] == id), None)
    if args.activity and activity is None:
        raise ValueError("Unknown activity. Run `course refresher list` for the activity IDs.")
    if action == "open" and activity is None:
        action = "status"
    if action in ("open", "done", "skip", "revisit", "note"):
        if action == "note" and args.text is None:
            raise ValueError("Use `course refresher note <activity> --text 'your note'`.")
        saved = refresher.update(saved, action, id, args.text)
        save(app, saved)
    if action == "mock":
        if not activity or activity["kind"] != "mock":
            raise ValueError("Choose a mock activity: `course refresher mock mocks-a` or `course refresher mock mocks-b`.")
        active = app.progress.active_interview()
        if active and active["id"] != saved["mock_sessions"].get(id):
            raise ValueError("A different mock is active. Run `course interview` to review it, then `course interview --finish` before starting this path mock.")
        if active is None:
            active = new_session(activity["exercises"], activity["minutes"])
            saved["mock_sessions"][id] = active["id"]
        saved = refresher.update(saved, "open", id)
        save(app, saved, interview=active)
        print(ui.heading(activity["title"] + " · refresher mock"))
        print("  Fresh passing runs are required, including for already-solved exercises.")
        return app.report_interview(active, final=False)

    print(ui.heading(plan["title"]))
    print("  " + plan["description"])
    print("  " + plan["prerequisites"])
    print("  Full curriculum: `course learn --list` or `course list`.")
    next_id = saved["next_activity"]
    if next_id:
        next_item = next(item for item in all_activities if item["id"] == next_id)
        print(f"\n  Next: {next_id} · {next_item['title']} ({next_item['minutes']} min)")
        print("  Resume with `course refresher open`.")
    else:
        print("\n  All path activities are done or skipped. Revisit any activity when useful.")
    if action == "list":
        for index, session in enumerate(plan["sessions"], 1):
            minutes = sum(item["minutes"] for item in session["activities"])
            print(ui.heading(f"Session {index}: {session['title']} · {minutes} min"))
            print("  Prerequisites: " + session["prerequisite"])
            for item in session["activities"]:
                print(f"  [{refresher.status(saved, item['id'])}] {item['id']} · {item['title']} ({item['minutes']} min)")
    elif action in ("open", "revisit", "note") and activity:
        print(ui.heading(activity["title"] + f" · {activity['minutes']} min"))
        print("  " + activity["description"])
        if activity["kind"] == "diagnostic":
            print("  Start or resume: `course diagnostic`.")
        for lesson in activity["lessons"]:
            print(f"  Lesson {lesson}: `course learn {lesson}`")
        for exercise in activity["exercises"]:
            print(f"  Exercise {exercise}: `course show {exercise}` then `course run {exercise}`")
        if activity["kind"] == "mock":
            print(f"  Start or resume this curated round: `course refresher mock {id}`.")
        note = saved["activities"].get(id, {}).get("note")
        if isinstance(note, str) and note:
            print("  Your note: " + note)
        print(f"  When ready: `course refresher done {id}`; or `course refresher skip {id}`.")
        print(f"  Save a takeaway: `course refresher note {id} --text 'your note'`.")
    weak = refresher.weak_areas(app.progress.data.get("diagnostic"))
    print(ui.heading("Diagnostic review suggestions"))
    if not weak:
        print("  No review signals saved yet. Try `course diagnostic` and record confidence and notes.")
    for row in weak:
        print(f"  {row['id']}: {'; '.join(row['reasons'])}.")
        if row["note"]:
            print("    " + row["note"])
        print("    " + " · ".join("course learn " + id for id in row["lessons"]))
    print(ui.heading("Optional extensions for your target interview"))
    for item in plan["optional"]:
        print(f"  {item['title']}: lessons {', '.join(item['lessons'])}")
    print("  Done/skip/revisit only changes this path. It does not assert mastery or award XP.")
    return 0
