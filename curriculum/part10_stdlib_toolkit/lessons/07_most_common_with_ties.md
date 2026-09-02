# Top N, with ties decided

--- teach
### `most_common` leaves ties to chance
`Counter(items).most_common(n)` returns the `n` biggest `(item, count)` pairs. When two counts are equal, the one seen **first** wins. So the same inventory in a different order gives a different report, and a dashboard that changes for no reason gets ignored.
```python
>>> from collections import Counter
>>> Counter(["Zoom", "Chrome", "Zoom", "Chrome"]).most_common(1)
[('Zoom', 2)]
>>> Counter(["Chrome", "Zoom", "Chrome", "Zoom"]).most_common(1)
[('Chrome', 2)]
```

--- predict
What does this print?
```python
from collections import Counter
print(Counter(["Zoom", "Chrome", "Zoom", "Chrome"]).most_common(1))
```
answer: [('Zoom', 2)]
> Both have count 2. `most_common` keeps first-seen order for ties, and `"Zoom"` appeared first.

--- teach
### A composite key makes the order yours
Sort the pairs yourself with the key from lesson 10.5: count descending (negate it), then item ascending. Now equal counts are alphabetical no matter how the input arrived. `Counter` accepts any iterable, so a generator works too, and `[:n]` on a short list simply returns everything.
```python
>>> ranked = sorted(Counter(["Zoom", "Chrome", "Zoom", "Chrome"]).items(),
...                 key=lambda kv: (-kv[1], kv[0]))
>>> ranked[:1]
[('Chrome', 2)]
```

--- code
Set `top` to the two most common apps as `(name, count)` pairs, with ties in alphabetical order.
```python
from collections import Counter
apps = ["Zoom", "Chrome", "Zoom", "Chrome", "Slack"]
```
check: top == [("Chrome", 2), ("Zoom", 2)]
solution: ranked = sorted(Counter(apps).items(), key=lambda kv: (-kv[1], kv[0]))
solution: top = ranked[:2]
> `Counter` counts, the composite key orders, and `[:2]` keeps two. `most_common(2)` would have put `"Zoom"` first because it was seen first.

--- predict
What does this print?
```python
from collections import Counter
apps = ["Zoom", "Chrome", "Zoom", "Chrome", "Slack"]
ranked = sorted(Counter(apps).items(), key=lambda kv: (-kv[1], kv[0]))
print(ranked[:2])
```
answer: [('Chrome', 2), ('Zoom', 2)]
> Both have count 2, so the second part of the key decides: `"Chrome"` sorts before `"Zoom"`. `"Slack"` with 1 is cut by the slice.

--- teach
### Including everything tied with the last place
With `include_ties`, "top 3" means the top 3 plus anyone with the same count as the third. Read the cutoff count from `ranked[n - 1]`, then walk forward while the count still equals it.
```python
cutoff = ranked[n - 1][1]
end = n
while end < len(ranked) and ranked[end][1] == cutoff:
    end += 1
return ranked[:end]
```
The `end < len(ranked)` test comes first so you never index past the list.

--- code
Move `end` past `n` while the counts stay tied with the n-th entry, then print `ranked[:end]`.
```python
ranked = [("Slack", 3), ("Zoom", 2), ("Chrome", 1), ("Firefox", 1)]
n = 3
```
expect: [('Slack', 3), ('Zoom', 2), ('Chrome', 1), ('Firefox', 1)]
solution: cutoff = ranked[n - 1][1]
solution: end = n
solution: while end < len(ranked) and ranked[end][1] == cutoff:
solution:     end += 1
solution: print(ranked[:end])
> The third entry has count 1, and so does `"Firefox"`, so `end` moves from 3 to 4 and the slice includes all four.

--- fill
Complete the loop that extends the slice past `n` while counts stay tied.
```python
cutoff = ranked[n - 1][1]
end = n
while end < len(ranked) and ranked[end][1] == ___:
    end += 1
```
answer: cutoff
> `cutoff` is the count of the n-th entry. Every following entry with that same count belongs in the result.

--- teach
### Edge cases first
Handle the degenerate inputs before the real work: `n <= 0` returns `[]`, and so does an empty `items` (the sorted list is empty). When `n` is at least the number of distinct items there is nothing beyond the slice to extend, so return `ranked[:n]` straight away.
```python
if n <= 0:
    return []
ranked = sorted(Counter(items).items(), key=lambda kv: (-kv[1], kv[0]))
if not ranked or not include_ties or n >= len(ranked):
    return ranked[:n]
```

--- quiz
`ranked` has 4 entries. What does `ranked[:10]` return?
- [x] All 4 entries
- [ ] `IndexError`
- [ ] 4 entries padded with `None`
> Slicing never raises for a stop beyond the end; it stops at the last item. That is why "n larger than distinct items" needs no special code.

--- exercise 10.7

--- recap
- `Counter.most_common` orders ties by first appearance, so output depends on input order.
- `sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))` makes ties alphabetical.
- To include ties, read the n-th count and extend while the next count equals it.
- `n <= 0` or empty input returns `[]`; a slice past the end is safe.
