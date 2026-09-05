# Walking a directory tree

--- teach #card-1424d703e0dc509e
### `Path` is a path you can ask questions
`pathlib.Path` wraps a path in an object. `Path(x)` accepts a `str` or a `Path`, so start every path function with it. Then ask: `p.is_dir()`, `p.is_file()`, `p.exists()`. A root that is not a directory should raise `NotADirectoryError`.
```python
from pathlib import Path

base = Path(root)
if not base.is_dir():
    raise NotADirectoryError(str(base))
```
`is_dir()` is `False` for a missing path too, so one check covers "missing" and "it is a file".

--- teach #card-1bffbccbf6245cb3
### `rglob("*")` walks every level; `is_file()` keeps the files
`p.glob("*")` lists one directory. `p.rglob("*")` recurses into every subdirectory. Both yield directories as well as files, so filter with `is_file()`. `p.stat().st_size` is the size in bytes.
```python
for path in base.rglob("*"):
    if not path.is_file():
        continue
    size = path.stat().st_size
```

--- fill #card-1229d94eaf3c5644
Complete the loop so it visits every file at every depth below `base`.
```python
for path in base.___("*"):
    if path.is_file():
        ...
```
answer: rglob
> `rglob` is recursive glob. Plain `glob("*")` would only see the top level.

--- teach #card-14603b94e6855da4
### Suffixes, normalised once
`Path("logs/old.LOG").suffix` is `".LOG"`, and `"app.tar.gz"` has suffix `".gz"`: only the last dot counts. Users write `"log"`, `".log"` or `".LOG"` for the same thing, so turn their list into a set of lowercase, dot-prefixed values once, then compare `path.suffix.lower()` against it. Keep `""` as is: it means "no extension".
```python
wanted = set()
for s in suffixes:
    s = s.lower()
    wanted.add(s if s.startswith(".") or s == "" else "." + s)
```

--- code #card-d3f6ccb49d40535d
Set `wanted` to the normalised form of `suffixes`: lowercase, with a leading dot, and `""` kept as it is.
```python
suffixes = ["log", ".GZ", ""]
```
check: wanted == {".log", ".gz", ""}
solution: wanted = set()
solution: for s in suffixes:
solution:     s = s.lower()
solution:     wanted.add(s if s.startswith(".") or s == "" else "." + s)
> `"log"` gains a dot, `".GZ"` is lowercased, and the empty string stays empty so files without an extension can still be selected.

--- predict #card-6bfcb4db1a525120
What does this print?
```python
from pathlib import Path
print(Path("logs/archive/app.tar.gz").suffix, Path("README").suffix == "")
```
answer: .gz True
> `suffix` is everything from the last dot: `.gz`, not `.tar.gz`. A name with no dot has an empty suffix.

--- teach #card-917b0c2b50a153ec
### Paths relative to the root, with forward slashes
The result wants the path below `root`, as text, with `/` on every platform. `path.relative_to(base)` removes the root part; `.as_posix()` renders it with forward slashes even on Windows.
```python
>>> Path("/srv/cache/blob.bin").relative_to("/srv").as_posix()
'cache/blob.bin'
```

--- predict #card-81b9670d503c507d
What does this print?
```python
from pathlib import Path
print(Path("/srv/logs/old.LOG").relative_to("/srv").as_posix())
```
answer: logs/old.LOG
> `relative_to` strips the `/srv/` prefix; `as_posix` gives the remainder as forward-slash text. Case is untouched.

--- teach #card-7bb0a10a2da75aba
### Sort by size down, then by path up
`sorted` takes a `key` function. Return a tuple: first the negated size (so bigger comes first), then the path (so ties sort alphabetically). One sort, both orders.
```python
found.sort(key=lambda item: (-item[1], item[0]))
```

--- predict #card-7cc132d948c75dbf
What does this print?
```python
found = [("install.log", 300), ("cache/blob.bin", 5000), ("README", 300)]
print(sorted(found, key=lambda item: (-item[1], item[0])))
```
answer: [('cache/blob.bin', 5000), ('README', 300), ('install.log', 300)]
> `-5000` is the smallest key, so the big file comes first. The two 300-byte files tie and fall back to the path; uppercase `R` sorts before lowercase `i`.

--- exercise 6.7 #card-29eda39f101e5255

--- recap #card-c852ca0660cf5ac8
- `Path(root)` accepts str or Path; `is_dir()` guards the root.
- `rglob("*")` recurses; filter with `is_file()`; `stat().st_size` is bytes.
- Normalise suffixes to lowercase with a leading dot; `suffix` is the last dot only.
- `relative_to(base).as_posix()` gives portable relative text.
- `key=lambda item: (-size, path)` sorts big first, ties alphabetically.
