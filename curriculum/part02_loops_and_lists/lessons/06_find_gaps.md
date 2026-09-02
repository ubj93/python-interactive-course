# Walking neighbours

--- teach
### A tuple is a fixed pair
A tuple is like a list, but written with parentheses and unchangeable once made. Use it for "two values that belong together", like the start and end of a range. Reading a tuple uses the same `[0]`, `[1]` as a list.
```python
>>> gap = (103, 104)
>>> gap[0]
103
>>> gaps = []
>>> gaps.append((107, 109))
>>> gaps
[(107, 109)]
```
Note the double parentheses in `append((107, 109))`: the inner pair makes the tuple, the outer pair calls `append`.

--- teach
### Unpacking: one name per item
Python can split a tuple into names in one line. This is called unpacking, and it works in a `for` loop too, when every item is a pair.
```python
>>> start, end = (103, 104)
>>> start
103
>>> for a, b in [(1, 2), (5, 9)]:
...     print(b - a)
1
4
```

--- predict
What does this print?
```python
lo, hi = (7, 9)
print(hi - lo)
```
answer: 2
> Unpacking gives `lo = 7` and `hi = 9`. Then `9 - 7`.

--- teach
### `zip` pairs each item with its neighbour
`zip(xs, ys)` walks two lists side by side, giving one pair per step, and stops when the shorter one runs out. Pass the same list twice, shifted by one (`xs[1:]`), and each pair is an item with the item after it.
```python
>>> tags = [100, 101, 105]
>>> list(zip(tags, tags[1:]))
[(100, 101), (101, 105)]
>>> for prev, cur in zip(tags, tags[1:]):
...     print(cur - prev)
1
4
```
The last item has no neighbour, so it is never a `prev`; `zip` cannot walk off the end.

--- code
Print the difference between each tag and the one before it, one per line.
```python
tags = [100, 101, 105, 110]
```
expect: 1\n4\n5
solution: for prev, cur in zip(tags, tags[1:]):
solution:     print(cur - prev)
> `zip(tags, tags[1:])` gives (100, 101), (101, 105), (105, 110). Unpacking each pair into `prev, cur` makes the subtraction read naturally.

--- predict
What does this print?
```python
tags = [1, 2, 4]
print(list(zip(tags, tags[1:])))
```
answer: [(1, 2), (2, 4)]|[(1,2), (2,4)]|[(1,2),(2,4)]
> `tags[1:]` is `[2, 4]`. Pairing position by position gives (1, 2) and (2, 4); the third element of `tags` has no partner, so zip stops.

--- teach
### Reading a pair of neighbours
The difference `cur - prev` tells you everything. `1` means consecutive: nothing missing. `0` is a duplicate: also nothing missing. Bigger than `1` means the numbers strictly between are missing, from `prev + 1` to `cur - 1`. Negative means the input is not sorted: raise `ValueError`.
```python
for prev, cur in zip(tags, tags[1:]):
    if cur < prev:
        raise ValueError("tags must be sorted ascending")
    if cur - prev > 1:
        gaps.append((prev + 1, cur - 1))
```
An empty list or a single tag yields no pairs, so `gaps` stays `[]`.

--- code
Fill `gaps` with a `(start, end)` tuple for every run of missing numbers between neighbours in `tags`.
```python
tags = [1, 2, 4, 7, 7, 8]
gaps = []
```
check: gaps == [(3, 3), (5, 6)]
solution: for prev, cur in zip(tags, tags[1:]):
solution:     if cur - prev > 1:
solution:         gaps.append((prev + 1, cur - 1))
> Only pairs with a difference above 1 are gaps: (2, 4) gives (3, 3) and (4, 7) gives (5, 6). The duplicate pair (7, 7) has a difference of 0 and adds nothing.

--- fill
Complete the tuple that describes the numbers missing between `prev` and `cur`.
```python
gaps.append((prev + 1, ___))
```
answer: cur - 1|cur-1
> The gap is everything strictly between the two neighbours. For neighbours 102 and 105 that is (103, 104): `102 + 1` up to `105 - 1`.

--- quiz
`find_gaps([7, 7, 9])` should return `[(8, 8)]`. What does the pair `(7, 7)` contribute?
- [x] Nothing: `cur - prev` is 0, which is not greater than 1
- [ ] The gap `(8, 6)`
- [ ] A `ValueError`, because 7 is not less than 7
> Duplicates have a difference of 0. Only a difference above 1 is a gap, and only a negative difference (`cur < prev`) means unsorted input.

--- exercise 2.6

--- recap
- A tuple `(a, b)` is a fixed pair; `append((a, b))` needs double parentheses.
- `a, b = pair` unpacks; so does `for a, b in pairs:`.
- `zip(xs, xs[1:])` pairs every item with the next one.
- Difference > 1 is a gap `(prev + 1, cur - 1)`; negative means unsorted.
