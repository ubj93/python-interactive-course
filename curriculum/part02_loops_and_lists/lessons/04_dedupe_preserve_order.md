# Removing duplicates

--- teach
### A set remembers what it has seen
A set is a collection with no order and no duplicates. `add` puts something in; `in` asks whether it is there. Asking a set is fast no matter how big it is, while `in` on a list scans from the start every time.
```python
>>> seen = set()
>>> seen.add("nuc-01")
>>> seen.add("nuc-01")
>>> seen
{'nuc-01'}
>>> "nuc-01" in seen
True
```
`set()` makes an empty set; `{}` would make an empty dict.

--- code
Add every hostname in `hosts` to `seen`, then print how many distinct hostnames there are.
```python
hosts = ["a", "b", "a", "c", "b"]
seen = set()
```
expect: 3
solution: for h in hosts:
solution:     seen.add(h)
solution: print(len(seen))
> `add` ignores anything already present, so after the loop the set holds only a, b and c.

--- predict
What does this print?
```python
seen = set()
for h in ["a", "b", "a", "c", "a"]:
    seen.add(h)
print(len(seen))
```
answer: 3
> Adding "a" three times leaves one "a". The set holds a, b and c.

--- teach
### Why `set(hostnames)` alone is not the answer
`list(set(xs))` removes duplicates but throws away the order, and it only treats identical strings as the same: `"MBP-J-DOE"` and `"mbp-j-doe"` would both survive. When order matters, walk the list yourself and use the set only for remembering.

--- teach
### The seen-set pattern
Two containers: a set of what you have handled, and a list of what you are keeping. Check the set before you act; add to both when the item is new.
```python
seen = set()
unique = []
for h in hostnames:
    if h not in seen:
        seen.add(h)
        unique.append(h)
return unique
```
The list keeps first-occurrence order; the set makes the check fast.

--- fill
Complete the check so only new hostnames are kept.
```python
if h ___ seen:
    seen.add(h)
    unique.append(h)
```
answer: not in
> `not in` is the opposite of `in`. The first time a value appears it is not in `seen`, so it is added; later copies are skipped.

--- teach
### Compare the clean form, keep the original
Duplicates are decided after `strip().lower()`, but the caller wants the first spelling exactly as written. So put the cleaned key in the set and the raw value in the list.
```python
key = h.strip().lower()
if key not in seen:
    seen.add(key)
    unique.append(h)          # the original, not key
```
This "normalise for comparison only" split comes up constantly: emails, hostnames, serials.

--- code
Build `unique`: the first spelling of each hostname, in order, treating entries as duplicates when they match after `strip().lower()`.
```python
hosts = ["MBP-01", " mbp-01 ", "nuc-01", "NUC-01"]
```
check: unique == ["MBP-01", "nuc-01"]
solution: seen = set()
solution: unique = []
solution: for h in hosts:
solution:     key = h.strip().lower()
solution:     if key not in seen:
solution:         seen.add(key)
solution:         unique.append(h)
> The cleaned `key` goes into the set; the raw `h` goes into the list. So " mbp-01 " and "NUC-01" are recognised as repeats, and the kept spellings are the originals.

--- predict
What does this print?
```python
seen = set()
unique = []
for h in ["MBP-01", " mbp-01 ", "nuc-01"]:
    key = h.strip().lower()
    if key not in seen:
        seen.add(key)
        unique.append(h)
print(unique)
```
answer: ['MBP-01', 'nuc-01']|["MBP-01", "nuc-01"]|['MBP-01','nuc-01']
> Both first entries clean to "mbp-01", so the second is a duplicate. The kept value is the raw first spelling "MBP-01".

--- quiz
Which is true of `x in some_list` compared with `x in some_set`?
- [ ] They are the same speed
- [x] The list is scanned from the start; the set is a direct lookup
- [ ] The set version raises if `x` is missing
> Membership on a list is a scan (fifty thousand items, fifty thousand comparisons); on a set it is a hash lookup. If you test membership more than once, build a set.

--- exercise 2.4

--- recap
- A set has no order and no duplicates; `in` on a set is fast.
- Seen-set pattern: check the set, then add to both set and list.
- Compare the normalised key; keep the original value.
- `set(xs)` alone loses order and casing differences.
