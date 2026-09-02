# Loops and numbers

--- teach
### `for` repeats a block for each item
A `for` loop takes each item of a list in turn and runs the indented block with it. The loop variable (`unit` below) is just a name for "the current item".
```python
units = ["B", "KiB", "MiB"]
for unit in units:
    print(unit)
```
This prints B, then KiB, then MiB.

--- predict
What does this print?
```python
total = 0
for n in [1, 2, 3]:
    total = total + n
print(total)
```
answer: 6
> Each pass adds the current item: 0+1, 1+2, 3+3. After the loop, `total` is 6.

--- code
Use a `for` loop to print each hostname in `hosts` in uppercase, one per line.
```python
hosts = ["mbp-j-doe", "win-lab-01"]
```
expect: MBP-J-DOE\nWIN-LAB-01
solution: for h in hosts:
solution:     print(h.upper())
> The loop body runs once per item with `h` bound to that item. `upper()` gives the uppercase copy to print.

--- teach
### `while` repeats until a condition is false
Use `while` when you do not know how many times in advance: keep dividing while the value is still big.
```python
value = 5000
while value >= 1024:
    value = value / 1024
```
`value = value / 1024` can be shortened to `value /= 1024`. A `while` loop whose condition never becomes false runs forever; the course runner stops it after a few seconds.

--- teach
### Two kinds of division
`/` always gives a float. `//` gives the whole part only, and `%` gives the remainder. `**` is power.
```python
>>> 7 / 2
3.5
>>> 7 // 2
3
>>> 7 % 2
1
>>> 2 ** 10
1024
```

--- predict
What does this print?
```python
print(1536 // 1024, 1536 % 1024)
```
answer: 1 512
> 1536 divided by 1024 is 1 with 512 left over. `print` separates its arguments with a space.

--- teach
### Format specs control how numbers look
After the expression in an f-string, a colon starts a format spec. `.1f` means one decimal place. `,` adds thousands separators. `>8` right-aligns in 8 characters.
```python
>>> f"{1.5:.1f} KiB"
'1.5 KiB'
>>> f"{2.0:.1f}"
'2.0'
>>> f"{1234567:,}"
'1,234,567'
```
Note that `.1f` keeps the `.0`: that is why `1024` bytes shows as `1.0 KiB`.

--- fill
Complete the format so the value shows exactly one decimal place.
```python
line = f"{value:___} {unit}"
```
answer: .1f
> `.1f` is "fixed-point with 1 digit after the point". `.2f` would give two.

--- code
Divide `n` by 1024 until it is under 1024, counting how many times you divided in `steps`, then print `steps`.
```python
n = 5 * 1024 ** 3
steps = 0
```
expect: 3
check: n == 5
solution: while n >= 1024:
solution:     n = n / 1024
solution:     steps = steps + 1
solution: print(steps)
> Three divisions take 5 GiB down to 5, so `steps` is 3 and `n` ends as 5.0, which equals 5.

--- quiz
Your function is given a negative byte count, which makes no sense. The description says to raise `ValueError`. Which line does that?
- [x] `raise ValueError("bytes must be non-negative")`
- [ ] `return ValueError("bytes must be non-negative")`
- [ ] `print("ValueError: bytes must be non-negative")`
> `raise` signals an error to the caller and stops the function. Returning or printing an error object is a classic beginner mistake; the test would see a normal return value.

--- exercise 1.5

--- recap
- `for item in list:` runs the block once per item; `while cond:` runs until the condition fails.
- `/` float division, `//` whole part, `%` remainder, `**` power.
- `f"{x:.1f}"` formats with one decimal.
- `raise ValueError("...")` reports bad input.
