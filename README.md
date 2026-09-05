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
Commands show, open, and grade answers in the gitignored `.course-workspace/answers/`
directory. Set `COURSE_WORKSPACE` to choose another location, and keep that location
out of version control. `course path 1.1` prints the answer file to edit and creates
it only if missing. Existing answers are never replaced when the course updates.

Curriculum files are course content. Initial answers use the committed starter when
Git history is available, or the supplied starter in a downloaded copy. Grading and
the REPL use disposable copies of your answer and sibling Python modules, with
tests and fixtures supplied by the curriculum. Normal study does not modify
curriculum files or browser starters.

To practise again while keeping a saved answer and its progress:

```bash
python3 course.py path 1.1 --scratch    # edit this separate practice file
python3 course.py run 1.1 --scratch     # grade without changing XP or completion
python3 course.py reset 1.1 --scratch   # fresh practice starter; old copy is kept
```

`course reset 1.1` resets the saved learner answer and its attempt/hint state. It
keeps the old answer and progress in uniquely named `.bak.*` recovery files. Earned
XP and solved status remain intact. Scratch reset affects only scratch practice.

#### Saved review queue

After a diagnostic or exercise result, record your own confidence and a short
mistake note. Both update the same review queue. **Needs review** schedules the
next local calendar day; **confident** schedules three days later. Choose a 7- or
30-day interval when useful. These dates are suggestions, and manual practice is
always available.
Chosen intervals survive reopening a round. Editing only a diagnostic note keeps
its existing review date; changing confidence schedules a new date.

```bash
python3 course.py reflect 1.2 --confidence needs-review --note 'Strip before checking'
python3 course.py review                 # saved reflections, due work and active round
python3 course.py review start           # resume, or start the currently due exercises
python3 course.py review show            # find the scratch file for this round
python3 course.py review run             # grade it independently
python3 course.py review help            # guidance without changing lifetime hint usage
python3 course.py review reflect --confidence confident --note 'Check empty input' --interval 7
python3 course.py review finish          # keep this round in review history
python3 course.py review new 1.2         # manual fresh round, including before its due date
python3 course.py review history
```

Open **Review queue** on the browser dashboard for the same workflow. Each new
round starts from course starters; resuming keeps its scratch files and drafts.
The CLI stores them in `.course-workspace/practice/<round-id>/`, included in
workspace backups. Browser drafts and queue state travel in progress exports.
Starting another round preserves the previous round's outcomes and drafts.
Test outcomes and confidence are recorded separately; reviews never award course
completion XP or alter saved answers, original passes, or lifetime hint usage.
Ready weaknesses appear first, followed by other due work and future reviews.
Finishing a round preserves its results; record a reflection to set its next date.

#### Moving answers from older versions

Earlier versions asked learners to edit `curriculum/**/exercise.py`. Review those
local changes before migration: the course cannot distinguish a learner answer
from an intentional author edit.

```bash
python3 course.py migrate-answers                  # preview only
python3 course.py migrate-answers 1.1 --apply       # copy one legacy answer
python3 course.py migrate-answers 1.1 --apply --restore-starters
# The last command also restores that curriculum file from HEAD.
```

Omit the exercise ID to apply to every candidate shown in the preview. Migration
always saves the legacy content under `.course-workspace/recovery/`. If a workspace
answer already differs, it keeps that answer and reports the recovery path for the
legacy version. Curriculum changes are left alone unless `--restore-starters` is
explicitly supplied; the Git index is never changed. Review staged author changes
separately before committing.

Migration detects uncommitted differences from Git's `HEAD`. For answers already
committed into a starter, or a download without Git history, compare and transfer
your code into the workspace manually while retaining the original copy. Restore
clean course starters before rebuilding browser content.

Your progress and your solutions never leave your machine, and nothing about them is
committed. To keep them safe across clones and machines:

```bash
python3 course.py backup                 # zip progress + workspace to ~/course-backups/
python3 course.py backup --to ~/Dropbox/ # or anywhere you like
python3 course.py restore ~/course-backups/course-backup-20260902-101500.zip
python3 course.py restore backup.zip --list        # peek without restoring
python3 course.py restore backup.zip --force       # replace existing files, keeping unique recovery copies
```

Backups contain saved answers, scratch practice, workspace recovery copies, and progress.
Before migration, detected local curriculum edits are also included as legacy recovery
entries, even when a workspace answer already exists. When Git cannot supply a baseline,
all supplied curriculum answers are conservatively included as unverified recovery
copies. These recovery entries never replace the primary workspace answer on restore. The backup command reports their
count; inspect the archive with `restore --list` to see their recovery paths.
Restore checks all destinations before writing and refuses existing-file conflicts
unless `--force` is supplied, including with `--exercises-only`. Earlier backups
containing curriculum answer paths are restored into the learner workspace. Restore
never writes to curriculum files. Explicit backup ZIP filenames must be new; default
backup filenames are unique.

### Browser progress and code backups

In **Profile → Back up progress and code**, choose **Export** and save the JSON as a file. The versioned
backup includes all progress, exercise drafts, and guided code-card drafts, including
older positional card drafts. Diagnostic and review code, reflections, and saved path
activities travel inside progress. Keep the complete document when transferring it.

To import, paste the JSON and choose **Import**. Review the XP, solved-exercise and
draft changes, then choose **Replace progress and drafts** or **Cancel import**.
Replacement uses the incoming progress and drafts in full; it does not merge them.
A legacy progress-only JSON file instead offers **Replace progress only** and keeps
all current browser drafts. Unsupported versions and invalid data are rejected
before any saved data changes, and the pasted input stays available.

Every confirmed import first saves a complete copy of the current data. **Recovery
copies → Load recovery JSON for preview** lets you inspect and restore a previous
copy through the same confirmation flow. If storage cannot hold a recovery copy,
import stops. Failed writes restore the previous data; an interrupted import retries
recovery on reload. If storage still prevents recovery, study stays paused and the
recovery screen exposes the saved JSON and a **Retry recovery** button. Copy that
JSON to a separate file before freeing browser storage. Recovery copies stay in this
browser; export copies you need before clearing site data.

The envelope uses `format: "python-cpe-course-backup"`, `version: 1`, an `exported_at`
timestamp, nested `progress`, and a `drafts` map. Draft keys start with
`cpe-course-draft:`; exercise keys and both stable and legacy `card:` keys are opaque
identifiers, not filesystem paths. Unknown progress and envelope fields are retained.
The terminal can use the same complete JSON file directly:

```bash
COURSE_PROGRESS=/path/to/browser-backup.json python3 course.py status
COURSE_PROGRESS=/path/to/browser-backup.json python3 course.py learn
```

Terminal saves update nested progress while preserving the envelope, its metadata,
and every browser draft. Import that entire updated file back into the browser.
The CLI does not turn ordinary browser drafts into learner answer files; use the
workspace for terminal answers. Diagnostic practice still initializes its separate
copies from saved diagnostic drafts as described below. Terminal ZIP backup/restore
also preserves the complete envelope. Study commands reject invalid JSON or an
unsupported shape without rewriting the file. You can still back up the original
bytes or restore a valid ZIP with `--force`, which keeps a recovery copy of the
damaged file. Progress saves replace the file atomically after validation and a
successful temporary write. Existing plain progress files continue to use their
original format.

### Fundamentals diagnostic

Start with six untimed problems (1.2, 1.3, 2.1, 2.2, 3.1, and 5.1) to choose
which Python topics to revisit. Try each problem before guidance, or use the help
escape whenever you need it. Each exercise records its latest test outcome,
your confidence (**confident** or **needs review**), and a short mistake note.
These are reflections on this round, not a mastery score.

```bash
course diagnostic                  # start or resume the summary
course diagnostic show 1.2         # problem and separate file to edit
course diagnostic path 1.2         # print that file's path
course diagnostic run 1.2          # grade the diagnostic copy
course diagnostic help 1.2         # hints and an optional lesson link
course diagnostic reflect 1.2 --confidence needs-review --note "Strip before splitting"
course diagnostic                  # outcomes, reflections and lesson links
course diagnostic new              # fresh round; archive the previous one
course diagnostic history          # review earlier summaries
```

In the browser, choose **Fundamentals diagnostic** on the dashboard. Drafts,
confidence, and notes save as you type; the summary offers lesson links and lets
you choose what to revisit. Earlier rounds remain reviewable after starting a new
one. A passing test never chooses your confidence for you.

Diagnostic runs, help, and reflections leave ordinary exercise completion, hints,
lesson cards, and XP unchanged, including for exercises already solved. CLI work
lives in `.course-workspace/practice/<round-id>/`; existing answers and earlier
rounds are preserved. `course backup` includes these files. Browser drafts and CLI
last-run code live inside the diagnostic progress object, so progress JSON exports
include them. Importing that progress into the CLI initializes missing diagnostic
files from those drafts; an existing CLI file always wins. Save a CLI file and run
it before exporting progress to carry its latest code to the browser; a workspace
backup also preserves files that have not been run yet.

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

### Saved two-week Interview refresher

For someone who has programmed before, `course refresher` and **Refresher** in the
browser offer 14 flexible sessions of 75–90 minutes. Take as many days as you need;
there are no imposed dates. Start with lessons 1.1–1.2 if Python values and strings
are unfamiliar. Each session names its prerequisites and reuses existing lessons.

| Sessions | Focus |
|---|---|
| 1 | Fundamentals diagnostic, confidence and mistake notes |
| 2–4 | Decisions and loops; functions; dictionaries and sets |
| 5–7 | Strings and parsing; CSV/JSON; errors and validation |
| 8–9 | Basic objects and dataclasses; comprehensions and generators |
| 10–12 | Dates/subprocesses; API basics; hash maps, stacks and binary search |
| 13–14 | Stale-device-report capstone; two curated mocks and review |

```bash
python3 course.py refresher                 # saved next activity and review suggestions
python3 course.py refresher list            # all sessions and stable activity IDs
python3 course.py refresher open            # resume; show lesson/practice commands
python3 course.py refresher done            # explicitly finish the current activity
python3 course.py refresher skip            # move on, recording the skip
python3 course.py refresher revisit baseline-diagnostic
python3 course.py refresher note baseline-plan --text 'Practise dictionary defaults'
python3 course.py refresher mock mocks-a    # start or resume the same curated round
```

The browser offers the same done, skip, revisit and note controls. Path progress
travels in the normal progress backup/export, including the saved next activity.
Diagnostic failed attempts, low confidence, help use and mistake notes suggest
specific existing lessons. Suggestions never reorder the path automatically.
Passing an exercise does not finish a path activity, and marking it done does not
assert mastery or award XP. The full curriculum stays available throughout.

Timebox the review cards, concentrate on unfamiliar ideas, and extend a session
when the exercises need more practice. Decorators/closures, elaborate class
protocols, and graph/LRU problems are linked as optional extensions for interviews
that need them. The path's two 30-minute mocks select already-practised material
(5.4/10.1 and 11.1/12.1); they require fresh passing runs and resume the same active
round. Finish a different active round before starting another. Review and note
each result before proceeding: the mock tool retains only the latest finished
round. The ordinary `course interview` command still offers its broader random pool.

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
- Lesson activity also keeps the streak and earns eligible streak badges. Restarting
  a lesson replays its cards while preserving each card's first-answer reward
  history and all earned XP. Watch mode starts grading after the next file save.
- **Daily kata** picks one unsolved exercise near your frontier, deterministic per day.
- **Mock interview** picks three problems from Part 9 onward and starts a 45-minute clock.
  Every round requires fresh passing runs, including for exercises solved before.
  Credit uses each exercise's first passing time; a pass exactly at the deadline
  is on time. Finish with `course interview --finish` to retain the result, review
  it with `course interview`, and start another round with `course interview --new`.
  Starting another round also saves the previous round's result. Only the most
  recently finished result is retained; `course interview --last` shows it even
  during a new round. The browser has the same scoring and keeps that result in
  exported progress. Finishing while a browser test is still running freezes the
  round immediately; that later result counts as ordinary practice and cannot
  change the finished result or earn credit in a new round.

## Adding or editing content

Read [`curriculum/AUTHORING.md`](curriculum/AUTHORING.md). Each lesson card has a
permanent authored ID; preserve it when editing or moving the same card, and assign
a new ID to a new question. Existing positional progress and browser drafts migrate
through the frozen shipped layout, retaining old records for recovery. Then:

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

The Part 12 pilot also has public **generalization tests** for `two_sum`,
`balanced_brackets`, and `bisect_first_bad`: fixed seeds vary short inputs against
simple independent checks. To check the reference implementations and plausible
mistakes with actual Python in the browser (downloads Pyodide on first use):

```sh
python3 -m unittest discover -s tests -p test_generalization.py
COURSE_REAL_BROWSER_TESTS=1 npx playwright test generalization.spec.cjs --project=desktop
```

The same cases and seeds ship in the browser bundle. The normal browser suite
skips this optional network check; no extra Python dependencies are needed.
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
course/              engine: catalog, lessons, runner, workspace, harness, progress, backup, cli, ui
.course-workspace/   gitignored answers, scratch practice, and migration recovery copies
curriculum/          parts → lessons/ (guided cards) + exercises (stub, tests, solution, meta) + LESSON.md
docs/                browser version (index.html, worker.js, generated exercises.js)
tools/               verify.py, build_web.py
tests/               engine unit tests
```
