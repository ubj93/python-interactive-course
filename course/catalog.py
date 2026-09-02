"""Discover parts and exercises on disk.

Layout::

    curriculum/
      part01_foundations/
        LESSON.md
        01_greet_device/
          exercise.py        # stub the learner edits (module docstring = problem statement)
          test_exercise.py   # unittest cases, import from ``exercise``
          solution.py        # reference solution(s), shown after a pass
          meta.json          # title, kyu, tags, hints, time_limit_min
          fixtures/          # optional data files used by tests
"""
from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parent.parent
CURRICULUM = ROOT / "curriculum"

# XP per kyu, roughly Codewars' honor curve. 8 kyu is the easiest.
KYU_XP = {8: 2, 7: 3, 6: 8, 5: 21, 4: 55, 3: 149, 2: 404, 1: 1097}

_PART_RE = re.compile(r"^part(\d{2})_([a-z0-9_]+)$")
_EX_RE = re.compile(r"^(\d{2})_([a-z0-9_]+)$")


@dataclass
class Exercise:
    part_num: int
    num: int
    slug: str
    dir: Path
    meta: dict = field(default_factory=dict)

    @property
    def id(self) -> str:
        return f"{self.part_num}.{self.num}"

    @property
    def title(self) -> str:
        return self.meta.get("title", self.slug.replace("_", " ").title())

    @property
    def kyu(self) -> int:
        return int(self.meta.get("kyu", 7))

    @property
    def xp(self) -> int:
        return KYU_XP[self.kyu]

    @property
    def tags(self) -> List[str]:
        return list(self.meta.get("tags", []))

    @property
    def hints(self) -> List[str]:
        return list(self.meta.get("hints", []))

    @property
    def time_limit_min(self) -> Optional[int]:
        v = self.meta.get("time_limit_min")
        return int(v) if v else None

    @property
    def timeout_s(self) -> int:
        return int(self.meta.get("timeout_s", 10))

    @property
    def exercise_file(self) -> Path:
        return self.dir / "exercise.py"

    @property
    def test_file(self) -> Path:
        return self.dir / "test_exercise.py"

    @property
    def solution_file(self) -> Path:
        return self.dir / "solution.py"

    def description(self) -> str:
        """Problem statement = module docstring of exercise.py."""
        src = self.exercise_file.read_text(encoding="utf-8")
        try:
            doc = ast.get_docstring(ast.parse(src))
        except SyntaxError:
            doc = None
        return (doc or "").strip()

    def stub_source(self) -> str:
        """The pristine stub, reconstructed from git-tracked file if available."""
        return self.exercise_file.read_text(encoding="utf-8")


@dataclass
class Part:
    num: int
    slug: str
    dir: Path
    exercises: List[Exercise] = field(default_factory=list)

    @property
    def id(self) -> str:
        return str(self.num)

    @property
    def lesson_file(self) -> Path:
        return self.dir / "LESSON.md"

    @property
    def title(self) -> str:
        try:
            for line in self.lesson_file.read_text(encoding="utf-8").splitlines():
                if line.startswith("# "):
                    title = line[2:].strip()
                    # "Part 3 · Functions" -> "Functions"
                    return re.sub(r"^part\s*\d+\s*[·:.\-–—]\s*", "", title, flags=re.I)
        except OSError:
            pass
        return self.slug.replace("_", " ").title()

    @property
    def total_xp(self) -> int:
        return sum(e.xp for e in self.exercises)


def load_catalog(curriculum: Path = CURRICULUM) -> List[Part]:
    parts: List[Part] = []
    if not curriculum.exists():
        return parts
    for pdir in sorted(curriculum.iterdir()):
        m = _PART_RE.match(pdir.name)
        if not m or not pdir.is_dir():
            continue
        part = Part(num=int(m.group(1)), slug=m.group(2), dir=pdir)
        for edir in sorted(pdir.iterdir()):
            em = _EX_RE.match(edir.name)
            if not em or not edir.is_dir() or not (edir / "exercise.py").exists():
                continue
            meta_path = edir / "meta.json"
            meta = {}
            if meta_path.exists():
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            part.exercises.append(
                Exercise(part_num=part.num, num=int(em.group(1)), slug=em.group(2), dir=edir, meta=meta)
            )
        parts.append(part)
    return parts


def all_exercises(catalog: List[Part]) -> List[Exercise]:
    return [e for p in catalog for e in p.exercises]


def total_xp(catalog: List[Part]) -> int:
    return sum(e.xp for e in all_exercises(catalog))


def find_part(catalog: List[Part], ref: str) -> Optional[Part]:
    ref = str(ref).strip().lower()
    for p in catalog:
        if ref in (str(p.num), f"{p.num:02d}", p.slug, f"part{p.num:02d}_{p.slug}", f"part{p.num}"):
            return p
    return None


def find_exercise(catalog: List[Part], ref: str) -> Optional[Exercise]:
    """Resolve ``3.2``, ``03.02``, ``3-2``, a slug, or ``part/slug`` to an exercise."""
    ref = str(ref).strip().lower().replace("-", ".").replace("/", ".")
    m = re.match(r"^(\d+)\.(\d+)$", ref)
    if m:
        p, n = int(m.group(1)), int(m.group(2))
        for e in all_exercises(catalog):
            if e.part_num == p and e.num == n:
                return e
        return None
    for e in all_exercises(catalog):
        if ref in (e.slug, e.dir.name, f"{e.part_num}.{e.dir.name}", e.title.lower()):
            return e
    return None
