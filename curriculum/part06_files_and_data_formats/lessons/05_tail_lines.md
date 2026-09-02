# The last n lines

--- teach
### `deque(maxlen=n)` keeps only the newest items
A `deque` (say "deck") is a list-like container from `collections`. Give it `maxlen=n` and it forgets the oldest item whenever a new one pushes it past `n`. Push every line through it and what is left is the tail of the file, oldest first.
```python
>>> from collections import deque
>>> d = deque(maxlen=2)
>>> for x in [1, 2, 3, 4]:
...     d.append(x)
>>> list(d)
[3, 4]
```

--- code
Push every item of `events` through a deque that holds at most 3, then set `last` to a list of what remains.
```python
from collections import deque
events = ["boot", "login", "sync", "sleep", "wake"]
```
check: last == ["sync", "sleep", "wake"]
solution: d = deque(maxlen=3)
solution: for event in events:
solution:     d.append(event)
solution: last = list(d)
> Each `append` past the third item evicts the oldest one. `list(d)` turns the deque back into a plain list, oldest first.

--- predict
What does this print?
```python
from collections import deque
print(list(deque(["l1", "l2", "l3", "l4", "l5"], maxlen=2)))
```
answer: ['l4', 'l5']
> `deque` accepts any iterable directly. With `maxlen=2` only the last two survive, in their original order.

--- teach
### Feed the file straight into the deque
A file object is an iterable of lines, so `deque(f, maxlen=n)` reads the whole file one line at a time and keeps `n` of them. Memory is `n` lines, not the whole file. Calling `f.read()` or `f.readlines()` would defeat the point, and the last test forbids it.
```python
with open(path, encoding="utf-8") as f:
    last = deque(f, maxlen=n)
```

--- fill
Complete the line so only the newest `n` lines are kept.
```python
with open(path, encoding="utf-8") as f:
    last = deque(f, maxlen=___)
```
answer: n
> `maxlen=n` is the whole trick: the deque drops old lines as new ones arrive, so the file is never held in memory.

--- teach
### Remove the line ending, and nothing else
The lines still carry `"\n"`, or `"\r\n"` from a Windows file. `strip()` would also delete the spaces inside a line that the spec says to keep. `rstrip("\r\n")` removes only those two characters from the right end.
```python
>>> "  indented  \r\n".rstrip("\r\n")
'  indented  '
>>> "last".rstrip("\r\n")          # a final line with no newline
'last'
```

--- code
Set `lines` to the items of `raw` with their line endings removed, keeping the spaces inside.
```python
raw = ["  a  \r\n", "b\n", "c"]
```
check: lines == ["  a  ", "b", "c"]
solution: lines = [line.rstrip("\r\n") for line in raw]
> `rstrip("\r\n")` strips only carriage returns and newlines from the right. The final `"c"` has no ending and is returned as it is.

--- predict
What does this print?
```python
print(repr("  x  \n".rstrip("\r\n")))
```
answer: '  x  '
> `rstrip("\r\n")` takes the argument as a set of characters to remove from the right. Spaces are not in it, so they stay.

--- teach
### Check `n` before opening the file
A negative `n` makes no sense: raise `ValueError`. `n == 0` should give `[]`, and `deque(maxlen=0)` handles that on its own. Do the check first, before any file work, so a bad argument never opens a file.
```python
if n < 0:
    raise ValueError("n must be >= 0")
```

--- quiz
`tail_lines(path, 0)` is called on a five-line file. What should happen?
- [ ] It raises `ValueError`
- [x] It returns `[]`
- [ ] It returns all five lines
> Zero lines is a valid request; only a negative `n` is an error. A `deque(maxlen=0)` keeps nothing, so the result is empty.

--- exercise 6.5

--- recap
- `deque(maxlen=n)` keeps the newest `n` items and drops the rest.
- `deque(f, maxlen=n)` streams the file with `n` lines of memory.
- `rstrip("\r\n")` removes the line ending only; `strip()` would eat inner spaces.
- Validate `n` first: negative raises `ValueError`, zero returns `[]`.
