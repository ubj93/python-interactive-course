# Sets and set operations

--- teach
### A set holds each value once
A set is an unordered collection of distinct values. `set(iterable)` builds one, dropping duplicates; `s.add(x)` inserts. `set()` is the empty set; `{}` is an empty dict, not a set.
```python
>>> set(["C02A", "C02A", "C02B"])
{'C02A', 'C02B'}
>>> "C02A" in {"C02A", "C02B"}
True
```
Membership is fast no matter how big the set is, which is why a fleet comparison uses sets and not nested loops.

--- predict
What does this print?
```python
print(len(set(["A", "A", "B"])))
```
answer: 2
> The two `A`s collapse into one member. Duplicates in an input source count once, exactly as the exercise requires.

--- teach
### Difference, intersection, union
Three operators do the reconciling. `a - b` is what is in `a` but not `b`. `a & b` is what is in both. `a | b` is everything in either.
```python
>>> mdm = {"A", "B", "C"}
>>> inv = {"B", "C", "D"}
>>> mdm - inv
{'A'}
>>> mdm & inv
{'B', 'C'}
>>> mdm | inv
{'A', 'B', 'C', 'D'}
```
Say the complexity in an interview: set difference is linear in the sizes; the nested-loop version is `n × m`.

--- predict
What does this print?
```python
print(sorted({"A", "B", "C"} - {"B"}))
```
answer: ['A', 'C']
> `-` removes every member of the right set from the left. `sorted` turns the result into an ordered list.

--- code
Set `only_mdm` to the serials in `mdm` but not `inv`, and `both` to the serials in both.
```python
mdm = {"A", "B", "C"}
inv = {"B", "C", "D"}
```
check: only_mdm == {"A"}
check: both == {"B", "C"}
solution: only_mdm = mdm - inv
solution: both = mdm & inv
> `-` is difference and `&` is intersection. Both return new sets and leave `mdm` and `inv` as they were.

--- quiz
`p` is the purchased set, `m` the MDM and `i` the inventory. Which expression is "purchased but seen by neither"?
- [x] `p - (m | i)`
- [ ] `p - (m & i)`
- [ ] `(m | i) - p`
> Subtract everything either system knows about, which is the union `m | i`. Subtracting only the intersection would keep serials that one system saw; the third is the reverse question.

--- teach
### Normalise while you build the set
A set comprehension is `{expr for x in source if cond}`. Strip and uppercase each serial, and drop the ones that are blank after stripping. It reads any iterable once: a list, a tuple, a set, or a generator that can only be consumed one time.
```python
def serials(source):
    return {s.strip().upper() for s in source if s.strip()}
```
Doing this once per input means every later operation compares clean values, and `" c02a "` and `"C02A"` are the same member.

--- fill
Complete the comprehension so blank serials are dropped.
```python
return {s.strip().upper() for s in source ___ s.strip()}
```
answer: if
> The `if` at the end filters: an empty string after stripping is falsy, so it is skipped. The `upper()` on the kept ones makes the comparison case-insensitive.

--- code
Set `clean` to the set of serials in `raw`, stripped and uppercased, with blank entries dropped.
```python
raw = [" c02a ", "C02A", "c02b", " "]
```
check: clean == {"C02A", "C02B"}
solution: clean = {s.strip().upper() for s in raw if s.strip()}
> The two spellings of `C02A` become the same member and the blank entry fails the `if`. Two members remain, whatever order the list had.

--- teach
### Sort before returning
A set has no order, and the order of a set of strings can change between runs. The spec, and every test, wants sorted lists, so wrap each result in `sorted(...)`. When `purchased` is `None`, use `set()` so the `"neither"` list is empty.
```python
p = serials(purchased) if purchased is not None else set()
return {"only_mdm": sorted(m - i), ...}
```

--- exercise 5.4

--- recap
- `set(...)` deduplicates; `set()` is empty, `{}` is a dict.
- `a - b`, `a & b`, `a | b`: difference, intersection, union.
- `{s.strip().upper() for s in src if s.strip()}` normalises any iterable into a set.
- Sets are unordered: `sorted(...)` before you return.
