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

## Two ways to use it

### Terminal (the main experience)

```bash
git clone https://github.com/ubj93/python-interactive-course
cd python-interactive-course
python3 course.py            # dashboard: rank, xp, streak, progress per part
python3 course.py lesson 1   # read the lesson for Part 1
python3 course.py next       # show the next unsolved exercise
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

### Browser

Live at **https://ubj93.github.io/python-interactive-course/** (deployed from `docs/`
by the `pages` workflow on every merge to `main`). Python runs in the browser via
Pyodide, so it works in mobile Safari for the daily kata on the train. To run it
locally, serve the `docs/` folder with any static server. Progress lives in `localStorage` and
can be exported and imported to move between devices or merged with the terminal file
(same JSON format).

```bash
python3 tools/build_web.py           # regenerate docs/exercises.js after editing content
python3 -m http.server -d docs 8000  # then open http://localhost:8000
```

## What is in the course

Thirteen parts, 88 exercises, graded from 8 kyu (warm-up) to 3 kyu (40-minute
capstones). Full plan in [`curriculum/SYLLABUS.md`](curriculum/SYLLABUS.md).

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

- **XP** comes from difficulty (8 kyu = 2 xp … 3 kyu = 149 xp, Codewars' curve).
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

CI runs all three on Python 3.9 and 3.12.

## Development workflow

**Nothing is committed to `main` directly.** Every change lands through a pull request.

1. Install the guard hooks once: `sh tools/install-hooks.sh`. They refuse commits and
   pushes to `main` locally. Add a branch protection rule on GitHub for the server side
   (require a PR and green CI).
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

**Backlog** lives in Todoist, project *Python Interactive Course* (board view: Backlog
→ In progress → In review (PR open) → Done). One task per PR-sized change; move it
to "In review" when the PR opens and "Done" when the release tag exists.

## Layout

```
course.py            entry point
course/              engine: catalog, runner, harness, progress, cli, ui
curriculum/          parts → exercises (stub, tests, solution, meta) + LESSON.md
docs/                browser version (index.html, worker.js, generated exercises.js)
tools/               verify.py, build_web.py
tests/               engine unit tests
```
