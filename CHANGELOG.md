# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versions follow
[Semantic Versioning](https://semver.org/): MAJOR for changes that break saved progress
or the exercise format, MINOR for new parts, exercises, or commands, PATCH for fixes
and wording.

Every pull request adds its notes under **Unreleased**. Before merging, run
`python3 tools/release.py bump <major|minor|patch>`, which moves those notes into a
dated version section and updates `course/__init__.py`. Merging to `main` tags the
release automatically.

## [Unreleased]

## [0.9.0] - 2026-09-05

### Added
- Export and restore versioned browser backups containing progress and code
  drafts, with an import preview, explicit replacement and complete recovery copies.
- Preserve browser drafts and metadata when updating exported progress in the CLI.

### Fixed
- Recover interrupted browser imports before further changes, and save unrun
  code-card drafts as they are typed.
- Write terminal progress atomically, preserving original bytes on failure, and
  keep backup/restore available when current progress is malformed.

## [0.8.0] - 2026-09-05

### Added
- Save confidence, mistake notes and next-review dates in one queue shared by
  diagnostic reflections and ordinary exercise practice, with optional 7/30-day
  intervals and manual revisits.
- Resume untimed review rounds in fresh scratch work, keeping drafts, outcomes
  and history separate from saved answers, original passes and completion XP.

## [0.7.0] - 2026-09-05

### Added
- Follow a saved Interview refresher path through 14 flexible sessions, with
  prerequisites, diagnostic review suggestions, optional topics and curated mocks.
- Resume, skip or revisit activities and keep personal notes independently of
  course completion and XP in both the browser and CLI.

## [0.6.0] - 2026-09-05

### Added
- Start an untimed six-exercise fundamentals diagnostic with fresh attempts,
  saved code, optional help, confidence and mistake notes in the browser and CLI.
- Resume a diagnostic summary with links to relevant lessons, preserving prior
  diagnostic rounds separately from course completion, hints and XP.

## [0.5.0] - 2026-09-05

### Added
- Give all lesson cards stable authored IDs and validate their uniqueness, so
  answers and code drafts follow the same card when lessons are reorganized.
- Migrate positional progress and reward history using the frozen shipped layout,
  preserve original records and drafts for recovery, and prefer existing stable
  records when both versions exist.

## [0.4.1] - 2026-09-05

### Fixed
- Keep each lesson card's first-answer reward history through retries, restart,
  reload and progress import, preserving earned XP without repeated awards.
- Award streak milestones for lesson activity, failed exercise attempts and
  solved-exercise retries. Verify watch waits for a learner file save before grading.

## [0.4.0] - 2026-09-05

### Added
- Keep saved answers and scratch practice in a separate learner workspace; grade
  disposable copies with the course's tests and fixtures, including learner helper
  modules. Add explicit, recoverable migration for older answers in curriculum.

### Fixed
- Back up workspace answers, scratch work and legacy recovery copies. Preflight
  restores, preserve overwritten files, and keep recovery files out of Git.
- Isolate backup tests from real curriculum and learner files.

## [0.3.5] - 2026-09-05

### Fixed
- Score mock interviews from fresh attempts in the current round, including
  previously solved exercises, while preserving lifetime completions and XP.
- Save the latest finished round and grade deadline credit by the first passing
  attempt time. Resume active rounds and migrate legacy sessions safely across
  terminal and browser progress.
- Preserve session boundaries while browser tests run and handle invalid or
  extreme timestamps without losing a round's recorded results.

## [0.3.4] - 2026-09-05

### Fixed
- Share UTC timestamp handling between terminal and browser progress, including
  existing local timestamps and explicit offsets. Imported progress can pass
  exercises without crashing; invalid or future start times earn no speed bonus.
- Use the device's local calendar day for streaks, daily kata and solved-today
  counts while preserving existing completions, XP and day history.

## [0.3.3] - 2026-09-05

### Fixed
- Continue a passed guided exercise through its own lesson's remaining recap;
  reopening completed lessons now shows completion. Preserve skipped exercises and
  resume correctly after reloads, including exercises solved before the lesson.

### Added
- Isolated browser navigation regressions in CI at desktop and mobile sizes.

## [0.3.2] - 2026-09-05

### Changed
- Enable and document main-branch protection: require pull requests, current Python
  3.9/3.12 verification and version checks, and resolved review conversations,
  including for administrators. Disable force pushes and branch deletion.

## [0.3.1] - 2026-09-04

### Changed
- Make Todoist the authoritative product backlog in the README and repository agent
  instructions, including task reuse, PR/release links and delivery status rules.

## [0.3.0] - 2026-09-02

### Added
- Guided lessons: every exercise is now reached through a sequence of bite-sized
  cards (teach, quiz, predict-the-output, fill-in-the-blank, recap) that end in the
  exercise, in the style of Mimo. 88 lessons in `curriculum/*/lessons/`.
- `course learn` (interactive, resumable; `--list`, `--show`, `--restart`) and a
  browser Learn flow with progress dots, two tries per check, and explanations.
- Card checks earn 1 xp on a correct first answer; ranks now include card xp.
- Authoring guide section for lesson cards; the verifier validates card structure and
  that every exercise is reached by exactly one lesson.

### Changed
- Home screens lead with "Continue learning"; the exercise list is now "Practice".
- `course lesson` and the site's "Reference chapter" keep the long-form chapters.

## [0.2.0] - 2026-09-02

### Added
- `course backup` and `course restore`: zip the progress file and every edited
  `exercise.py` (only files that differ from the committed stub) to `~/course-backups/`
  or a chosen path, and restore them with `.bak` copies of anything overwritten.
  Restore refuses to overwrite an existing progress file without `--force` and ignores
  paths outside `curriculum/`.

## [0.1.1] - 2026-09-02

### Added
- `pages` workflow: enables GitHub Pages and deploys the browser version from `docs/`
  on every merge to `main`, rebuilding the exercise bundle first.

### Changed
- README points at the live site.

## [0.1.0] - 2026-09-02

### Added
- Course engine (`course/`): catalog discovery, subprocess test harness with per-test
  results and trimmed tracebacks, progress with XP, kyu ranks, streaks, badges, daily
  kata, and timed mock interviews. CLI: `status`, `list`, `show`, `next`, `run`,
  `watch`, `hint`, `solution`, `lesson`, `daily`, `interview`, `badges`, `reset`, `repl`.
- Browser version (`docs/`): the same harness running in Pyodide inside a web worker,
  CodeMirror editor, progress in `localStorage` with export/import compatible with the
  CLI's progress file.
- Curriculum: 13 parts, 88 auto-graded exercises with lessons, hints, and reference
  solutions, from foundations to timed Client Platform Engineering capstones.
- Tooling: `tools/verify.py` (solutions pass, stubs fail, metadata valid),
  `tools/build_web.py`, engine unit tests, CI on Python 3.9 and 3.12, release tagging
  on merge to `main`, git hooks that block direct commits and pushes to `main`.
