"""Small optional Bash-to-Python bridges inside existing guided lessons."""

BRIDGES = [
    {"id": "return", "title": "Return versus print", "lesson": "3.1", "card": "bash-return-worked",
     "diagnostic_ids": ["1.2", "3.1"], "prerequisites": "Function calls and arithmetic"},
    {"id": "collections", "title": "Keep collections structured", "lesson": "5.1", "card": "bash-collections-worked",
     "diagnostic_ids": ["2.1", "2.2", "5.1"], "prerequisites": "Lists, loops and dictionary lookup"},
    {"id": "aliasing", "title": "Mutability and aliasing", "lesson": "2.3", "card": "bash-aliasing-worked",
     "diagnostic_ids": ["2.2", "5.1"], "prerequisites": "Lists and function calls"},
    {"id": "defaults", "title": "Defaults and local scope", "lesson": "3.2", "card": "bash-defaults-worked",
     "diagnostic_ids": ["3.1"], "prerequisites": "Functions, optional arguments and lists (lesson 3.1)"},
    {"id": "process", "title": "Exceptions versus exit status", "lesson": "10.4", "card": "bash-process-worked",
     "diagnostic_ids": ["3.1"], "prerequisites": "Functions and try/except/raise (lessons 3.1 and 7.1–7.2); process failures are not directly assessed by this diagnostic"},
]


def bridges_for(exercise_id):
    return [bridge for bridge in BRIDGES if exercise_id in bridge["diagnostic_ids"]]


def has_review_signal(row):
    return (row["outcome"] == "not_passed" or row["confidence"] == "needs_review"
            or row["help_used"] or bool(row["mistake_note"].strip()))
