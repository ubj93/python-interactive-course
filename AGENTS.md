# Project working instructions

## Product backlog

Todoist is the authoritative product backlog for this project, as requested by the
user. Use the personal **Python Interactive Course** project:
https://app.todoist.com/app/project/6hQCc7vr8jPJ4VV3

- Project ID: `6hQCc7vr8jPJ4VV3`.
- Backlog: `6hQCc8HxrWJMRrfV`.
- In progress: `6hQCc8JWXhgq2q43`.
- In review (PR open): `6hQCc8JMpjcH637V`.
- Done: `6hQCc8HcVg45fQRV`.

Before starting product work, find the relevant Todoist task and read its scope,
acceptance criteria, priority and dependencies. Update an existing task when it
already covers the work; otherwise create one for an authorized implementation or
stage a new idea in Backlog. Keep tasks small enough for a focused pull request.
Backlog presence alone is not authorization to implement every item.

Use Todoist for product priorities, feature ideas, defects and delivery status.
Do not maintain a competing backlog in repository TODO/ROADMAP files, GitHub Issues,
or Codex tasks. Temporary implementation plans and technical documentation are fine;
link them to the Todoist task when useful. GitHub remains the home for code, pull
requests, reviews and releases.

Move a task to In progress when implementation begins and In review (PR open) when
a pull request exists. Add the PR link, validation results and any remaining work to
the task description. Move it to Done only after the change is merged and its
release tag exists; record the release link. Preserve unrelated study schedules.

Keep tracking current as scope changes. If Todoist is unavailable, report the sync
gap and continue already-authorized work where possible; do not invent a second
backlog or claim a Todoist update succeeded. Tracking does not add a permission gate.

## Repository workflow

Follow the development workflow in README.md: branch from main using `codex/` by
default, make changes through a pull request, add CHANGELOG.md notes under
Unreleased, and perform the version bump before merging. Run checks appropriate to
the change. Do not commit directly to main.
