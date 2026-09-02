# Format specs and column widths

--- teach
### Align and pad with a format spec
After the colon in `{value:spec}`, `<` means left-align, `>` right-align, and the number is the width to pad to. Strings default to left and numbers to right; say so when you write a table, and write the alignment anyway so the intent is on the page.
```python
>>> f"{'mbp':<10}|"
'mbp       |'
>>> f"{16:>5}|"
'   16|'
```

--- predict
What does this print?
```python
print(len(f"{'os':<6}"))
```
answer: 6
> The width pads `os` with four spaces to reach six characters. Padding never truncates: a longer value simply overflows the width.

--- teach
### The width can be a variable
Put a name in its own braces inside the spec and the width comes from data. The alignment can be a variable too. This is how one line renders every cell of a table.
```python
>>> w = 10
>>> f"{'mbp':<{w}}|"
'mbp       |'
>>> align = ">"
>>> f"{'16':{align}{w}}|"
'        16|'
```
Note that `'16'` here is a string, and it still right-aligns because the spec says so. Render every cell to text first, then decide the alignment from the *original* value.

--- fill
Complete the line so numbers go right and everything else goes left.
```python
align = "___" if is_number else "<"
```
answer: >
> `>` right-aligns, which lines up the last digits of a column of numbers. `<` left-aligns text.

--- code
Print `name` left-aligned in a field `w` characters wide, followed by `|`.
```python
name = "mbp"
w = 6
```
expect: mbp   |
solution: print(f"{name:<{w}}|")
> The inner `{w}` is replaced by 6 before the spec is applied, so the spec becomes `<6`. Three spaces of padding bring `mbp` to six characters, then the bar.

--- teach
### Widths come from the data
A column is as wide as its longest rendered cell, header included. Start with the header lengths, then raise each width with `max` as you walk the rows. `enumerate` gives you the column index. The separator line is `"-" * width` per column; join cells with two spaces.
```python
widths = [len(h) for h in headers]
for row in text_rows:
    for i, cell in enumerate(row):
        widths[i] = max(widths[i], len(cell))

sep = "  ".join("-" * w for w in widths)
```

--- code
Set `widths` to the width of each column: the longest cell in it, header included.
```python
headers = ["host", "ram"]
rows = [["mbp-1", "16"], ["win-lab-01", "8"]]
```
check: widths == [10, 3]
solution: widths = [len(h) for h in headers]
solution: for row in rows:
solution:     for i, cell in enumerate(row):
solution:         widths[i] = max(widths[i], len(cell))
> `host` is 4 wide but `win-lab-01` is 10, so the first column grows. No cell in the second column beats the header `ram`, so it stays at 3.

--- teach
### Rendering a cell, and the `bool` trap
Cells become text with `str(cell)`; `None` becomes `"-"`. `isinstance(x, sometype)` asks whether `x` is of that type (or a tuple of types). `bool` is a subclass of `int` in Python, so `isinstance(True, int)` is `True`. Exclude it explicitly, or `True` will be right-aligned like a number.
```python
def is_number(cell):
    return isinstance(cell, (int, float)) and not isinstance(cell, bool)

text = "-" if cell is None else str(cell)
```

--- quiz
What does `isinstance(True, int)` return?
- [x] `True`
- [ ] `False`
- [ ] It raises `TypeError`
> `bool` inherits from `int` (`True == 1`), so the check passes. The exercise wants bools treated as text, hence the extra `not isinstance(cell, bool)`.

--- teach
### Assemble the lines
Build a list of lines (header, separator, one per row), `rstrip()` each so no line ends in padding spaces, and join with `"\n"`. `join` adds no trailing newline. Validate first: empty headers, or a row whose length differs from `len(headers)`, raises `ValueError`.
```python
return "\n".join(line.rstrip() for line in lines)
```

--- exercise 4.7

--- recap
- `f"{x:<{w}}"` and `f"{x:>{w}}"` pad to width `w`; the width and alignment can be variables.
- Column width is the longest rendered cell, header included.
- `str(cell)`, `None` to `"-"`; numbers are `int`/`float` but not `bool`.
- `"\n".join(line.rstrip() for line in lines)` gives clean output.
