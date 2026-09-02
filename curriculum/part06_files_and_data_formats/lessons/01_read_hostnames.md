# Reading a text file

--- teach
### `with open(...)` opens a file and closes it for you
`open(path)` gives you a file object. Put it in a `with` block and Python closes the file when the block ends, even if something goes wrong inside. Always pass `encoding="utf-8"` so the file reads the same on macOS, Linux and Windows.
```python
with open("hosts.txt", encoding="utf-8") as f:
    text = f.read()
```
`"r"` (read) is the default mode, so you can leave it out. Writing `f = open(...)` on its own line, with no `with`, is the thing interviewers notice first.

--- fill
Complete the line so the file is read as UTF-8 text.
```python
with open(path, encoding=___) as f:
```
answer: "utf-8" | 'utf-8' | utf-8
> `encoding="utf-8"` every time. Without it Python uses the platform default, which was cp1252 on Windows for years.

--- teach
### Looping over a file gives one line at a time
`for line in f:` hands you each line in turn, and each line still ends with its newline character (`"\n"`, or `"\r\n"` from Windows). Strip it before you use the text.
```python
with open("hosts.txt", encoding="utf-8") as f:
    for raw in f:
        line = raw.strip()
```
`strip()` removes spaces, tabs and both kinds of line ending in one go. Looping like this also keeps memory flat: only one line is in memory at a time.

--- code
`io.StringIO` wraps a string in a file object, so you can practise without a real file. Loop over `f` and print each line stripped.
```python
import io
f = io.StringIO("  mbp-j-doe \n\twin-lab-01\t\n")
```
expect: mbp-j-doe\nwin-lab-01
solution: for raw in f:
solution:     print(raw.strip())
> A file object is an iterable of lines. Each `raw` still ends in `\n`, and `strip()` removes it together with the spaces and tabs.

--- predict
What does this print?
```python
raw = "  win-lab-01\t\r\n"
print(repr(raw.strip()))
```
answer: 'win-lab-01'
> `strip()` removes spaces, tabs, `\r` and `\n` from both ends. `repr` shows the quotes so you can see there is nothing left around the text.

--- teach
### Skip what you do not want with `continue`
Config-style files have blank lines and comments. After stripping, a blank line is `""`, which is false, and a comment starts with `#`. `continue` jumps to the next line, so the code below it only sees real data.
```python
hosts = []
for raw in f:
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    hosts.append(line)
```
Because you stripped first, an indented comment like `   # note` is caught too.

--- code
Fill `hosts` with the real hostnames from `f`: stripped, skipping blank lines and comments.
```python
import io
f = io.StringIO("# lab\nmbp-j-doe\n\n   # old\nwin-lab-01\n")
hosts = []
```
check: hosts == ["mbp-j-doe", "win-lab-01"]
solution: for raw in f:
solution:     line = raw.strip()
solution:     if not line or line.startswith("#"):
solution:         continue
solution:     hosts.append(line)
> Strip first, then test. `not line` catches the blank line and `startswith("#")` catches both comments, including the indented one.

--- predict
What does this print?
```python
lines = ["# lab\n", "mbp-j-doe\n", "   \n", "  #old\n", "win-lab-01\n"]
kept = []
for raw in lines:
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    kept.append(line)
print(kept)
```
answer: ['mbp-j-doe', 'win-lab-01']
> The comment, the whitespace-only line and the indented comment are all skipped. Stripping happens before the tests, so indentation does not matter.

--- teach
### Accept a `str` or a `Path`; let a missing file raise
Callers pass paths as plain strings or as `pathlib.Path` objects. `open()` accepts both, so you need no conversion. If the file does not exist, `open` raises `FileNotFoundError`. When the task says "let it raise", do nothing: the caller wants to see that error.
```python
from pathlib import Path

read_hostnames("hosts.txt")          # str works
read_hostnames(Path("hosts.txt"))    # Path works too
```

--- quiz
Why is `with open(...) as f:` preferred over `f = open(...)`?
- [ ] It reads the file faster
- [x] It closes the file when the block ends, even if an error is raised
- [ ] It converts the file to UTF-8 automatically
> `with` guarantees the close. Encoding is set by the `encoding=` argument, not by `with`, and there is no speed difference.

--- exercise 6.1

--- recap
- `with open(path, encoding="utf-8") as f:` opens and closes the file safely.
- `for line in f:` yields one line at a time, newline included; `strip()` it.
- `if not line or line.startswith("#"): continue` skips blanks and comments.
- `open` takes a `str` or a `Path`; a missing file raises `FileNotFoundError`.
