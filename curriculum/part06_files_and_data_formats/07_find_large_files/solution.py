"""Reference solutions for find_large_files."""
from pathlib import Path
from typing import List, Optional, Sequence, Set, Tuple, Union


# Best practice: normalise the suffix list once into a set, walk with rglob("*") and
# filter with is_file(), then sort with a key of (-size, path) to get both orders at once.
def _normalise(suffixes: Optional[Sequence[str]]) -> Optional[Set[str]]:
    if not suffixes:
        return None
    wanted = set()
    for s in suffixes:
        s = s.lower()
        wanted.add(s if s.startswith(".") or s == "" else "." + s)
    return wanted


def find_large_files(
    root: Union[str, Path], min_bytes: int, suffixes: Optional[Sequence[str]] = None
) -> List[Tuple[str, int]]:
    base = Path(root)
    if not base.is_dir():
        raise NotADirectoryError(str(base))
    wanted = _normalise(suffixes)
    found: List[Tuple[str, int]] = []
    for path in base.rglob("*"):
        if not path.is_file():
            continue
        if wanted is not None and path.suffix.lower() not in wanted:
            continue
        size = path.stat().st_size
        if size >= min_bytes:
            found.append((path.relative_to(base).as_posix(), size))
    found.sort(key=lambda item: (-item[1], item[0]))
    return found


# Clever: a generator expression per filter step reads like a pipeline; sorted() with
# the same key does the ordering.
def find_large_files_pipeline(
    root: Union[str, Path], min_bytes: int, suffixes: Optional[Sequence[str]] = None
) -> List[Tuple[str, int]]:
    base = Path(root)
    if not base.is_dir():
        raise NotADirectoryError(str(base))
    wanted = _normalise(suffixes)
    files = (p for p in base.rglob("*") if p.is_file())
    if wanted is not None:
        files = (p for p in files if p.suffix.lower() in wanted)
    sized = ((p.relative_to(base).as_posix(), p.stat().st_size) for p in files)
    return sorted((item for item in sized if item[1] >= min_bytes), key=lambda item: (-item[1], item[0]))
