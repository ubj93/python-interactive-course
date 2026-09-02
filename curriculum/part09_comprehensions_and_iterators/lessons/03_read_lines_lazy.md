# Streaming lines

--- teach
### A file is an iterable of lines
`for line in fh` gives one line at a time, newline included, without loading the whole file. A list of strings or a generator behaves the same way in that loop. The exercise accepts any of them, so iterate, and never call `read()`, `readlines()` or `list()` on the input.
```python
with open("hosts.txt", encoding="utf-8") as fh:
    for line in fh:
        ...                     # one line, e.g. "mbp-j-doe   # jane\n"
```

--- teach
### Cleaning one line
`#` starts a comment. `line.split("#", 1)[0]` is the text before the first `#` (or the whole line if there is none). Then `strip()` removes spaces and the trailing newline. If nothing is left, the line was blank or all comment.
```python
line = line.split("#", 1)[0].strip()
if line:
    ...                         # something real
```

--- predict
What does this print?
```python
print("win-lab-01#lab\n".split("#", 1)[0].strip())
```
answer: win-lab-01
> `split("#", 1)` cuts at the first `#` and `[0]` keeps the left part. `strip()` then removes the newline, leaving the clean hostname.

--- fill
Complete the clean-up so the newline and surrounding spaces are removed.
```python
text = line.split("#", 1)[0].___()
```
answer: strip
> `strip()` removes whitespace from both ends, including `\n`. `rstrip()` would also drop the newline but would leave leading spaces.

--- teach
### The loop version, then the generator
A loop that collects clean lines into a list reads the whole input before returning anything. Replace `append` with `yield` and the function becomes a generator: it hands out each line as soon as it is clean and reads no further until asked.
```python
def read_lines_lazy(lines):
    for line in lines:
        line = line.split("#", 1)[0].strip()
        if line:
            yield line
```
No `result` list, no `return`. `list(read_lines_lazy(fh))` gives the list when you want one.

--- predict
What does this print?
```python
gen = read_lines_lazy(["# header", "  mbp-j-doe  ", "", "win-lab-01 # lab"])
print(next(gen), next(gen))
```
answer: mbp-j-doe win-lab-01
> The first pull skips the comment line and yields the stripped second line. The second pull skips the blank line and yields the fourth, with its inline comment removed.

--- quiz
The tests feed an infinite generator and call `next()` twice. Which version passes?
- [ ] `return [clean(l) for l in lines if clean(l)]`
- [x] `for line in lines: ... yield line`
- [ ] `return list(lines)[:2]`
> Both wrong answers try to consume the whole input first and never finish. The generator reads only as far as the second clean line.

--- exercise 9.3

--- recap
- Iterate over `lines`; a file, list or generator all work the same.
- `line.split("#", 1)[0].strip()` drops the comment and the newline.
- `if line:` skips what is left empty.
- `yield` instead of `append` turns the loop into a lazy generator.
