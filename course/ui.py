"""Tiny ANSI UI helpers. Honors NO_COLOR and non-TTY output."""
from __future__ import annotations

import os
import shutil
import sys
import textwrap

_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR") and os.environ.get("TERM") != "dumb"


def enable_color(flag: bool) -> None:
    global _COLOR
    _COLOR = flag


def _c(code: str, s: str) -> str:
    return f"\033[{code}m{s}\033[0m" if _COLOR else s


def bold(s: str) -> str: return _c("1", s)
def dim(s: str) -> str: return _c("2", s)
def red(s: str) -> str: return _c("31", s)
def green(s: str) -> str: return _c("32", s)
def yellow(s: str) -> str: return _c("33", s)
def blue(s: str) -> str: return _c("34", s)
def magenta(s: str) -> str: return _c("35", s)
def cyan(s: str) -> str: return _c("36", s)


def width() -> int:
    return min(shutil.get_terminal_size((100, 24)).columns, 100)


def bar(frac: float, size: int = 24, fill: str = "█", empty: str = "░") -> str:
    frac = max(0.0, min(1.0, frac))
    n = int(round(frac * size))
    return green(fill * n) + dim(empty * (size - n))


def hr(char: str = "─") -> str:
    return dim(char * width())


def heading(s: str) -> str:
    return "\n" + bold(cyan(s)) + "\n" + hr()


def kyu_color(kyu: int, s: str) -> str:
    if kyu >= 7:
        return _c("37", s)
    if kyu >= 5:
        return yellow(s)
    if kyu >= 3:
        return blue(s)
    return magenta(s)


def wrap(text: str, indent: str = "  ") -> str:
    out = []
    for para in text.split("\n"):
        if not para.strip():
            out.append("")
        elif para.startswith("    ") or para.startswith("\t") or para.lstrip().startswith((">>>", "$ ", "- ", "* ", "|")):
            out.append(indent + para)
        else:
            out.extend(textwrap.wrap(para, width() - len(indent), initial_indent=indent, subsequent_indent=indent))
    return "\n".join(out)


def status_icon(status: str) -> str:
    return {
        "pass": green("✔"),
        "fail": red("✘"),
        "error": red("💥"),
        "skip": yellow("–"),
    }.get(status, "?")


def page(text: str) -> None:
    """Print through $PAGER when interactive, else plain print."""
    if sys.stdout.isatty() and len(text.splitlines()) > shutil.get_terminal_size((100, 24)).lines - 2:
        import subprocess

        pager = os.environ.get("PAGER", "less -R")
        try:
            subprocess.run(pager, input=text, text=True, shell=True, check=False)
            return
        except OSError:
            pass
    print(text)
