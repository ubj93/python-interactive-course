# Python for Client Platform Engineering

An interactive, auto-graded Python course for people preparing for **Client Platform
Engineering (CPE) coding interviews**. It sits at the intersection of two things that
are hard to find together:

- the **substance** of a university course (University of Helsinki's Python MOOC, MIT
  6.0001): real lessons, a deliberate order of concepts, exercises that build on each
  other;
- the **feedback loop** of Codewars, Mimo, and Exercism: every exercise is graded the
  second you run it, you earn XP and kyu ranks, keep a streak, get a daily kata, and
  see "best practice" vs "clever" reference solutions after you pass.

Every example and exercise is set in the CPE world: fleets of Macs and Windows boxes,
MDM check-ins, serial numbers, plists, syslog, package manifests, REST APIs with
pagination and rate limits. The subject is Python; the setting is the job.

Runs anywhere Python 3.9+ runs. Zero dependencies. Also runs entirely in the browser,
including on a phone.

## How a lesson works

Each exercise is reached through a **guided lesson**: a handful of short cards in the
style of Mimo. A card teaches one idea in plain words with a snippet, the next card
checks it (multiple choice, "what does this print?", or fill in the blank), and the
lesson ends with a real exercise that puts the ideas together. Correct first answers
earn XP; a wrong answer gets a second try, then the explanation. Every part also has a
full reference chapter for when you want the whole picture.

```
Lesson 1.3 · Making decisions          9 cards · ends in exercise 1.3
  1 learn     if, elif, else
  2 predict   What does this print?  →  WARN
  3 learn     Order matters
  4 learn     Comparisons, and the special value None
  5 quiz      Which expression is true only between 0 and 1?
  6 fill      if used ___ None:
  7 learn     Return early
  8 exercise  1.3 Classify disk usage
  9 recap
```

## Two ways to use it

### Terminal (the main experience)

```bash
git clone https://github.com/ubj93/python-interactive-course
cd python-interactive-course
python3 course.py            # dashboard: rank, xp, streak, progress per part
python3 course.py learn      # guided lesson: cards, checks, then the exercise (resumes where you left off)
python3 course.py learn --list   # all lessons and progress
python3 course.py lesson 1   # the reference chapter for Part 1
python3 course.py next       # show the next unsolved exercise (practice mode)
# edit the file it names, then:
python3 course.py run        # auto-grade the last exercise you opened
python3 course.py watch 1.2  # re-run on every save
python3 course.py hint 1.2   # progressive hints (each costs 25% of the xp)
python3 course.py solution 1.2   # reference solutions, unlocked once you pass
python3 course.py daily      # today's kata (+5 xp bonus)
python3 course.py interview  # timed mock interview: 3 random problems, 45 minutes
```

Tip: `alias course='python3 /path/to/course.py'`. Progress is stored in
`.course_progress.json` (gitignored; set `COURSE_PROGRESS` to put it elsewhere).

Your progress and your solutions never leave your machine, and nothing about them is
committed. To keep them safe across clones and machines:

```bash
python3 course.py backup                 # zip progress + every edited exercise to ~/course-backups/
python3 course.py backup --to ~/Dropbox/ # or anywhere you like
python3 course.py restore ~/course-backups/course-backup-20260902-101500.zip
python3 course.py restore backup.zip --list        # peek without restoring
python3 course.py restore backup.zip --force       # overwrite an existing progress file (kept as .bak)
```

A backup only contains files that differ from the committed stubs, so restoring never
touches exercises you have not started.

### Browser

Live at **https://ubj93.github.io/python-interactive-course/** (deployed from `docs/`
by the `pages` workflow on every merge to `main`). Python runs in the browser via
Pyodide, so it works in mobile Safari for the daily kata on the train. To run it
locally, serve the `docs/` folder with any static server. Progress lives in `localStorage` and
can be exported and imported to move between devices or merged with the terminal file
(same JSON format).

Both clients write timestamps in UTC (`2026-09-05T00:30:00.000Z`). Existing terminal
timestamps without an offset are interpreted as local time on the device reading
them. Streaks, daily katas and "solved today" use the device's local calendar date;
importing progress preserves existing day keys and completions. Invalid or future
start times do not earn a speed bonus.

```bash
python3 tools/build_web.py           # regenerate docs/exercises.js after editing content
python3 -m http.server -d docs 8000  # then open http://localhost:8000
```

## What is in the course

Thirteen parts, 88 guided lessons, 88 exercises graded from 8 kyu (warm-up) to 3 kyu
(40-minute capstones). Full plan in [`curriculum/SYLLABUS.md`](curriculum/SYLLABUS.md).

| Part | Topic | What it drills |
|---|---|---|
| 1 | Foundations | values, strings, f-strings, conditionals |
| 2 | Loops and lists | for/while, slicing, sorting with keys, running-best |
| 3 | Functions and modules | defaults, `*args/**kwargs`, closures, higher-order functions |
| 4 | Strings and regex | parsing log lines, versions, IPs; `re` done right |
| 5 | Dicts and sets | counting, grouping, inversion, set algebra, deep merge |
| 6 | Files and data formats | pathlib, JSON, CSV, plists, streaming large files |
| 7 | Errors and robustness | exceptions, custom errors, validation, retry decorator |
| 8 | Classes and dataclasses | `__repr__`/`__eq__`, dataclasses, enums, comparable versions, rate limiter |
| 9 | Comprehensions and iterators | generators, itertools, heapq, multi-key sorts |
| 10 | Standard-library toolkit | datetime, argparse, hashlib, subprocess (injected), collections |
| 11 | HTTP APIs | pagination, backoff, rate limits, webhook signatures, state sync |
| 12 | Interview patterns | hash map, two pointers, sliding window, stack, binary search, topo sort, LRU |
| 13 | Capstones | timed, realistic CPE take-home problems |

Suggested pace for someone who has programmed before: Parts 1–5 in the first week,
6–9 in the second, 10–12 in the third, capstones and mock interviews in the fourth.
Pair it with one Exercism session a week for human feedback.

## How grading works

Each exercise folder has a stub (`exercise.py`), a `unittest` suite, reference
solutions, and metadata. The runner executes the tests in a subprocess with a timeout,
shows each test's one-line description, and trims tracebacks down to your code.

- **XP** comes from difficulty (8 kyu = 2 xp … 3 kyu = 149 xp, Codewars' curve), plus
  1 xp for every lesson card answered correctly on the first try.
- **Bonuses**: first-try pass ×1.25, inside the time limit ×1.1. **Penalties**: each
  hint −25%, peeking at the solution before passing ×0.1.
- **Rank** is your share of the total XP: 8 kyu Help Desk → 1 kyu Principal CPE.
- **Streaks** count days with at least one test run. **Badges** for milestones.
- **Daily kata** picks one unsolved exercise near your frontier, deterministic per day.
- **Mock interview** picks three problems from Part 9 onward and starts a 45-minute clock.

## Adding or editing content

Read [`curriculum/AUTHORING.md`](curriculum/AUTHORING.md). Then:

```bash
python3 tools/verify.py        # every solution passes, every stub fails, metadata valid
python3 -m unittest discover -s tests   # engine tests
python3 tools/build_web.py     # refresh the browser bundle
```

CI runs all three on Python 3.9 and 3.12. Browser navigation regressions also run
in Chromium at desktop and mobile viewport sizes:

```bash
npm ci --ignore-scripts                 # development tools only; Node 20+
npx playwright install chromium        # once per machine
npm run test:browser
```

These tests use an isolated browser profile and a deterministic worker response;
the Python checks above verify exercise grading. They never edit learner answers.
To use an installed Google Chrome locally, run
`PLAYWRIGHT_CHROMIUM_CHANNEL=chrome npm run test:browser`.

## Development workflow

**Nothing is committed to `main` directly.** Every change lands through a pull request.

1. Install the guard hooks once: `sh tools/install-hooks.sh`. They refuse commits and
   pushes to `main` locally. GitHub also protects `main`: changes require a PR,
   up-to-date successful `verify (3.9)`, `verify (3.12)` and `version` checks, and
   resolved review conversations. The rule applies to administrators too; force
   pushes and branch deletion are disabled. Independent review is part of the
   workflow; a separate approving GitHub account is not required.
2. Branch from `main`, make the change, add a note under **Unreleased** in
   [`CHANGELOG.md`](CHANGELOG.md).
3. Bump the version before merging: `python3 tools/release.py bump patch|minor|major`.
   This moves the Unreleased notes into a dated section and updates
   `course/__init__.py`. The `version` CI job on the PR fails if the version is not
   newer than `main` or the changelog section is missing.
4. Open the PR with detailed notes (what changed, why, how it was verified).
5. On merge, the `release` workflow tags `vX.Y.Z` and publishes a GitHub Release whose
   body is that changelog section. Every merge to `main` is therefore a versioned,
   documented release.

Versioning: MAJOR when saved progress or the exercise format breaks, MINOR for new
parts, exercises, or commands, PATCH for fixes and wording.

**Todoist is the authoritative product backlog**, in the personal
[*Python Interactive Course* project](https://app.todoist.com/app/project/6hQCc7vr8jPJ4VV3).
Use the board workflow: Backlog → In progress → In review (PR open) → Done.
Keep priorities, scope, acceptance criteria, dependencies and delivery status there,
with one task per PR-sized change. Update existing tasks instead of creating
duplicates, and link each task to its PR and validation results. Move it to
"In review" when the PR opens and "Done" after merging and confirming the release
tag. GitHub is for code, PRs and releases; do not maintain a parallel product backlog
in GitHub Issues, repository TODO/ROADMAP files or Codex tasks. Agent instructions
and the Todoist project/section IDs are in [`AGENTS.md`](AGENTS.md).

## Layout

```
course.py            entry point
course/              engine: catalog, lessons, runner, harness, progress, backup, cli, ui
curriculum/          parts → lessons/ (guided cards) + exercises (stub, tests, solution, meta) + LESSON.md
docs/                browser version (index.html, worker.js, generated exercises.js)
tools/               verify.py, build_web.py
tests/               engine unit tests
```
