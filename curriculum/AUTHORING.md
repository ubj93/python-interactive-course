# Authoring guide

Every exercise is a folder. Every folder has the same four files. The engine
(`course/`) and the verifier (`tools/verify.py`) rely on this shape.

```
curriculum/partNN_slug/
  LESSON.md                 # the teaching text for the part
  NN_slug/
    exercise.py             # the stub the learner edits; module docstring = problem statement
    test_exercise.py        # unittest cases; `from exercise import ...`
    solution.py             # reference solution(s); must pass when copied over exercise.py
    meta.json               # title, kyu, tags, hints, time_limit_min
    fixtures/               # optional data files (tests run with cwd = the exercise folder)
```

Numbering is two digits and gap-free (`01_`, `02_`, ...). Slugs are `snake_case` and
match the main function or class name where sensible.

## exercise.py

```python
"""One-line title.

Two to five short paragraphs describing the task in the voice of a ticket or an
interviewer. Say what goes in, what comes out, and every edge case the tests check.
Use plain text; the CLI wraps prose and keeps indented blocks as-is.

Rules:
- bullet the rules the tests enforce
- name exceptions to raise and when

Examples:
    >>> normalize_hostname("  MBP-J-DOE \\n")
    'mbp-j-doe'
"""
from typing import Optional


def normalize_hostname(raw: str) -> str:
    raise NotImplementedError("write normalize_hostname")
```

- The module docstring **is** the problem statement shown by `course show`. Escape
  backslashes inside it (`\\n`) because it is a normal string.
- Include the imports the learner will need (typing, dataclasses, re, ...). Keep type hints.
- Every stub raises `NotImplementedError("write <name>")` so the untouched file fails
  every test in an obvious way. Class exercises stub each method the same way.
- One skill per exercise. Two or three functions are fine when they share a theme.

## test_exercise.py

```python
import unittest

from exercise import normalize_hostname


class TestNormalizeHostname(unittest.TestCase):
    def test_strips_and_lowercases(self):
        """Strips whitespace and lowercases"""
        self.assertEqual(normalize_hostname("  MBP-J-DOE \n"), "mbp-j-doe")


if __name__ == "__main__":
    unittest.main()
```

- `unittest` only. Every test method has a **one-line docstring**; the CLI shows that
  line instead of the method name, so write it as the behaviour being checked.
- Order tests from easiest to hardest in the file; the harness runs them in file order.
- 4 to 8 tests. Each test checks one behaviour. Use `assertEqual(actual, expected)`
  with the learner's call first. Add a message argument in loops (`self.assertEqual(..., s)`).
- Cover: the happy path, boundaries, empty input, `None` where the description says so,
  the error case with `assertRaises`.
- Deterministic. No randomness, no wall-clock dependence (inject `now` or `sleep`), no
  network, no real subprocesses, no threads, no third-party packages.
- Files: create them with `tempfile` inside the test, or ship them in `fixtures/` and
  open them by relative path (`fixtures/inventory.csv`). Keep fixtures under 20 KB.
- Never import or reference `solution.py`.
- Tests must fail on the untouched stub (the verifier checks this).

## solution.py

```python
"""Reference solutions for normalize_hostname."""


# Best practice: a chain of string methods, one rule per call, in the order the spec lists them.
def normalize_hostname(raw: str) -> str:
    return raw.strip().lower().split(".")[0].replace("_", "-")


# Clever: str.partition returns (before, sep, after) and never raises.
def normalize_hostname_partition(raw: str) -> str:
    head, _, _ = raw.strip().lower().partition(".")
    return head.replace("_", "-")
```

- The first solution uses the **exact names** from the stub; the verifier copies this
  file over `exercise.py` and runs the tests.
- Add one alternative when it teaches something (a different idiom, a data-driven
  version, a stdlib shortcut). Give it a suffixed name and a comment saying why it is
  interesting. This mirrors Codewars' "best practice" vs "clever" views.
- Comments explain the *why*, not the *what*. Two to four lines of commentary per solution.

## meta.json

```json
{
  "title": "Normalize a hostname",
  "kyu": 8,
  "tags": ["strings", "methods"],
  "time_limit_min": 5,
  "hints": [
    "String methods return new strings, so you can chain them: raw.strip().lower()",
    "\"a.b.c\".split(\".\") gives ['a', 'b', 'c']; index [0] takes the first part.",
    "str.replace(old, new) replaces every occurrence."
  ]
}
```

- `kyu` 8 (easiest) to 3 (hardest). XP is derived from kyu, do not set it.
- `time_limit_min`: how long a prepared candidate needs in an interview. Beating it
  earns a bonus. Rough guide: 8 kyu 3–5, 7 kyu 5–10, 6 kyu 10–15, 5 kyu 15–25, 4 kyu 25–35, 3 kyu 35–50.
- `hints`: 2 to 4, progressive. First a nudge (which tool or idea), then the approach,
  last one is nearly a spoiler. Each hint costs the learner 25% of the XP.
- `tags`: 2 to 4 lowercase words. Concepts first, domain second.
- Optional `timeout_s` (default 10) if the tests legitimately need longer.

### Kyu calibration

| kyu | feels like | example |
|---|---|---|
| 8 | one or two lines, one concept | f-string, a single `if` ladder |
| 7 | a loop or a couple of string methods with an edge case | bytes to human, dedupe |
| 6 | several rules, one data structure, a few edge cases | group by key, parse a log line |
| 5 | two or more functions/classes cooperating, real edge cases | deep merge, paginated fetch |
| 4 | algorithmic thinking or state: graphs, sorting with keys, invariants | topo sort, LRU cache |
| 3 | capstone: 20–40 minutes, combines several parts | reconcile two inventories |

## LESSON.md

Match the tone and structure of `part01_foundations/LESSON.md`:

- `# Part N · Title` as the first line (the engine strips the "Part N ·" prefix).
- A blockquote "What you will be able to do" with a time estimate.
- Numbered sections with REPL snippets (`>>>`) the reader can type, short tables for
  method/idiom references, and explicit **gotchas** (the things interviewers probe).
- An "Interview notes for this part" section: what to say out loud, what to ask, the
  trap to avoid.
- An "Exercises" list mapping each exercise to the concept it drills.
- 200 to 400 lines. Teach Python; the CPE setting (MDM, Jamf, Munki, osquery, plists,
  fleet inventories, macOS and Windows endpoints, logs, package installs, compliance)
  is the example domain, not the subject. Do not explain how those tools work.
- Prefer showing the idiomatic way and then naming the non-idiomatic way people write
  in interviews and why it is worse.

## Compatibility rules

The same files run in a terminal (Python 3.9+) and in the browser (Pyodide), so:

- Python 3.9 syntax only: no `match`, no `X | Y` unions at runtime (use `Optional`,
  `Union`), no `tomllib`, no `zip(strict=True)`, no `str.removeprefix` is fine (3.9).
- Standard library only.
- Nothing that touches the network, real processes, threads, or signals. When the
  topic *is* subprocess or HTTP, the function takes an injectable `runner`/`client`/`sleep`
  callable and the tests pass a fake.
- Files only in the working directory or `tempfile`.
- Fast: every test module completes in well under a second.

## Before you are done

```
python tools/verify.py 4        # one part
python tools/verify.py          # everything
```

It must print `all good`. It checks: files present, meta valid, solution passes,
stub fails, no third-party imports, no network calls, numbering without gaps.
