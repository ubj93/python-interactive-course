"""Back up learner progress, answers, scratch work and recoverable copies.

New archives store learner files under ``workspace/``. Legacy curriculum answer
entries are restored into the learner workspace, never into course source files.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import stat
import uuid
import zipfile
from pathlib import Path
from typing import List, Optional, Tuple

from . import __version__
from .catalog import Part, all_exercises, load_catalog
from .workspace import Workspace, committed_starter, recovery_copy
from .practice import SESSION_ID

DEFAULT_DIR = Path.home() / "course-backups"
_FILE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]*\.py(?:\.bak\.[a-f0-9]{32})*")
_MIGRATION = re.compile(r"migration-[a-f0-9]{32}")


def _parts(name: str) -> tuple:
    if not isinstance(name, str) or not name or "\\" in name or "\0" in name:
        raise ValueError(f"Invalid archive path: {name!r}")
    parts = tuple(name.split("/"))
    if any(part in ("", ".", "..") or ":" in part for part in parts):
        raise ValueError(f"Unsafe archive path: {name!r}")
    return parts


def _workspace_file(parts: tuple, known: dict) -> bool:
    """Accept only Python work associated with a known course exercise."""
    if len(parts) == 4 and parts[0] in ("answers", "scratch"):
        pair = parts[1:3]
    elif len(parts) == 5 and parts[0] == "practice" and SESSION_ID.fullmatch(parts[1]):
        pair = parts[2:4]
    elif len(parts) == 5 and parts[0] == "recovery" and _MIGRATION.fullmatch(parts[1]):
        pair = parts[2:4]
    else:
        return False
    return pair in known and bool(_FILE.fullmatch(parts[-1]))


def _workspace_target(workspace: Workspace, parts: tuple) -> Path:
    target = workspace.root.joinpath(*parts)
    candidate = workspace.root
    if candidate.is_symlink():
        raise ValueError(f"Refusing a symbolic link: {candidate}")
    for part in parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise ValueError(f"Refusing a symbolic link: {candidate}")
    return target


def _check_target(target: Path) -> None:
    if target.is_symlink():
        raise ValueError(f"Refusing a symbolic link: {target}")
    if target.exists() and not target.is_file():
        raise ValueError(f"Expected a regular file: {target}")
    for parent in target.parents:
        if parent.exists():
            if not parent.is_dir():
                raise ValueError(f"Expected a directory: {parent}")
            break


def _catalog_entries(catalog: List[Part]) -> dict:
    return {(ex.dir.parent.name, ex.dir.name): ex for ex in all_exercises(catalog)}


def backup(catalog: List[Part], progress_path: Path, dest: Optional[Path] = None,
           workspace: Optional[Workspace] = None) -> Tuple[Path, int, bool]:
    """Create an archive exclusively; return (path, learner_file_count, progress)."""
    workspace = workspace or Workspace()
    known = _catalog_entries(catalog)
    files = []
    _workspace_target(workspace, ())
    if workspace.root.exists():
        for path in sorted(workspace.root.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"Refusing a symbolic link in the learner workspace: {path}")
            parts = path.relative_to(workspace.root).parts
            if path.is_file() and _workspace_file(parts, known):
                _workspace_target(workspace, parts)
                files.append(("workspace/" + "/".join(parts), path.read_bytes()))
    # Until migration is applied, the only copy of an older answer may still be
    # in curriculum. Without a Git baseline, preserve the source conservatively.
    # These snapshots are recovery content, never replacements for primary answers.
    legacy_recoveries = []
    migration = "migration-" + uuid.uuid4().hex
    for ex in all_exercises(catalog):
        if ex.exercise_file.is_symlink():
            raise ValueError(f"Refusing a symbolic link: {ex.exercise_file}")
        baseline = committed_starter(ex, workspace.repository_root)
        current = ex.exercise_file.read_bytes()
        if baseline is not None and current == baseline:
            continue
        name = "/".join(("workspace", "recovery", migration,
                         ex.dir.parent.name, ex.dir.name, "exercise.py"))
        files.append((name, current))
        legacy_recoveries.append(name)
    has_progress = progress_path.exists()
    progress = progress_path.read_bytes() if has_progress else None
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"course-backup-{stamp}-{uuid.uuid4().hex}.zip"
    if dest is None:
        dest = DEFAULT_DIR / filename
    else:
        dest = Path(dest)
        if dest.is_dir() or dest.suffix.lower() != ".zip":
            dest = dest / filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "format": 2,
        "created": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "course_version": __version__,
        "progress": has_progress,
        "exercises": [name for name, data in files],
        "legacy_recoveries": legacy_recoveries,
    }
    # Exclusive creation is deliberate: an explicit archive path is never replaced.
    with zipfile.ZipFile(dest, "x", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))
        if has_progress:
            zf.writestr("progress.json", progress)
        for name, data in files:
            zf.writestr(name, data)
    return dest, len(files), has_progress


def _manifest(data: bytes) -> dict:
    manifest = json.loads(data)
    if not isinstance(manifest, dict) or not isinstance(manifest.get("exercises", []), list):
        raise ValueError("Invalid backup manifest")
    entries = set()
    for name in manifest.get("exercises", []):
        _parts(name)
        if name in entries:
            raise ValueError(f"Duplicate manifest entry: {name}")
        entries.add(name)
    return manifest


def inspect(archive: Path) -> dict:
    with zipfile.ZipFile(archive) as zf:
        if "manifest.json" not in zf.namelist():
            raise ValueError("not a course backup: manifest.json missing")
        return _manifest(zf.read("manifest.json"))


def restore(archive: Path, progress_path: Path, force: bool = False,
            exercises_only: bool = False, progress_only: bool = False,
            catalog: Optional[List[Part]] = None,
            workspace: Optional[Workspace] = None) -> dict:
    """Preflight the complete restore before writing any files.

    Every existing destination requires ``force``, including learner-only restores.
    Forced replacement first preserves each file in a unique sibling recovery copy.
    Unknown course exercises are skipped; unsafe archive paths are rejected.
    """
    if exercises_only and progress_only:
        raise ValueError("Choose either --exercises-only or --progress-only")
    workspace = workspace or Workspace()
    known = _catalog_entries(load_catalog() if catalog is None else catalog)
    written = {"progress": None, "exercises": [], "skipped": [], "recoveries": []}
    staged = []
    with zipfile.ZipFile(archive) as zf:
        names = set()
        for info in zf.infolist():
            _parts(info.filename[:-1] if info.is_dir() else info.filename)
            if info.filename in names:
                raise ValueError(f"Duplicate archive entry: {info.filename}")
            names.add(info.filename)
            kind = stat.S_IFMT(info.external_attr >> 16)
            if kind not in (0, stat.S_IFREG, stat.S_IFDIR):
                raise ValueError(f"Not a regular archive file: {info.filename}")
            if kind == stat.S_IFDIR and not info.is_dir():
                raise ValueError(f"Directory masquerading as an archive file: {info.filename}")
        if "manifest.json" not in names:
            raise ValueError("not a course backup: manifest.json missing")
        manifest = _manifest(zf.read("manifest.json"))
        entries = manifest.get("exercises", [])
        if not exercises_only and "progress.json" in names:
            data = zf.read("progress.json")
            if not isinstance(json.loads(data), dict):
                raise ValueError("Invalid progress data: expected a JSON object")
            staged.append(("progress", "progress.json", Path(progress_path), data, None))
        if not progress_only:
            for name in entries:
                parts = _parts(name)
                target_parts = None
                if len(parts) == 4 and parts[0] == "curriculum" and parts[-1] == "exercise.py":
                    ex = known.get(parts[1:3])
                    if ex is not None:
                        target_parts = ("answers", ex.dir.parent.name, ex.dir.name, "exercise.py")
                elif parts[0] == "workspace" and _workspace_file(parts[1:], known):
                    target_parts = parts[1:]
                if target_parts is None or name not in names:
                    written["skipped"].append(name)
                    continue
                target = _workspace_target(workspace, target_parts)
                staged.append(("exercises", name, target, zf.read(name), target_parts))

    # Check all collisions and destinations after reading every selected member, so
    # a late conflict or corrupt archive cannot leave progress partially restored.
    targets = set()
    for kind, name, target, data, parts in staged:
        _check_target(target)
        key = target.resolve().as_posix().casefold()
        if key in targets:
            raise ValueError(f"Duplicate restore destination: {target}")
        if any(key.startswith(other + "/") or other.startswith(key + "/") for other in targets):
            raise ValueError(f"Conflicting file and directory destinations: {target}")
        targets.add(key)
        if target.exists() and not force:
            raise FileExistsError(f"{target} already exists; pass --force to replace it with a recoverable copy")
    for kind, name, target, data, parts in staged:
        if target.exists():
            written["recoveries"].append(str(recovery_copy(target)))
    for kind, name, target, data, parts in staged:
        target.parent.mkdir(parents=True, exist_ok=True)
        if parts is not None:
            _workspace_target(workspace, parts)
        _check_target(target)
        with target.open("wb" if force else "xb") as out:
            out.write(data)
        if kind == "progress":
            written["progress"] = str(target)
        else:
            written["exercises"].append(name)
    return written
