# Reading rate-limit headers

--- teach #card-e83972eccbd558b0
### What the server tells you
APIs report your quota in response headers: `X-RateLimit-Remaining` (requests left), `X-RateLimit-Reset` (a unix timestamp, seconds since 1970, when the quota refills) and, with a 429, `Retry-After` (seconds to wait). The exercise packs the answer into a `namedtuple`, a tuple whose fields have names.
```python
>>> from collections import namedtuple
>>> RateLimit = namedtuple("RateLimit", ["remaining", "reset_in"])
>>> rl = RateLimit(12, 60.0)
>>> rl.remaining, rl.reset_in
(12, 60.0)
>>> RateLimit(remaining=None, reset_in=None)
RateLimit(remaining=None, reset_in=None)
```
`None` means "the server did not say".

--- teach #card-b2aa63a9d1795def
### Header names are case-insensitive
HTTP does not care whether it is `X-RateLimit-Reset` or `x-ratelimit-reset`, and different libraries hand you different spellings. So never `headers["X-RateLimit-Reset"]`. Either loop and compare with `.lower()`, or lowercase all the keys once and use `.get`. Values are strings and may carry whitespace.
```python
def _header(headers, name):
    want = name.lower()
    for key, value in headers.items():
        if key.lower() == want:
            return value
    return None
```

--- code #card-e0d45972dfd15eb7
Write `get_header(headers, name)` that returns the value whose key matches `name` ignoring case, or `None`. Then print `get_header(headers, "retry-after")`.
```python
headers = {"Content-Type": "application/json", "Retry-After": "30"}
```
expect: 30
check: get_header(headers, "x-nope") is None
solution: def get_header(headers, name):
solution:     for key, value in headers.items():
solution:         if key.lower() == name.lower():
solution:             return value
solution:     return None
solution: print(get_header(headers, "retry-after"))
> Lowercasing both sides makes `"Retry-After"` match `"retry-after"`. Falling off the end of the loop returns `None` for a header that is not there.

--- predict #card-928cc61d29b754a8
What does this print?
```python
headers = {"X-RateLimit-Remaining": " 3 "}
lowered = {k.lower(): v for k, v in headers.items()}
print(lowered.get("x-ratelimit-remaining").strip())
```
answer: 3
> Lowercasing the keys once makes any spelling match; `strip()` removes the padding around the value.

--- teach #card-677e2218716b5cbe
### "A number, or None"
A header value like `"lots"` is not an error in your code; it is a server you cannot trust. Try to convert, and turn failure into `None`, so the rest of the function only deals with numbers or "missing". One tiny helper keeps every call site clean.
```python
def _number(text):
    if text is None:
        return None
    try:
        return float(text.strip())
    except ValueError:
        return None
```
`remaining` is an int, so wrap it: `int(value)` when the value is not `None`.

--- code #card-3d8f4540893d5949
Write `to_number(text)` that returns `float(text.strip())`, or `None` when `text` is `None` or not numeric. Then print `to_number(" 12 ")`.
```python
# your code here
```
expect: 12.0
check: to_number("soon") is None
check: to_number(None) is None
solution: def to_number(text):
solution:     if text is None:
solution:         return None
solution:     try:
solution:         return float(text.strip())
solution:     except ValueError:
solution:         return None
solution: print(to_number(" 12 "))
> The `None` guard comes first because `None.strip()` would raise `AttributeError`, not `ValueError`. The `try` turns `"soon"` into `None`.

--- fill #card-6e28e7a4db3b5796
Complete the helper so a non-numeric value counts as missing.
```python
try:
    return float(text.strip())
except ___:
    return None
```
answer: ValueError
> `float("soon")` raises `ValueError`. Catching exactly that, and nothing wider, turns garbage into `None` without hiding real bugs.

--- teach #card-bd476e5c27305c55
### `Retry-After` wins; clamp the rest
If the server sends `Retry-After`, that is an instruction: `reset_in` is that number. Otherwise compute `reset - now`, where `now` is injected as a float unix timestamp (the same idea as the injected `now` in lesson 10.1; never call `time.time()` yourself). A reset time already in the past would go negative, so clamp with `max(0.0, ...)`.
```python
retry_after = _number(_header(headers, "Retry-After"))
if retry_after is not None:
    reset_in = retry_after
else:
    reset_at = _number(_header(headers, "X-RateLimit-Reset"))
    reset_in = max(0.0, reset_at - now) if reset_at is not None else None
```

--- predict #card-d1d02d5bbb665372
What does this print?
```python
reset_at, now = 1000.0, 1200.0
print(max(0.0, reset_at - now))
```
answer: 0.0
> The reset was 200 seconds ago. `max(0.0, -200.0)` clamps it to zero: there is nothing to wait for.

--- teach #card-75d04ebe9d1457e7
### When to actually wait
`wait_seconds` turns the parsed values into a sleep: wait `reset_in` when the server sent `Retry-After`, or when `remaining` is 0 or below. In every other case, including `reset_in` being `None`, return `0.0`.
```python
def wait_seconds(headers, now):
    rl = parse_rate_limit(headers, now)
    told_to_wait = _number(_header(headers, "Retry-After")) is not None
    if told_to_wait or (rl.remaining is not None and rl.remaining <= 0):
        return rl.reset_in or 0.0
    return 0.0
```
`rl.reset_in or 0.0` covers the `None` case in one expression.

--- quiz #card-3181c60eb7dc59d7
Headers are `{"X-RateLimit-Remaining": "0"}` and nothing else. What does `wait_seconds` return?
- [ ] `None`
- [ ] It raises `ValueError`
- [x] `0.0`
> Nothing is left, so we would wait, but there is no reset time, so `reset_in` is `None` and `None or 0.0` gives `0.0`.

--- exercise 11.2 #card-5b13e1213da4589d

--- recap #card-177018a76f735803
- A `namedtuple` is a tuple with named fields; `None` means "not sent".
- Match header names case-insensitively; values are strings with possible whitespace.
- Convert with `try: float(...) except ValueError: None`; garbage means missing.
- `Retry-After` beats your own maths; clamp `reset - now` with `max(0.0, ...)`.
- `now` is injected; never read the clock inside.
