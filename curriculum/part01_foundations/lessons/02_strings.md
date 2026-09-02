# Cleaning up strings

--- teach
### Strings never change; methods give you new ones
Text values are immutable. Every string method leaves the original alone and returns a new string. So you almost always write the result back to a name, or feed it straight into the next step.
```python
>>> raw = "  MBP-J-DOE "
>>> raw.strip()
'MBP-J-DOE'
>>> raw
'  MBP-J-DOE '        # unchanged
```

--- predict
What does this print?
```python
print("MBP".lower())
```
answer: mbp
> `lower()` returns a lowercase copy. The original "MBP" is untouched.

--- teach
### The four methods you will use every day
- `strip()` removes spaces, tabs and newlines from both ends.
- `lower()` / `upper()` change case.
- `split(sep)` cuts a string into a list at each `sep`.
- `replace(old, new)` swaps every `old` for `new`.
```python
>>> "a.b.c".split(".")
['a', 'b', 'c']
>>> "win_lab_01".replace("_", "-")
'win-lab-01'
```

--- teach
### Chain them, left to right
Because each method returns a new string, you can call the next method on the result. Read chains as a pipeline: strip, then lower, then split.
```python
>>> "  MBP-J-DOE.corp.example.com \n".strip().lower().split(".")
['mbp-j-doe', 'corp', 'example', 'com']
```
Indexing `[0]` on the list takes the first piece.

--- fill
Complete the chain so `name` is the trimmed, lowercased hostname.
```python
name = raw.___().lower()
```
answer: strip
> `strip()` first, so stray spaces and newlines are gone before anything else looks at the text.

--- predict
What does this print?
```python
print("mbp-j-doe.corp.example.com".split(".")[0])
```
answer: mbp-j-doe
> `split(".")` gives `['mbp-j-doe', 'corp', 'example', 'com']` and `[0]` picks the first item.

--- quiz
What is `"a_b_c".replace("_", "-")`?
- [x] `'a-b-c'`
- [ ] `'a-b_c'`
- [ ] `['a', 'b', 'c']`
> `replace` swaps every occurrence, not just the first. `split` is the one that returns a list.

--- exercise 1.2

--- recap
- String methods return new strings; the original is unchanged.
- `strip`, `lower`, `split`, `replace` cover most clean-up jobs.
- Chain methods left to right; `[0]` takes the first item of a list.
