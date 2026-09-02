"""Back up and restore learner state: the progress file plus every edited exercise.

A backup is a zip archive containing:

    manifest.json               what is inside, when it was made, course version
    progress.json               the progress file (xp, solved, streaks, badges)
    curriculum/<part>/<ex>/exercise.py   every exercise.py that differs from the stub in git

Only files that differ from the committed stub are included, so a backup stays small
and restoring never touches exercises you have not started.
"""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import zipfile
from pathlib import Path
from typing import List, Optional, Tuple

from . import __version__
from .catalog import ROOT, Exercise, Part, all_exercises

DEFAULT_DIR = Path.home() / "course-backups"


def _git_stub(ex: Exercise) -> Optional[str]:
    """The committed version of exercise.py, or None if git cannot tell us."""
    try:
        rel = ex.exercise_file.relative_to(ROOT).as_posix()
        return subprocess.run(
            ["git", "show", f"HEAD:{rel}"], capture_output=True, text=True, cwd=str(ROOT), check=True
        ).stdout
    except (subprocess.CalledProcessError, OSError, ValueError):
        return None


def edited_exercises(catalog: List[Part]) -> List[Exercise]:
    """Exercises whose exercise.py differs from the stub committed in git."""
    out = []
    for ex in all_exercises(catalog):
        stub = _git_stub(ex)
        current = ex.exercise_file.read_text(encoding="utf-8")
        if stub is None or stub != current:
            out.append(ex)
    return out


def backup(catalog: List[Part], progress_path: Path, dest: Optional[Path] = None) -> Tuple[Path, int, bool]:
    """Write a backup zip. Returns (path, edited_exercise_count, progress_included)."""
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    if dest is None:
        dest = DEFAULT_DIR / f"course-backup-{stamp}.zip"
    elif dest.is_dir() or dest.suffix.lower() != ".zip":
        # Anything that is not an explicit .zip file name is treated as a directory.
        dest = Path(dest) / f"course-backup-{stamp}.zip"
    dest.parent.mkdir(parents=True, exist_ok=True)

    edited = edited_exercises(catalog)
    manifest = {
        "created": dt.datetime.now().replace(microsecond=0).isoformat(),
        "course_version": __version__,
        "progress": progress_path.exists(),
        "exercises": [ex.exercise_file.relative_to(ROOT).as_posix() for ex in edited],
    }
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))
        if progress_path.exists():
            zf.write(progress_path, "progress.json")
        for ex in edited:
            zf.write(ex.exercise_file, ex.exercise_file.relative_to(ROOT).as_posix())
    return dest, len(edited), progress_path.exists()


def inspect(archive: Path) -> dict:
    with zipfile.ZipFile(archive) as zf:
        return json.loads(zf.read("manifest.json"))


def restore(archive: Path, progress_path: Path, force: bool = False, exercises_only: bool = False, progress_only: bool = False) -> dict:
    """Restore a backup. Refuses to overwrite an existing progress file unless force=True.

    Existing files that would be overwritten are first copied to ``<name>.bak``.
    Returns a summary dict with the files written.
    """
    written = {"progress": None, "exercises": [], "skipped": []}
    with zipfile.ZipFile(archive) as zf:
        names = set(zf.namelist())
        if "manifest.json" not in names:
            raise ValueError("not a course backup: manifest.json missing")
        manifest = json.loads(zf.read("manifest.json"))

        if not exercises_only and "progress.json" in names:
            if progress_path.exists() and not force:
                raise FileExistsError(
                    f"{progress_path} already exists; pass --force to overwrite it "
                    "(a copy is kept as .bak)"
                )
            if progress_path.exists():
                progress_path.with_suffix(progress_path.suffix + ".bak").write_bytes(progress_path.read_bytes())
            progress_path.parent.mkdir(parents=True, exist_ok=True)
            progress_path.write_bytes(zf.read("progress.json"))
            written["progress"] = str(progress_path)

        if not progress_only:
            for rel in manifest.get("exercises", []):
                if rel not in names:
                    written["skipped"].append(rel)
                    continue
                # Guard against path traversal: only curriculum/**/exercise.py is allowed.
                parts = Path(rel).parts
                if parts[0] != "curriculum" or parts[-1] != "exercise.py" or ".." in parts:
                    written["skipped"].append(rel)
                    continue
                target = ROOT / rel
                if not target.parent.exists():
                    written["skipped"].append(rel)
                    continue
                if target.exists():
                    target.with_suffix(".py.bak").write_bytes(target.read_bytes())
                target.write_bytes(zf.read(rel))
                written["exercises"].append(rel)
    return written
