#!/usr/bin/env python3
"""Versioning helper.

  python tools/release.py version                 # print the current version
  python tools/release.py bump patch|minor|major  # move Unreleased notes into a new version
  python tools/release.py check [--base main]     # CI: version bumped vs base and CHANGELOG has a section
  python tools/release.py notes [VERSION]         # print the CHANGELOG section for a version
"""
from __future__ import annotations

import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INIT = ROOT / "course" / "__init__.py"
CHANGELOG = ROOT / "CHANGELOG.md"
VERSION_RE = re.compile(r'^__version__\s*=\s*"(\d+)\.(\d+)\.(\d+)"', re.M)


def read_version(text: str) -> tuple:
    m = VERSION_RE.search(text)
    if not m:
        raise SystemExit("could not find __version__ in course/__init__.py")
    return tuple(int(x) for x in m.groups())


def fmt(v: tuple) -> str:
    return ".".join(str(x) for x in v)


def current() -> tuple:
    return read_version(INIT.read_text(encoding="utf-8"))


def section(version: str, text: str) -> str:
    m = re.search(rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## \[|\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else ""


def cmd_bump(kind: str) -> int:
    major, minor, patch = current()
    if kind == "major":
        new = (major + 1, 0, 0)
    elif kind == "minor":
        new = (major, minor + 1, 0)
    elif kind == "patch":
        new = (major, minor, patch + 1)
    else:
        raise SystemExit("bump takes major, minor or patch")
    text = CHANGELOG.read_text(encoding="utf-8")
    unreleased = section("Unreleased", text)
    if not unreleased:
        raise SystemExit("CHANGELOG.md has nothing under ## [Unreleased]; write the notes first")
    today = dt.date.today().isoformat()
    text = text.replace("## [Unreleased]\n\n" + unreleased, f"## [Unreleased]\n\n## [{fmt(new)}] - {today}\n\n{unreleased}", 1)
    CHANGELOG.write_text(text, encoding="utf-8")
    INIT.write_text(VERSION_RE.sub(f'__version__ = "{fmt(new)}"', INIT.read_text(encoding="utf-8")), encoding="utf-8")
    print(f"{fmt((major, minor, patch))} -> {fmt(new)}")
    return 0


def cmd_check(base: str) -> int:
    ours = current()
    try:
        base_text = subprocess.run(["git", "show", f"{base}:course/__init__.py"], capture_output=True, text=True, check=True, cwd=ROOT).stdout
    except subprocess.CalledProcessError:
        print(f"could not read course/__init__.py from {base}; skipping version comparison")
        base_text = None
    problems = []
    if base_text is not None:
        theirs = read_version(base_text)
        if ours <= theirs:
            problems.append(f"version {fmt(ours)} is not newer than {base} ({fmt(theirs)}); run tools/release.py bump <patch|minor|major>")
    notes = section(fmt(ours), CHANGELOG.read_text(encoding="utf-8"))
    if not notes:
        problems.append(f"CHANGELOG.md has no '## [{fmt(ours)}]' section")
    if problems:
        for p in problems:
            print("  - " + p)
        return 1
    print(f"version {fmt(ours)} with changelog notes: ok")
    return 0


def main(argv: list) -> int:
    if not argv or argv[0] == "version":
        print(fmt(current()))
        return 0
    if argv[0] == "bump":
        return cmd_bump(argv[1] if len(argv) > 1 else "")
    if argv[0] == "check":
        base = "origin/main"
        if "--base" in argv:
            base = argv[argv.index("--base") + 1]
        return cmd_check(base)
    if argv[0] == "notes":
        v = argv[1] if len(argv) > 1 else fmt(current())
        print(section(v, CHANGELOG.read_text(encoding="utf-8")))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
