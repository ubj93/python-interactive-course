# Splitting a line into fields

--- teach #card-66aea3373384500d
### Split on the separator, then clean each piece
A `key=value` line is a list of fields joined by `;`. `split(";")` cuts it back into a list. The pieces keep their spaces, and a trailing `;` leaves an empty piece at the end, so strip each one and skip the empties.
```python
>>> "a=1; b=2;".split(";")
['a=1', ' b=2', '']
```
```python
for field in line.split(";"):
    field = field.strip()
    if not field:
        continue          # skip to the next field
```
`continue` jumps straight to the next loop pass. `not field` is true for the empty string.

--- predict #card-69bbca16e7155096
What does this print?
```python
print(len("a=1;;b=2;".split(";")))
```
answer: 4
> The pieces are `'a=1'`, `''`, `'b=2'` and `''`: a doubled `;;` and a trailing `;` each leave an empty piece. Your loop must skip those.

--- code #card-19aa92c8a4145780
Print each field of `line` stripped of spaces, one per line, skipping the empty ones.
```python
line = "a=1; b=2;;"
```
expect: a=1\nb=2
solution: for field in line.split(";"):
solution:     field = field.strip()
solution:     if field:
solution:         print(field)
> `split(";")` gives four pieces, two of them empty after stripping. The `if field:` test drops those; `print` shows the other two on their own lines.

--- teach #card-24e186140b025298
### `partition` splits once and never fails
`split("=")` would cut `token=abc=def` into three pieces. `partition("=")` cuts at the *first* `=` only and always returns three parts: before, the separator, after.
```python
>>> "token=abc=def".partition("=")
('token', '=', 'abc=def')
>>> "broken".partition("=")
('broken', '', '')
```
When the separator is missing there is no error: the middle part is `''` and the tail is `''`. Unpack the three parts into names in one line.
```python
key, sep, value = field.partition("=")
```

--- quiz #card-e69b57d84fd3521b
What does `"broken".partition("=")` return?
- [ ] It raises `ValueError`
- [x] `('broken', '', '')`
- [ ] `('broken',)`
> `partition` never raises and always gives a 3-tuple. The empty middle part is your signal that the `=` was missing; `split("=", 1)` would give a one-item list and `key, value = ...` would crash on it.

--- code #card-17d061abc81c578c
Set `key` and `value` to the stripped text before and after the first `=` of `field`.
```python
field = " token = abc=def "
```
check: key == "token"
check: value == "abc=def"
solution: key, sep, value = field.partition("=")
solution: key = key.strip()
solution: value = value.strip()
> `partition` cuts at the first `=` only, so the value keeps its own `=`. Each part is stripped separately; stripping the whole field first would not remove the spaces around the `=`.

--- teach #card-b8b5edd840115db1
### Use the empty separator to spot bad fields
After `partition`, an empty `sep` means "no `=` here", and an empty `key` after stripping means "nothing before the `=`". Both are errors for this exercise, so raise.
```python
key, sep, value = field.partition("=")
key = key.strip()
if not sep or not key:
    raise ValueError(f"malformed field: {field!r}")
```
`{field!r}` puts the repr in the message, so quotes and spaces are visible. An empty *value* (`note=`) is allowed: it becomes `''`.

--- fill #card-f85259090dca5f41
Complete the line so the value may itself contain `=` signs.
```python
key, sep, value = field.___("=")
```
answer: partition
> `partition` splits at the first `=` only, so `abc=def` stays whole. `split("=")` would break it apart.

--- teach #card-ae391001c10a593f
### Build the dict as you go
Start with an empty dict `{}` and assign each pair with `result[key] = value`. Assigning to a key that already exists overwrites the old value, which is exactly the "later value wins" rule.
```python
result = {}
for field in line.split(";"):
    ...
    result[key] = value.strip()
return result
```
A blank line has only empty fields, so the loop skips everything and `{}` comes back on its own.

--- predict #card-b2668a4b8a4c5cc4
What does this print?
```python
d = {}
d["os"] = "macOS"
d["os"] = "Windows"
print(d)
```
answer: {'os': 'Windows'}
> A dict holds one value per key. The second assignment replaces the first; nothing is appended.

--- exercise 4.1 #card-6573c3c1e3035be8

--- recap #card-7483c5fe2fe3512a
- `split(";")` cuts a line into fields; strip each and skip the empty ones.
- `partition("=")` splits once, keeps the rest whole, and never raises.
- An empty separator or empty key means a malformed field: `raise ValueError`.
- `result[key] = value` inserts or overwrites, so the later value wins.
