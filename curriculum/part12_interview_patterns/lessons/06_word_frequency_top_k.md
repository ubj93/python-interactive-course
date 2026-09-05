# Counting and top-k: Counter plus a heap

--- teach #card-f2dc1033269d5e59
### The pattern: count once, then pick the top k
"Which words dominate the last hour of error logs?" The brute force counts each distinct word with `text.count`, then repeatedly finds the biggest.
```python
def top_k_slow(words, k):
    distinct = set(words)
    counts = [(w, words.count(w)) for w in distinct]   # scans the list per word
    result = []
    for _ in range(min(k, len(counts))):
        best = max(counts, key=lambda wc: wc[1])        # scans the counts per pick
        counts.remove(best)
        result.append(best)
    return result
```
Two scans hide inside: `words.count` walks the whole list for every distinct word, and `max` walks the counts for every pick. Say it: "Count with a Counter, then pick the top k; O(n) to count."

--- quiz #card-93065528befa5cb2
With n words, d distinct, what does `[(w, words.count(w)) for w in distinct]` cost?
- [ ] O(n)
- [x] O(n · d)
- [ ] O(d log d)
> `count` scans all n words, and it runs once per distinct word. With 5,000 words and 100 distinct ones that is 500,000 steps for a job one pass can do.

--- teach #card-576109dc83645ac7
### The insight: `Counter` counts in one pass
`collections.Counter` is a dict from item to count, built in O(n). Lowercase first, then pull words out with the regex `\w+` (a run of letters, digits and underscores), so punctuation splits words and `Timeout` and `timeout` match.
```python
>>> import re
>>> from collections import Counter
>>> counts = Counter(re.findall(r"\w+", "Timeout again; mdmclient[512]: timeout".lower()))
>>> counts
Counter({'timeout': 2, 'again': 1, 'mdmclient': 1, '512': 1})
>>> counts.most_common(1)
[('timeout', 2)]
```
`most_common(k)` gives the biggest counts, but equal counts come out in first-seen order, not alphabetical.

--- code #card-c63715431452537c
Build `counts`: lowercase the text, pull out the words with `re.findall(r"\w+", ...)`, and count them with `Counter`. Then print `counts["timeout"]`.
```python
import re
from collections import Counter
text = "Timeout again; mdmclient[512]: timeout"
```
expect: 2
check: counts["512"] == 1 and "mdmclient" in counts
solution: counts = Counter(re.findall(r"\w+", text.lower()))
solution: print(counts["timeout"])
> Lowercasing folds `Timeout` into `timeout`, so it counts 2. `\w+` treats `[`, `]` and `:` as separators, so `mdmclient` and `512` become their own words.

--- predict #card-f0426e49f25e5dbd
What does this print?
```python
from collections import Counter
print(Counter("a b b c c c".split()).most_common(1))
```
answer: [('c', 3)]
> `Counter` counts one pass over the four-item list; `most_common(1)` returns a list holding the single top `(word, count)` tuple.

--- teach #card-2aa7bbcae6185731
### Ties broken alphabetically: sort on `(-count, word)`
When the spec says "equal counts in alphabetical order", `most_common` is not enough. Give each entry the key `(-count, word)`: bigger counts become smaller negatives and come first; equal counts fall back to the word, A to Z.
```python
import heapq
items = counts.items()                      # (word, count) pairs
heapq.nsmallest(k, items, key=lambda kv: (-kv[1], kv[0]))
```
`heapq.nsmallest(k, ...)` keeps a heap of only k entries: O(d log k). A full `sorted(items, key=...)[:k]` is O(d log d), also fine, and easier to defend when d is small.

--- code #card-b99e1b2a6b345ee7
Print the top 2 entries of `counts` using `heapq.nsmallest` with a key that puts bigger counts first and breaks ties alphabetically.
```python
import heapq
counts = {"zeta": 2, "alpha": 2, "disk": 3}
```
expect: [('disk', 3), ('alpha', 2)]
solution: print(heapq.nsmallest(2, counts.items(), key=lambda kv: (-kv[1], kv[0])))
> `disk` has the biggest count, so `(-3, 'disk')` is smallest. `alpha` and `zeta` tie at `-2`, and `'alpha' < 'zeta'`, so `alpha` takes the second slot.

--- fill #card-5714b57fa2b95a17
Complete the key so bigger counts come first and equal counts are ordered A to Z.
```python
key=lambda kv: (___kv[1], kv[0])
```
answer: -
> `kv` is `(word, count)`. Negating the count turns "biggest first" into "smallest first", which is what `nsmallest` and `sorted` do by default; the word breaks ties.

--- quiz #card-45829e32851d5397
`counts` is `{'zeta': 2, 'alpha': 2, 'disk': 3}`. What does `sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))` start with?
- [x] `('disk', 3), ('alpha', 2), ('zeta', 2)`
- [ ] `('disk', 3), ('zeta', 2), ('alpha', 2)`
- [ ] `('alpha', 2), ('disk', 3), ('zeta', 2)`
> `-3` sorts before `-2`, so `disk` leads. `alpha` and `zeta` share `-2`, so the second item of the key, the word, orders them alphabetically.

--- teach #card-dbb57c570e065958
### The cost, and how to say it
O(n) to count n words, O(d log k) to pick the top k of d distinct words, O(d) space for the counter.

Say it out loud: "Counter for the counting, then a heap keyed on `(-count, word)` so ties fall back to alphabetical. Linear to count, d log k to pick."

Guards first: `k <= 0` gives `[]`, and an empty or whitespace-only text has no words, so the counter is empty and the result is `[]`. When k is bigger than the number of distinct words, `nsmallest` simply returns them all.

--- exercise 12.6 #card-a448a8b637b35820

--- recap #card-646a15b852685414
- "Most common", "top 10 offenders": count with `Counter`, then pick.
- `re.findall(r"\w+", text.lower())` splits on punctuation and folds case.
- `most_common` ignores alphabetical ties; key on `(-count, word)` instead.
- `heapq.nsmallest(k, items, key=...)` is O(d log k); `sorted(...)[:k]` is O(d log d).
