# Top k with a heap

--- teach #card-ce2321fe0d00505b
### The simple answer: sort, then slice
"Top k by disk usage" can be written as a full sort in descending order, then the first `k` items. `reverse=True` flips the order and `[:k]` slices. It is clear and correct.
```python
sorted(items, key=key, reverse=True)[:k]
```
The cost: it sorts all `n` items and holds the whole list, even when `k` is ten out of fifty thousand.

--- code #card-2109a17df5bb578d
Set `top2` to the two entries in `usage` with the highest usage (the second element), highest first, using `sorted`.
```python
usage = [("mbp-j-doe", 0.91), ("win-lab-01", 0.42), ("mbp-a-lee", 0.97)]
```
check: top2 == [("mbp-a-lee", 0.97), ("mbp-j-doe", 0.91)]
solution: top2 = sorted(usage, key=lambda d: d[1], reverse=True)[:2]
> The key picks the usage number, `reverse=True` puts the largest first, and the slice keeps two. The whole list was sorted to get there.

--- predict #card-098d6f65878056d7
What does this print?
```python
print(sorted([3, 9, 5, 7], reverse=True)[:2])
```
answer: [9, 7]
> The descending sort is `[9, 7, 5, 3]` and the slice keeps the first two.

--- teach #card-311b3d8534c45c57
### `heapq.nlargest`: the same answer, holding only `k` items
`heapq.nlargest(k, items, key=key)` returns the `k` items with the largest keys, largest first. Internally it keeps a heap of `k` candidates and streams through the input once, so it works on a generator and never builds the full sorted list. Ties keep input order, exactly like the sort.
```python
>>> import heapq
>>> usage = [("mbp-j-doe", 0.91), ("win-lab-01", 0.42), ("mbp-a-lee", 0.97)]
>>> heapq.nlargest(2, usage, key=lambda d: d[1])
[('mbp-a-lee', 0.97), ('mbp-j-doe', 0.91)]
```
`heapq.nsmallest` is the mirror image.

--- code #card-c9f35e5959e358f5
Set `top2` to the same two entries, highest usage first, this time with `heapq.nlargest`. The input is a one-shot generator, so do not sort or index it.
```python
import heapq
usage = (row for row in [("mbp-j-doe", 0.91), ("win-lab-01", 0.42), ("mbp-a-lee", 0.97)])
```
check: top2 == [("mbp-a-lee", 0.97), ("mbp-j-doe", 0.91)]
solution: top2 = heapq.nlargest(2, usage, key=lambda d: d[1])
> `nlargest` walks the generator once, keeping only the two best candidates seen so far, and returns them largest first. Same answer as the sort, without ever holding the full list.

--- teach #card-8f7e6eb88db058b8
### Edge cases: `k <= 0` and `k` larger than the input
`nlargest` returns `[]` for `k <= 0` and simply returns every item, sorted, when `k` is bigger than the input. An explicit guard makes the intent obvious to a reader and costs nothing.
```python
if k <= 0:
    return []
return heapq.nlargest(k, items, key=key)
```
Do not call `len(items)` or iterate twice: `items` may be a one-shot generator.

--- quiz #card-0a4487ea198152f9
When does `heapq.nlargest` beat `sorted(...)[:k]`?
- [ ] Always; it is a faster sort
- [x] When `k` is small compared with `n`, or the input is a stream that should not be held in memory
- [ ] When `k` is close to `n`
> `nlargest` is O(n log k) time and O(k) memory; sorting is O(n log n) and O(n). For small `k` on a big input that is a real win. When `k` is close to `n` it does about the same work and `sorted` is simpler. Say the trade-off out loud.

--- exercise 9.7 #card-f140f8ae79025b2e

--- recap #card-6656a5639ab75683
- `sorted(items, key=key, reverse=True)[:k]` is the simple, correct answer.
- `heapq.nlargest(k, items, key=key)` gives the same result holding only `k` items.
- Both keep input order among ties; both accept any key function.
- Prefer the heap for small `k` on large or streaming input; prefer sort when `k` is near `n`.
