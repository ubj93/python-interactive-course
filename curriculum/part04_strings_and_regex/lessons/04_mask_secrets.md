# Replacing with re.sub

--- teach #card-7249e7e33dc35b68
### `re.sub` replaces every match
`re.sub(pattern, replacement, text)` finds each match of the pattern and swaps in the replacement. It returns a new string; text with no match comes back unchanged, which is one of this exercise's rules for free.
```python
>>> import re
>>> re.sub(r"\d+", "#", "pid 512 and 33")
'pid # and #'
```

--- predict #card-0dded3248923581f
What does this print?
```python
import re
print(re.sub(r"\s+", " ", "a   b\tc"))
```
answer: a b c
> `\s` is any whitespace and `+` makes it a run, so each run of spaces or tabs becomes one space.

--- teach #card-c91434d4a5dd5c02
### Alternation and a class of literal characters
`a|b` matches either side. `[=:]` matches one character that is `=` or `:`. `\s*` is zero or more whitespace characters. Together they describe "one of these key names, optional spaces, a separator, optional spaces".
```python
>>> re.findall(r"(?:password|token)\s*[=:]\s*", "password = x token:y")
['password = ', 'token:']
```
Wrap the alternation in `(?:...)` so the `|` does not swallow the rest of the pattern.

--- teach #card-255ee9939d3f5e63
### A negated class stops at the delimiter
`[^...]` matches one character that is *not* in the set. `[^\s;,&]+` is a run of characters that are not whitespace, `;`, `,` or `&`, so it runs to the end of the value and no further.
```python
>>> re.search(r"=([^\s;,&]+)", "pw=abcd;x").group(1)
'abcd'
```
Because `+` needs at least one character, `password=` with nothing after it does not match at all, which is exactly the "no value, leave it alone" rule.

--- code #card-afeface1ee805128
Print the value that follows `password=` in `line`, stopping at the first delimiter.
```python
import re
line = "user=jdoe password=hunter2;host=mbp-1"
```
expect: hunter2
solution: print(re.search(r"password=([^\s;,&]+)", line).group(1))
> The negated class runs from `h` to `2` and stops at the `;`. `group(1)` is the captured value; `group(0)` would include `password=`.

--- teach #card-c391cb09cdbb59a4
### The replacement can be a function
Pass a function instead of a string and `re.sub` calls it once per match with the `Match` object. Whatever the function returns is inserted. `m.group(1)` is the text of group 1. Use group 1 for the part to keep and group 2 for the value.
```python
def mask(m):
    value = m.group(2)
    return m.group(1) + "*" * (len(value) - 4) + value[-4:]

re.sub(r"(password=)(\S+)", mask, "password=hunter2secret")
# 'password=*********cret'
```
`"*" * n` repeats the star n times and `value[-4:]` is the last four characters.

--- fill #card-ec7c3db42edc5b6e
Complete the mask so only the last four characters stay visible.
```python
return m.group(1) + "*" * (len(value) - 4) + value[___]
```
answer: -4:
> `value[-4:]` is a slice from four-before-the-end to the end. For a value of four characters or fewer, mask everything instead: `"*" * len(value)`.

--- code #card-60b46e06964d5f0b
Use `re.sub` with the function `mask` to mask the token in `line`, then print the result.
```python
import re
def mask(m):
    return m.group(1) + "*" * (len(m.group(2)) - 4) + m.group(2)[-4:]
line = "token=abcdefgh ok"
```
expect: token=****efgh ok
solution: print(re.sub(r"(token=)(\S+)", mask, line))
> Group 1 is `token=`, group 2 is the value. `re.sub` calls `mask` once for the match and inserts what it returns; the ` ok` after the value is not part of the match, so it stays.

--- teach #card-047b678035fe56b5
### Case-insensitive, but only where you want it
`re.compile(pattern, re.IGNORECASE)` makes the whole pattern ignore case. For this exercise `Password` must match but `bearer` must not, so scope the flag to one piece with `(?i:...)`.
```python
>>> re.findall(r"(?i:token)=", "Token= token= TOKEN=")
['Token=', 'token=', 'TOKEN=']
```
Put the finished pattern in a module-level `re.compile(...)` with an `UPPER_CASE` name; `SECRET.sub(mask, text)` then reads like a sentence.

--- quiz #card-1199626021a65313
Which keeps `Bearer` case-sensitive while the key names ignore case?
- [ ] `re.compile(pattern, re.IGNORECASE)`
- [x] `(?i:password|passwd|secret|token)` inside the pattern
- [ ] Call `text.lower()` before matching
> The `(?i:...)` group limits the flag to the key names. The module flag affects everything, and lowercasing the text would change the output, which must stay exactly as written outside the masked value.

--- exercise 4.4 #card-6627872fc9525841

--- recap #card-69b182e9d45d577d
- `re.sub(p, repl, s)` returns a new string; no match means no change.
- `a|b` is either; `[=:]` is one of; `[^\s;,&]+` runs until a delimiter.
- A function as `repl` gets the `Match` and returns the text to insert.
- `(?i:...)` scopes case-insensitivity to part of the pattern.
