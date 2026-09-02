# Grouping by a canonical key: anagrams

--- teach
### The pattern: group by a key everyone in the group shares
"Which app names are letter-scrambles of each other?" The brute force compares each new name against the first member of every group so far.
```python
def anagram_groups_slow(names):
    groups = []
    for name in names:
        for group in groups:
            if sorted(group[0]) == sorted(name):
                group.append(name)
                break
        else:
            groups.append([name])
    return groups
```
Each name is compared with every group, and each comparison sorts two strings. Say it: "Compare every name with every group, O(n squared) comparisons. I can do better with a dict."

--- quiz
With n names of length k, what does the brute force cost when most names are in their own group?
- [ ] O(n log n)
- [x] O(n² · k log k)
- [ ] O(n · k)
> Each of n names is compared with up to n groups, and each comparison sorts strings of length k. That is n² comparisons times k log k for the sort.

--- teach
### The insight: a canonical key
Two names are anagrams when their sorted letters are the same. `"".join(sorted(name))` turns any scramble into one fixed spelling: a **canonical key**. Anagrams share it, non-anagrams never do. So the key goes into a dict, and each name is filed under it in O(1).
```python
>>> "".join(sorted("listen"))
'eilnst'
>>> "".join(sorted("silent"))
'eilnst'
```
The same trick groups devices by `os_family`, files by checksum, or users by lowercased email. The question is always "what single value do all members share?"

--- code
Set `key` to the canonical key of `name`, the sorted letters joined back into a string, and print it.
```python
name = "silent"
```
expect: eilnst
check: key == "eilnst"
solution: key = "".join(sorted(name))
solution: print(key)
> `sorted("silent")` is `['e', 'i', 'l', 'n', 's', 't']` and `"".join` turns the list back into text. Every anagram of `silent` gives the same key.

--- predict
What does this print?
```python
print("".join(sorted("enlist")))
```
answer: eilnst
> `sorted` puts the characters in order as a list; `"".join` glues them back into a string. `enlist`, `listen` and `silent` all become `eilnst`.

--- teach
### File names under their key, in order
`dict.setdefault(key, [])` returns the list for that key, creating an empty one first if the key is new. Then `append` files the name.
```python
groups = {}
for name in names:
    key = "".join(sorted(name))
    groups.setdefault(key, []).append(name)
return list(groups.values())
```
Two order rules come free: a dict remembers the order keys were first inserted, so groups appear in the order their first member appeared, and `append` keeps names in input order inside each group. A name with no anagram is a group of one.

--- code
File each name under its canonical key with `setdefault`, then print `list(groups.values())`.
```python
names = ["listen", "google", "silent"]
groups = {}
```
expect: [['listen', 'silent'], ['google']]
solution: for name in names:
solution:     key = "".join(sorted(name))
solution:     groups.setdefault(key, []).append(name)
solution: print(list(groups.values()))
> `listen` creates the `eilnst` list, `google` creates its own, and `silent` finds `eilnst` again and is appended. The dict keeps first-insertion order, so `listen`'s group comes first.

--- fill
Complete the line that files `name` under its canonical key.
```python
groups.___(key, []).append(name)
```
answer: setdefault
> `setdefault(key, [])` gives back the existing list, or stores and returns a new empty one. `collections.defaultdict(list)` does the same job; say which you chose.

--- quiz
What does `list(groups.values())` return after filing `["abc", "Abc", "cab"]`?
- [x] `[['abc', 'cab'], ['Abc']]`
- [ ] `[['abc', 'Abc', 'cab']]`
- [ ] `[['Abc'], ['abc', 'cab']]`
> `sorted("Abc")` is `['A', 'b', 'c']`, a different key from `abc`: comparison is case-sensitive. Groups come out in first-appearance order, and `abc` appeared before `Abc`.

--- teach
### The cost, and how to say it
Each name costs one sort, O(k log k), plus one O(1) dict step. Total O(n · k log k) time and O(n · k) space for the dict.

Say it out loud: "I group by a canonical key: the sorted letters. Anagrams collapse to the same key, so a single pass through a dict does it. If the alphabet were small I could use a tuple of 26 counts as the key and drop the log factor."

Edge cases to walk through: an empty list gives `[]`, and two identical names are anagrams of each other and stay in one group.

--- exercise 12.3

--- recap
- Grouping questions want a dict keyed by a canonical value all members share.
- `"".join(sorted(name))` is the canonical key for anagrams.
- `setdefault(key, []).append(name)` files each name; dict order gives first-appearance order.
- O(n · k log k) time; comparison is exact, so case and every character matter.
