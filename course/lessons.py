"""Guided lessons: bite-sized cards that teach one idea, check it, and end in an exercise.

Each part has a ``lessons/`` folder with one Markdown file per lesson::

    curriculum/part01_foundations/lessons/01_values_and_names.md

A lesson file is a title line followed by cards separated by ``--- <type>`` lines:

    # Values and names

    --- teach
    ### A name is a label on a value
    Two or three sentences. Then a snippet.
    ```python
    ram_gb = 16
    ```

    --- quiz
    What does `type(16)` return?
    - [ ] `<class 'str'>`
    - [x] `<class 'int'>`
    - [ ] `16`
    > `16` is a whole number, so Python calls it an int.

    --- predict
    What does this print?
    ```python
    print(7 // 2)
    ```
    answer: 3
    > `//` is floor division: it throws away the remainder.

    --- fill
    Complete the line so `name` has no surrounding spaces.
    ```python
    name = raw.___()
    ```
    answer: strip
    > strip() removes whitespace from both ends.

    --- exercise 1.1

    --- recap
    - bullets that summarise the lesson

    --- code
    Print the hostname in lowercase.
    ```python
    hostname = "MBP-J-DOE"
    ```
    expect: mbp-j-doe
    solution: print(hostname.lower())
    > lower() returns a lowercase copy; print shows it.

Card types: ``teach`` (no check), ``quiz`` (exactly one ``[x]`` option), ``predict`` and
``fill`` (an ``answer:`` line; several accepted answers separated by ``|``), ``code``
(the learner writes real Python under the starter snippet and it is run: ``expect:`` is
the exact stdout, ``check:`` lines are expressions that must be true afterwards, and
``solution:`` is the model answer shown after two failed runs), ``exercise`` (the id of
an exercise in the same part), ``recap`` (no check). A ``>`` line after the answer is
the explanation shown once the learner has answered.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .catalog import Part

_LESSON_FILE_RE = re.compile(r"^(\d{2})_([a-z0-9_]+)\.md$")
_CARD_RE = re.compile(r"^---\s+(teach|quiz|predict|fill|code|exercise|recap)(?:\s+(\S+))?\s*$")
_OPTION_RE = re.compile(r"^- \[([ xX])\]\s+(.*)$")
_ANSWER_RE = re.compile(r"^answer:\s*(.+?)\s*$")
_EXPECT_RE = re.compile(r"^expect:\s*(.*?)\s*$")
_CHECK_RE = re.compile(r"^check:\s*(.+?)\s*$")
_SOLUTION_RE = re.compile(r"^solution:(?: ?(.*?))?\s*$")  # keeps indentation after the first space

CARD_XP = 1  # xp for a correct first answer on a checkable card


def normalize_answer(s: str) -> str:
    """Compare answers loosely: trim, collapse inner whitespace, drop surrounding quotes."""
    s = " ".join(str(s).strip().split())
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"":
        s = s[1:-1]
    return s


@dataclass
class Card:
    kind: str                     # teach | quiz | predict | fill | exercise | recap
    body: str = ""                # markdown (question or teaching text, may include a code fence)
    options: List[str] = field(default_factory=list)   # quiz
    correct: Optional[int] = None                       # quiz: index into options
    answers: List[str] = field(default_factory=list)   # predict/fill accepted answers
    explanation: str = ""
    exercise_id: Optional[str] = None                   # exercise
    expect: Optional[str] = None                        # code: exact stdout (stripped)
    checks: List[str] = field(default_factory=list)    # code: expressions that must be true
    solution: str = ""                                  # code: model answer

    @property
    def checkable(self) -> bool:
        return self.kind in ("quiz", "predict", "fill", "code")

    @property
    def starter(self) -> str:
        """For code cards: the code inside the fence, which the learner extends."""
        m = re.search(r"```(?:python)?\n(.*?)```", self.body, re.S)
        return m.group(1).rstrip("\n") + "\n" if m else ""

    @property
    def prompt(self) -> str:
        """For code cards: the body without the fence."""
        return re.sub(r"```(?:python)?\n.*?```", "", self.body, flags=re.S).strip()

    def test_source(self) -> str:
        """Generated unittest module that grades a code card (runs in the harness or Pyodide)."""
        lines = [
            "import contextlib, io, runpy, unittest",
            "",
            "",
            "def _run():",
            "    buf = io.StringIO()",
            "    with contextlib.redirect_stdout(buf):",
            "        ns = runpy.run_path('exercise.py')",
            "    return buf.getvalue(), ns",
            "",
            "",
            "class TestCard(unittest.TestCase):",
        ]
        if self.expect is not None:
            exp = self.expect.replace("\\n", "\n")
            lines += [
                "    def test_output(self):",
                f"        {repr('Prints: ' + exp.replace(chr(10), ' / '))}",
                "        out, _ = _run()",
                f"        self.assertEqual(out.strip(), {repr(exp)})",
                "",
            ]
        for i, expr in enumerate(self.checks, 1):
            lines += [
                f"    def test_check_{i}(self):",
                f"        {repr('Afterwards: ' + expr)}",
                "        _, ns = _run()",
                f"        self.assertTrue(eval({repr(expr)}, dict(ns)), {repr(expr + ' is not true')})",
                "",
            ]
        return "\n".join(lines) + "\n"

    def check(self, given: str) -> bool:
        if self.kind == "quiz":
            g = given.strip().lower()
            if g.isdigit():
                return int(g) - 1 == self.correct
            if len(g) == 1 and g.isalpha():
                return ord(g) - ord("a") == self.correct
            return normalize_answer(given) == normalize_answer(self.options[self.correct]) if self.correct is not None else False
        if self.kind in ("predict", "fill"):
            g = normalize_answer(given)
            return any(g == normalize_answer(a) for a in self.answers)
        return True


@dataclass
class Lesson:
    part_num: int
    num: int
    slug: str
    title: str
    path: Path
    cards: List[Card] = field(default_factory=list)

    @property
    def id(self) -> str:
        return f"{self.part_num}.{self.num}"

    @property
    def exercise_ids(self) -> List[str]:
        return [c.exercise_id for c in self.cards if c.kind == "exercise" and c.exercise_id]

    @property
    def checkable_count(self) -> int:
        return sum(1 for c in self.cards if c.checkable)

    @property
    def xp(self) -> int:
        return self.checkable_count * CARD_XP


def parse_lesson(path: Path, part_num: int, num: int, slug: str) -> Lesson:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    title = slug.replace("_", " ").capitalize()
    i = 0
    # Title: first "# " line before the first card.
    while i < len(lines) and not _CARD_RE.match(lines[i]):
        if lines[i].startswith("# "):
            title = lines[i][2:].strip()
        i += 1
    lesson = Lesson(part_num=part_num, num=num, slug=slug, title=title, path=path)
    current: Optional[Card] = None
    body: List[str] = []

    def finish() -> None:
        if current is None:
            return
        _fill_card(current, body)
        lesson.cards.append(current)

    for line in lines[i:]:
        m = _CARD_RE.match(line)
        if m:
            finish()
            current = Card(kind=m.group(1))
            if current.kind == "exercise":
                current.exercise_id = m.group(2)
            body = []
        elif current is not None:
            body.append(line)
    finish()
    return lesson


def _fill_card(card: Card, body: List[str]) -> None:
    text_lines: List[str] = []
    expl: List[str] = []
    in_fence = False
    for line in body:
        if line.startswith("```"):
            in_fence = not in_fence
            text_lines.append(line)
            continue
        if in_fence:
            text_lines.append(line)
            continue
        om = _OPTION_RE.match(line)
        if om and card.kind == "quiz":
            if om.group(1).lower() == "x":
                card.correct = len(card.options)
            card.options.append(om.group(2).strip())
            continue
        am = _ANSWER_RE.match(line)
        if am and card.kind in ("predict", "fill"):
            card.answers = [a.strip() for a in am.group(1).split("|") if a.strip()]
            continue
        if card.kind == "code":
            em = _EXPECT_RE.match(line)
            if em:
                card.expect = em.group(1)
                continue
            cm = _CHECK_RE.match(line)
            if cm:
                card.checks.append(cm.group(1))
                continue
            sm = _SOLUTION_RE.match(line)
            if sm:
                piece = sm.group(1) or ""
                card.solution = (card.solution + "\n" + piece) if card.solution else piece
                continue
        if line.startswith(">"):
            expl.append(line[1:].strip())
            continue
        text_lines.append(line)
    card.body = "\n".join(text_lines).strip()
    card.explanation = " ".join(expl).strip()


def load_lessons(part: Part) -> List[Lesson]:
    ldir = part.dir / "lessons"
    lessons: List[Lesson] = []
    if not ldir.is_dir():
        return lessons
    for f in sorted(ldir.iterdir()):
        m = _LESSON_FILE_RE.match(f.name)
        if not m:
            continue
        lessons.append(parse_lesson(f, part.num, int(m.group(1)), m.group(2)))
    return lessons


def load_all_lessons(catalog: List[Part]) -> Dict[int, List[Lesson]]:
    return {p.num: load_lessons(p) for p in catalog}


def find_lesson(lessons_by_part: Dict[int, List[Lesson]], ref: str) -> Optional[Lesson]:
    ref = str(ref).strip().lower().replace("-", ".")
    m = re.match(r"^l?(\d+)\.(\d+)$", ref)
    if m:
        p, n = int(m.group(1)), int(m.group(2))
        for l in lessons_by_part.get(p, []):
            if l.num == n:
                return l
        return None
    for ls in lessons_by_part.values():
        for l in ls:
            if ref in (l.slug, l.title.lower()):
                return l
    return None


def validate_lesson(lesson: Lesson, part: Part) -> List[str]:
    """Structural problems with one lesson (used by tools/verify.py)."""
    problems: List[str] = []
    tag = f"[lesson {lesson.id} {lesson.path.name}]"
    if not lesson.cards:
        problems.append(f"{tag} has no cards")
        return problems
    if not (4 <= len(lesson.cards) <= 16):
        problems.append(f"{tag} has {len(lesson.cards)} cards; aim for 5 to 12")
    if lesson.cards[0].kind != "teach":
        problems.append(f"{tag} should start with a teach card")
    if lesson.checkable_count < 2:
        problems.append(f"{tag} needs at least two checks (quiz/predict/fill)")
    if not lesson.exercise_ids:
        problems.append(f"{tag} must end in an exercise card")
    ex_ids = {e.id for e in part.exercises}
    for idx, c in enumerate(lesson.cards, 1):
        ctag = f"{tag} card {idx} ({c.kind})"
        if c.kind in ("teach", "quiz", "predict", "fill", "code") and not c.body:
            problems.append(f"{ctag} is empty")
        if c.kind == "teach" and len(c.body.split()) > 170:
            problems.append(f"{ctag} is too long ({len(c.body.split())} words; keep under 170)")
        if c.kind == "quiz":
            if len(c.options) < 2:
                problems.append(f"{ctag} needs at least two options")
            if c.correct is None:
                problems.append(f"{ctag} has no [x] option")
        if c.kind in ("predict", "fill") and not c.answers:
            problems.append(f"{ctag} has no 'answer:' line")
        if c.kind == "fill" and "___" not in c.body:
            problems.append(f"{ctag} needs a ___ blank in its code")
        if c.kind == "code":
            if "```" not in c.body:
                problems.append(f"{ctag} needs a starter code fence (it may be a single comment line)")
            if c.expect is None and not c.checks:
                problems.append(f"{ctag} needs an 'expect:' or at least one 'check:' line")
            if not c.solution:
                problems.append(f"{ctag} needs a 'solution:' line")
        if c.checkable and not c.explanation:
            problems.append(f"{ctag} needs a '>' explanation line")
        if c.kind == "exercise":
            if c.exercise_id not in ex_ids:
                problems.append(f"{ctag} references unknown exercise '{c.exercise_id}'")
            if idx != len(lesson.cards) and lesson.cards[idx].kind != "recap":
                problems.append(f"{ctag} should be the last card (a recap may follow)")
    return problems
