# Rolling windows

--- teach
### `sum` and `len` give a mean
The mean (average) of a list is the total divided by the count. `sum` adds the items, `len` counts them, and `/` always gives a float, so `sum([5]) / 1` is `5.0`.
```python
>>> window = [10, 20]
>>> sum(window) / len(window)
15.0
```
Never divide by `len` of an empty list; `ZeroDivisionError` is the result.

--- predict
What does this print?
```python
print(sum([3, 6, 9]) / len([3, 6, 9]))
```
answer: 6.0
> 18 divided by 3. Division with `/` returns a float, so it prints `6.0`, not `6`.

--- teach
### `round` trims decimals
`round(x, 2)` returns `x` with two decimal places. Floats carry tiny errors (`0.1 + 0.2` is `0.30000000000000004`), and rounding before you return makes results predictable and testable.
```python
>>> round(5 / 3, 2)
1.67
>>> round(0.1 + 0.2, 2)
0.3
```

--- code
Set `mean` to the average of `window`, rounded to two decimal places.
```python
window = [1, 2, 2]
```
check: mean == 1.67
solution: mean = round(sum(window) / len(window), 2)
> `sum` is 5, `len` is 3, and `5 / 3` is 1.666...; `round(..., 2)` makes it 1.67.

--- fill
Complete the line so the mean is rounded to two decimals.
```python
value = ___(sum(window) / len(window), 2)
```
answer: round
> `round(number, 2)` keeps two digits after the point. The second argument is how many decimals to keep.

--- teach
### `range(len(xs))` when you really need the index
This time the position matters: the window ending at `i` depends on `i`. So loop over the indexes, and `samples[i]` is the current sample.
```python
for i in range(len(samples)):
    ...
```
An empty list gives `range(0)`, an empty loop, and you return `[]` for free. Check `n >= 1` before the loop and raise `ValueError` otherwise, as in the last lesson.

--- teach
### A window is a slice that ends at `i`
The window of the last `n` samples ending at `i` is `samples[i - n + 1:i + 1]`. Near the start, `i - n + 1` goes negative, and a negative start counts from the end of the list, which is wrong. Clamp it with `max(0, ...)`.
```python
start = max(0, i - n + 1)
window = samples[start:i + 1]
```
`max(0, -2)` is 0; `max(0, 3)` is 3. With `i = 0` the window is `samples[0:1]`, one item, so the first output is always `samples[0]`.

--- code
Set `window` to the last `n` samples ending at index `i`, clamping the start at 0 so the slice is never negative.
```python
samples = [3, 6, 9, 12, 15]
n = 3
i = 1
```
check: window == [3, 6]
solution: start = max(0, i - n + 1)
solution: window = samples[start:i + 1]
> `i - n + 1` is -1, so `max(0, -1)` clamps the start to 0 and the window is `samples[0:2]`: only two samples exist so far.

--- predict
What does this print?
```python
samples = [10, 20, 30, 40]
i = 2
n = 2
start = max(0, i - n + 1)
print(samples[start:i + 1])
```
answer: [20, 30]|[20,30]
> `i - n + 1` is 1, so the window is `samples[1:3]`: the two samples ending at index 2.

--- quiz
With `n = 3` and `i = 0`, what is `max(0, i - n + 1)`?
- [ ] `-2`
- [x] `0`
- [ ] `1`
> `0 - 3 + 1` is `-2`, and `max(0, -2)` is `0`. Without the clamp, `samples[-2:1]` would be the wrong (and usually empty) slice.

--- exercise 2.5

--- recap
- Mean: `sum(xs) / len(xs)`; `/` gives a float.
- `round(x, 2)` for two decimals.
- Loop over `range(len(xs))` only when the index itself matters.
- Window ending at `i`: `xs[max(0, i - n + 1):i + 1]`.
