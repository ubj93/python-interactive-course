# A comparable value type

--- teach #card-13faae4185995667
### Parse once, in `__init__`
`Version("v14.5.0")` must become a tuple of ints. Strip whitespace, drop one leading `v`/`V`, split on `.`, and check every piece with `str.isdigit()`, which is `False` for an empty string, so `"1..2"` and `""` fail naturally. Raise `ValueError` with the original text in the message.
```python
text = original.strip()
if text[:1] in ("v", "V"):
    text = text[1:]
pieces = text.split(".")
if not all(p.isdigit() for p in pieces):
    raise ValueError(f"invalid version: {original!r}")
numbers = [int(p) for p in pieces]
```

--- code #card-187a696351fd5626
Set `parts` to a tuple of ints parsed from `text`: strip it, drop the leading `v`, split on `.`, convert each piece.
```python
text = " v14.5.1 "
```
check: parts == (14, 5, 1)
solution: text = text.strip()
solution: if text[:1] in ("v", "V"):
solution:     text = text[1:]
solution: parts = tuple(int(p) for p in text.split("."))
> Strip first so the `v` is really at position 0, slice it off, then `int()` each piece of the split. `tuple(...)` freezes the result so it can be compared and hashed later.

--- predict #card-30e08d8535c351c9
What does this print?
```python
print("".isdigit(), "12".isdigit(), "1a".isdigit())
```
answer: False True False
> `isdigit` is True only for a non-empty string made entirely of digits. That single check rejects empty pieces, letters and suffixes like `-beta`.

--- teach #card-6fece729768c558a
### Trailing zeros go, but keep at least one part
`"1.2.0"` and `"1.2"` must be the same version, so remove zeros from the end. A `while` loop on the list, stopping at length one, does it; then freeze the result as a tuple, because tuples can be hashed and compared.
```python
while len(numbers) > 1 and numbers[-1] == 0:
    numbers.pop()
self.parts = tuple(numbers)      # "1.2.0" -> (1, 2); "0.0.0" -> (0,)
```
The properties are then simple: `major` is `self.parts[0]`, and `minor` is `self.parts[1] if len(self.parts) > 1 else 0`.

--- code #card-8caf86951c8e5c5b
Remove trailing zeros from `numbers` in place, but never make it shorter than one element. Do the same to `zeros`.
```python
numbers = [1, 2, 0, 0]
zeros = [0, 0, 0]
```
check: numbers == [1, 2]
check: zeros == [0]
solution: while len(numbers) > 1 and numbers[-1] == 0:
solution:     numbers.pop()
solution: while len(zeros) > 1 and zeros[-1] == 0:
solution:     zeros.pop()
> The `len(...) > 1` guard is what stops `[0, 0, 0]` from collapsing to an empty list. `pop()` with no argument removes the last element.

--- predict #card-414c8839a0c05e9f
What does this print?
```python
print((1, 10) > (1, 9), "1.10" > "1.9")
```
answer: True False
> Tuples compare element by element as numbers: 10 beats 9. Strings compare character by character, and `"1"` comes before `"9"`, so text comparison gets versions wrong. That is why `parts` is a tuple of ints.

--- teach #card-46efcd470ad5536b
### `__eq__`, `__lt__`, and `total_ordering` for the rest
Write two comparisons and let `functools.total_ordering` derive `<=`, `>` and `>=`. Both return `NotImplemented` for a non-Version: `==` then becomes `False`, and `<` raises `TypeError`, which is right.
```python
from functools import total_ordering

@total_ordering
class Version:
    def __eq__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self.parts == other.parts

    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self.parts < other.parts
```

--- quiz #card-6f89d7ecc51a566a
What does `@total_ordering` need you to define?
- [ ] All six comparison methods
- [x] `__eq__` plus one of `__lt__`, `__le__`, `__gt__`, `__ge__`
- [ ] Only `__lt__`
> It fills in the missing four from `__eq__` and any one ordering method. It does not add `__eq__` for you, and without `__eq__` the derived methods cannot tell "less" from "less or equal".

--- teach #card-7bbb6a7a59f2503a
### `__str__`, `__repr__` and `__hash__`
`str(v)` is the friendly form: the parts joined with dots. `repr(v)` is the rebuilding call, so wrap `str(self)` with `!r` to get the quotes. Since you defined `__eq__`, add `__hash__` on the same data.
```python
def __str__(self):
    return ".".join(str(p) for p in self.parts)

def __repr__(self):
    return f"Version({str(self)!r})"

def __hash__(self):
    return hash(self.parts)
```
`join` needs strings, hence `str(p)` for each int.

--- fill #card-8029b1fb1c1e5f2d
Complete the hash so equal versions share a hash.
```python
def __hash__(self):
    return hash(self.___)
```
answer: parts
> `__eq__` compares `parts`, so `__hash__` must use `parts` too. Hashing the original text would give `"1.2"` and `"1.2.0"` different hashes even though they are equal.

--- exercise 8.5 #card-5952f65fc9515c40

--- recap #card-bbb0843951e05b03
- Parse in `__init__`: strip, drop one `v`, split on `.`, `isdigit` every piece, `int` them.
- Pop trailing zeros but never below one part; store a tuple.
- Tuples of ints compare numerically; strings do not.
- `__eq__` + `__lt__` + `@total_ordering` gives all six operators; `__hash__` on `parts`.
