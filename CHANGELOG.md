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
