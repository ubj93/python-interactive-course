# Changing case, and a first regex

--- teach #card-e8a6dd887ce95a93
### Split on underscores and drop the empties
`split("_")` cuts `snake_case` into words. Doubled or leading underscores leave empty strings in the list, so filter them out with a list comprehension that keeps only truthy words. Lowercase each word while you are at it.
```python
>>> "__OS_VERSION__".split("_")
['', '', 'OS', 'VERSION', '', '']
>>> [w.lower() for w in "__OS_VERSION__".split("_") if w]
['os', 'version']
```
If the list ends up empty (the input was `""` or `"___"`), return `""` straight away.

--- code #card-f4bcea8550d35a3c
Set `words` to the lowercase words of `name`, with the empty pieces dropped.
```python
name = "mdm__Check_In"
```
check: words == ["mdm", "check", "in"]
solution: words = [w.lower() for w in name.split("_") if w]
> The double underscore gives an empty string between `mdm` and `Check`; `if w` drops it, and `lower()` normalises the case of what is left.

--- teach #card-213a2a577758511e
### `capitalize`, not `title`
`capitalize()` uppercases the first character and lowercases the rest. `title()` uppercases after *every* non-letter, digits included, which is wrong for `v2a`. Join the words back with `"".join(...)`; the first word stays lowercase.
```python
>>> "vERSION".capitalize()
'Version'
>>> words = ["last", "check", "in"]
>>> words[0] + "".join(w.capitalize() for w in words[1:])
'lastCheckIn'
```
`words[1:]` is every word after the first.

--- predict #card-ba0fe6b0754b555d
What does this print?
```python
print("v2a".capitalize(), "v2a".title())
```
answer: V2a V2A
> `capitalize` touches only the first character. `title` starts a new "word" after the digit and uppercases the `a` too. That is why the exercise forbids it.

--- teach #card-67b33e6924175a8c
### A character class matches one character from a set
The other direction, `camelCase` to `snake_case`, needs to find capital letters. The `re` module does this with a pattern. `[A-Z]` matches one uppercase letter; `[a-z0-9]` matches one lowercase letter or digit. Write patterns as raw strings, `r"..."`, so backslashes are passed through untouched.
```python
>>> import re
>>> re.findall(r"[A-Z]", "deviceID")
['I', 'D']
```
`re.findall` returns every match as a list of strings.

--- teach #card-98761c61afe05937
### `+` means "one or more"
A quantifier after a class says how many times it may repeat. `[A-Z]+` is a run of one or more capitals, as long as possible.
```python
>>> re.findall(r"[A-Z]+", "HTTPSProxyURL")
['HTTPSP', 'URL']
```
Notice the run swallowed the `P` of `Proxy`. An acronym ends where a capital is followed by a lowercase letter, so the pattern for that is `([A-Z]+)([A-Z][a-z])`: the capitals, then "one capital, one lowercase".

--- predict #card-027236e108975733
What does this print?
```python
import re
print(re.findall(r"[A-Z]+", "deviceID"))
```
answer: ['ID']
> `I` and `D` are next to each other, so `+` joins them into one match. With plain `[A-Z]` you got two separate matches.

--- teach #card-0a6f5b55cfa652d3
### Groups and `re.sub`
Parentheses make a group, and `re.sub(pattern, replacement, text)` replaces every match. In the replacement, `\1` and `\2` stand for what group 1 and group 2 matched. This inserts `_` between a lowercase letter or digit and the capital that follows.
```python
>>> re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", "deviceName")
'device_Name'
>>> re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", "v2Build").lower()
'v2_build'
```
Run the acronym pattern first, then this one, then `lower()` the result.

--- fill #card-da39a2270d905187
Complete the replacement so an underscore is inserted between the two groups.
```python
s = re.sub(r"([a-z0-9])([A-Z])", r"___", name)
```
answer: \1_\2
> `\1` is the character before the capital, `\2` is the capital. Putting `_` between them splits the word without losing either character.

--- code #card-383b0a6126565d58
Print `name` in snake_case: insert `_` before each capital that follows a lowercase letter or digit, then lowercase everything.
```python
import re
name = "lastCheckIn2Go"
```
expect: last_check_in2_go
solution: print(re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower())
> Three boundaries match: `tC`, `kI` and `2G`. Each gets an underscore, and `lower()` finishes the job. The digit is just another ordinary character.

--- exercise 4.2 #card-b8351e183470569f

--- recap #card-5bd2d2570f455fd7
- `[w.lower() for w in name.split("_") if w]` gives clean words.
- `capitalize()` uppercases only the first character; `title()` also fires after digits.
- `[A-Z]` matches one capital; `+` makes it a run.
- `re.sub(r"(...)(...)", r"\1_\2", s)` inserts text between two groups.
