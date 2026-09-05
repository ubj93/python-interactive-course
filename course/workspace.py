"""Learner answers and scratch practice, kept separate from course content."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, List, Optional

from .catalog import ROOT, Exercise, Part, all_exercises


def committed_starter(ex: Exercise, repository_root: Path = ROOT) -> Optional[bytes]:
    """Read the committed starter, without guessing whether local edits are answers."""
    try:
        root = Path(repository_root).resolve()
        top = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], cwd=str(root),
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        if Path(top).resolve() != root:
            return None
        rel = ex.exercise_file.resolve().relative_to(root).as_posix()
        return subprocess.run(
            ["git", "show", f"HEAD:{rel}"], cwd=str(repository_root),
            capture_output=True, check=True,
        ).stdout
    except (OSError, ValueError, subprocess.CalledProcessError):
        return None


def recovery_copy(path: Path) -> Path:
    """Keep an existing file under a new name; never reuse an earlier recovery copy."""
    if path.is_symlink():
        raise ValueError(f"Refusing a symbolic link: {path}")
    backup_path = path.with_name(path.name + ".bak." + uuid.uuid4().hex)
    with backup_path.open("xb") as out:
        out.write(path.read_bytes())
    return backup_path


class Workspace:
    def __init__(self, root: Optional[Path] = None, repository_root: Path = ROOT):
        self.repository_root = Path(repository_root).resolve()
        self.root = Path(root or os.environ.get("COURSE_WORKSPACE") or self.repository_root / ".course-workspace").expanduser().resolve()
        if self.root == self.repository_root:
            raise ValueError("The learner workspace must be separate from the repository root")
        for name in ("curriculum", "docs", "course", ".git"):
            source = self.repository_root / name
            if self.root == source or source in self.root.parents:
                raise ValueError(f"The learner workspace cannot be inside {source}")

    def _path(self, *parts: str) -> Path:
        target = self.root.joinpath(*parts)
        try:
            relative = target.relative_to(self.root)
        except ValueError:
            raise ValueError("Invalid learner workspace path")
        if ".." in relative.parts:
            raise ValueError("Invalid learner workspace path")
        candidate = self.root
        for part in relative.parts:
            candidate = candidate / part
            if candidate.is_symlink():
                raise ValueError(f"Refusing a symbolic link in the learner workspace: {candidate}")
        return target

    def answer_path(self, ex: Exercise) -> Path:
        return self._path("answers", ex.dir.parent.name, ex.dir.name, "exercise.py")

    def scratch_path(self, ex: Exercise) -> Path:
        return self._path("scratch", ex.dir.parent.name, ex.dir.name, "exercise.py")

    def starter(self, ex: Exercise) -> bytes:
        committed = committed_starter(ex, self.repository_root)
        return committed if committed is not None else ex.exercise_file.read_bytes()

    def ensure(self, ex: Exercise, scratch: bool = False) -> Path:
        """Create a starter only if no saved answer exists, including under races."""
        path = self.scratch_path(ex) if scratch else self.answer_path(ex)
        if path.exists():
            if not path.is_file():
                raise ValueError(f"Expected an answer file: {path}")
            return path
        source = self.starter(ex)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._path(*path.relative_to(self.root).parts)
        try:
            with path.open("xb") as out:
                out.write(source)
        except FileExistsError:
            # Another command initialized this answer; its content wins.
            pass
        return path

    def reset(self, ex: Exercise, scratch: bool = False) -> tuple:
        """Reset only the learner copy, preserving the previous answer for recovery."""
        path = self.scratch_path(ex) if scratch else self.answer_path(ex)
        source = self.starter(ex)
        saved = recovery_copy(path) if path.exists() else None
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(source)
        return path, saved

    @contextmanager
    def grading_copy(self, ex: Exercise, answer: Optional[Path] = None) -> Iterator[Exercise]:
        """Run with fresh test/fixture copies so grading cannot alter course content."""
        answer = answer or self.ensure(ex)
        try:
            answer = self._path(*answer.relative_to(self.root).parts)
        except ValueError as error:
            raise ValueError(f"Expected an answer inside the learner workspace: {answer}") from error
        learner_code = answer.read_bytes()
        helpers = []
        for helper in sorted(answer.parent.glob("*.py")):
            if helper.is_symlink():
                raise ValueError(f"Refusing a symbolic link in the learner workspace: {helper}")
            if helper.is_file() and helper.name not in ("exercise.py", "test_exercise.py"):
                helpers.append((helper.name, helper.read_bytes()))
        with tempfile.TemporaryDirectory(prefix="course-grade-") as tmp:
            directory = Path(tmp) / ex.dir.name
            directory.mkdir()
            (directory / "exercise.py").write_bytes(learner_code)
            for name, content in helpers:
                (directory / name).write_bytes(content)
            # Learner modules accompany the answer; grader tests and fixtures
            # always come from the curriculum, never from the learner directory.
            shutil.copy2(ex.test_file, directory / "test_exercise.py")
            fixtures = ex.dir / "fixtures"
            if fixtures.is_dir():
                shutil.copytree(fixtures, directory / "fixtures")
            yield Exercise(ex.part_num, ex.num, ex.slug, directory, ex.meta)

    def legacy_answers(self, catalog: List[Part]) -> list:
        """Local differences are candidates, not automatically classified learner work."""
        changes = []
        for ex in all_exercises(catalog):
            original = committed_starter(ex, self.repository_root)
            if original is not None and ex.exercise_file.read_bytes() != original:
                changes.append(ex)
        return changes

    def migrate(self, exercises: List[Exercise], restore_starters: bool = False) -> dict:
        """Explicitly copy selected legacy edits; preserve both sides of conflicts."""
        result = {"copied": [], "conflicts": [], "recoveries": [], "restored": []}
        snapshots = []
        for ex in exercises:
            original = committed_starter(ex, self.repository_root)
            if original is None:
                raise ValueError(f"Cannot identify a committed starter for {ex.id}; copy its answer manually")
            if ex.exercise_file.is_symlink():
                raise ValueError(f"Refusing a symbolic link: {ex.exercise_file}")
            current = ex.exercise_file.read_bytes()
            if current != original:
                snapshots.append((ex, original, current, self.answer_path(ex)))
        for ex, original, current, target in snapshots:
            recovery = self._path("recovery", "migration-" + uuid.uuid4().hex, ex.dir.parent.name, ex.dir.name, "exercise.py")
            recovery.parent.mkdir(parents=True, exist_ok=True)
            with recovery.open("xb") as out:
                out.write(current)
            result["recoveries"].append(str(recovery))
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                with target.open("xb") as out:
                    out.write(current)
                result["copied"].append(str(target))
            except FileExistsError:
                if target.read_bytes() != current:
                    result["conflicts"].append(str(target))
            if restore_starters:
                # Preserve a concurrent edit too: leave it untouched and ask for a new migration.
                if ex.exercise_file.read_bytes() != current:
                    raise ValueError(f"{ex.exercise_file} changed during migration; it was not reset")
                ex.exercise_file.write_bytes(original)
                result["restored"].append(str(ex.exercise_file))
        return result
