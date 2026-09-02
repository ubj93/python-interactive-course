"""Find large files under a directory.

Disk-full tickets usually end with "what is eating the space?". Write
`find_large_files(root, min_bytes, suffixes=None)` that walks `root`
recursively with pathlib and returns a list of (relative_path, size_bytes)
tuples for every regular file whose size is at least `min_bytes`.

Rules:
- `root` may be a str or a pathlib.Path; if it does not exist or is not a
  directory raise NotADirectoryError
- walk every level below root (Path.rglob), but only report files; skip
  directories (a directory's size is meaningless here)
- a file whose size is exactly min_bytes is included
- `suffixes`, when given, is a list of extensions to keep. Matching is
  case-insensitive and tolerant of a leading dot: "log", ".log" and ".LOG" all
  mean the same thing. A file's extension is Path.suffix (so "app.tar.gz" has
  suffix ".gz"). Files with no extension only match if "" is in `suffixes`.
  suffixes=None (the default) or [] means keep every file
- relative_path is the path below root as a string with forward slashes on
  every platform (Path.relative_to(root).as_posix())
- sort by size descending; files of equal size sort by relative_path ascending
- an empty directory (or nothing over the threshold) returns []

Examples:
    given root/ containing:
        install.log      (300 bytes)
        cache/blob.bin   (5000 bytes)
        cache/tiny.log   (10 bytes)
        logs/old.LOG     (300 bytes)

    >>> find_large_files("root", 300)
    [('cache/blob.bin', 5000), ('install.log', 300), ('logs/old.LOG', 300)]
    >>> find_large_files("root", 1, suffixes=["log"])
    [('install.log', 300), ('logs/old.LOG', 300), ('cache/tiny.log', 10)]
"""
from pathlib import Path
from typing import List, Optional, Sequence, Tuple, Union


def find_large_files(
    root: Union[str, Path], min_bytes: int, suffixes: Optional[Sequence[str]] = None
) -> List[Tuple[str, int]]:
    raise NotImplementedError("write find_large_files")
