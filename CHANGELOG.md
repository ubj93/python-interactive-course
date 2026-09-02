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
