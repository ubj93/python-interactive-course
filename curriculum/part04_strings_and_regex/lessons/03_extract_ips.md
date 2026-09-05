# Finding addresses with regex

--- teach #card-f89e6cf840b75617
### `\d` is a digit; `{n,m}` says how many
`\d` matches one digit. A quantifier in braces gives a count: `\d{3}` is exactly three digits, `\d{1,3}` is one to three. `re.findall` returns every non-overlapping match.
```python
>>> import re
>>> re.findall(r"\d{2,3}", "1 22 333")
['22', '333']
```
The `1` is too short to match. Each group of an IP address is one to three digits, so `\d{1,3}` is the building block.

--- predict #card-a6d513cefb4c5d40
What does this print?
```python
import re
print(re.findall(r"\d{3}", "10.0.0.5 port 443"))
```
answer: ['443']
> Only `443` has three digits in a row. `10`, `0` and `5` are shorter, so they do not match.

--- teach #card-fe4bab02f5e25cb1
### The dot must be escaped
In a pattern `.` means "any character". A real dot is `\.`. Forgetting this is the classic bug: `r"10.0.0.1"` happily matches `10x0y0z1`.
```python
>>> re.findall(r"\d\.\d", "1.2 1x2")
['1.2']
>>> re.findall(r"\d.\d", "1.2 1x2")
['1.2', '1x2']
```

--- quiz #card-e2e8cd22443d56d7
Which pattern matches `10.0` but not `10x0`?
- [ ] `r"\d+.\d+"`
- [x] `r"\d+\.\d+"`
- [ ] `r"\d+\\.\d+"`
> `\.` is a literal dot. A bare `.` matches any character, including `x`. In a raw string `\\.` is a literal backslash followed by any character, which matches neither.

--- teach #card-2fb3b5418f465aae
### Repeat a piece with a non-capturing group
Parentheses group a piece so a quantifier applies to the whole thing. `(?:...)` is a group that does *not* capture, which matters here: `findall` returns only the captured groups when there are any, and you want the whole address.
```python
>>> re.findall(r"(?:\d{1,3}\.){3}\d{1,3}", "gw 192.168.1.1 ok")
['192.168.1.1']
```
Read it as "digits and a dot, three times, then digits".

--- predict #card-14136e07d3905741
What does this print?
```python
import re
print(re.findall(r"(\d+)\.(\d+)", "14.5"))
```
answer: [('14', '5')]
> With capturing groups, `findall` gives a tuple of the groups, not the full match. Use `(?:...)` when you want the whole text back.

--- teach #card-4a4f57123ae25d35
### Lookarounds: check the neighbours without eating them
`(?<![\d.])` means "not preceded by a digit or dot" and `(?![\d.])` means "not followed by one". They only look; they consume no characters, so a `:` or `)` next to the address is fine, but a fifth dotted group or a glued digit is rejected.
```python
>>> re.findall(r"(?<!\d)\d{3}(?!\d)", "1234 567")
['567']
```
`\b` (word boundary) is the usual trick, but a dot is not a word character, so `10.1.2.3.4` would still yield a match. Lookarounds say exactly what you mean.

--- code #card-ef1d50c37a635cf5
Print every dotted candidate in `text` that is not glued to another digit or dot on either side.
```python
import re
text = "10.1.2.3.4 gw 10.0.0.1:443 (192.168.1.20)"
```
expect: ['10.0.0.1', '192.168.1.20']
solution: print(re.findall(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])", text))
> The lookbehind and lookahead reject every way of cutting `10.1.2.3.4` into four groups, because a dot or digit is always next door. The `:` and the brackets are neither, so the other two pass.

--- teach #card-7ba65694663e546d
### Regex for shape, Python for range
`\d{1,3}` matches `999`, and a pattern that encodes 0..255 is unreadable. Let the regex find candidates, then check each group in plain Python: split on `.`, reject a leading zero, and test the number.
```python
def valid_octet(o):
    if len(o) > 1 and o[0] == "0":
        return False
    return 0 <= int(o) <= 255

all(valid_octet(o) for o in candidate.split("."))
```
Say this split out loud in an interview; it is the answer they want.

--- code #card-ea81bcc4479f52ab
Print the list of candidates whose four groups are all in the range 0 to 255.
```python
candidates = ["10.0.0.1", "256.1.1.1", "1.1.1.999"]
```
expect: ['10.0.0.1']
solution: print([c for c in candidates if all(0 <= int(o) <= 255 for o in c.split("."))])
> `split(".")` gives the groups as strings, `int` makes each a number, and `all` is true only when every group passes. The leading-zero rule is a second small check you add in the exercise.

--- exercise 4.3 #card-a3dc03ee0ee8532f

--- recap #card-bd5b0bbd7e7c5539
- `\d{1,3}` is one to three digits; `\.` is a real dot.
- `(?:...){3}` repeats a piece without capturing it.
- `(?<![\d.])` and `(?![\d.])` reject neighbours without consuming them.
- Regex finds the shape; a small Python check does the range.
