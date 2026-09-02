"""Run an exercise's tests in an isolated subprocess and parse the result."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .catalog import Exercise
from .harness import SENTINEL

HARNESS = Path(__file__).resolve().parent / "harness.py"


@dataclass
class TestCase:
    name: str
    doc: str
    status: str  # pass | fail | error | skip
    message: str = ""
    traceback: str = ""


@dataclass
class RunResult:
    tests: List[TestCase] = field(default_factory=list)
    import_error: Optional[str] = None
    stdout: str = ""
    timed_out: bool = False
    crashed: str = ""

    @property
    def passed(self) -> int:
        return sum(1 for t in self.tests if t.status == "pass")

    @property
    def total(self) -> int:
        return sum(1 for t in self.tests if t.status != "skip")

    @property
    def ok(self) -> bool:
        return (
            not self.timed_out
            and not self.crashed
            and self.import_error is None
            and self.total > 0
            and self.passed == self.total
        )


def run_tests(ex: Exercise, python: str = sys.executable, timeout: Optional[int] = None) -> RunResult:
    timeout = timeout or ex.timeout_s
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        proc = subprocess.run(
            [python, str(HARNESS), str(ex.dir)],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            cwd=str(ex.dir),
        )
    except subprocess.TimeoutExpired as e:
        res = RunResult(timed_out=True)
        res.stdout = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        return res

    res = RunResult()
    combined = proc.stdout
    if SENTINEL not in combined:
        res.crashed = (proc.stderr or "").strip() or f"harness exited with code {proc.returncode}"
        res.stdout = combined
        return res
    before, _, payload = combined.partition(SENTINEL + "\n")
    try:
        data = json.loads(payload.strip().splitlines()[0])
    except (json.JSONDecodeError, IndexError):
        res.crashed = "could not parse harness output:\n" + payload
        return res
    res.import_error = data.get("import_error")
    res.stdout = data.get("stdout", "") + before
    for t in data.get("tests", []):
        res.tests.append(
            TestCase(
                name=t.get("name", "?"),
                doc=t.get("doc", ""),
                status=t.get("status", "error"),
                message=t.get("message", ""),
                traceback=t.get("traceback", ""),
            )
        )
    return res


def run_solution(ex: Exercise, python: str = sys.executable) -> RunResult:
    """Run the tests against solution.py instead of exercise.py (used by tools/verify.py)."""
    import shutil
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp) / ex.dir.name
        shutil.copytree(ex.dir, tmpdir)
        (tmpdir / "exercise.py").write_text(ex.solution_file.read_text(encoding="utf-8"), encoding="utf-8")
        alt = Exercise(ex.part_num, ex.num, ex.slug, tmpdir, ex.meta)
        return run_tests(alt, python=python)
