# Verifying a webhook

--- teach
### HMAC: a hash that needs a secret
When the vendor calls *your* endpoint, anyone else can too. So they sign each request: an HMAC is a hash of the message computed with a shared secret, and only someone holding the secret can produce it. `hmac.new(key, message, hashlib.sha256).hexdigest()` gives 64 hex characters. Everything must be bytes; encode `str` inputs with UTF-8. The message here is the timestamp, a dot, then the body, so the timestamp is covered by the signature too.
```python
import hashlib, hmac

def sign_payload(secret, body, timestamp):
    message = f"{timestamp}.".encode("utf-8") + body
    return hmac.new(secret, message, hashlib.sha256).hexdigest()
```
A helper `_bytes(value)` that encodes only when given a `str` keeps this tidy.

--- code
Write `sign(secret, body, t)` returning the hex HMAC-SHA256 of `f"{t}."` (as bytes) plus `body` under `secret`, all bytes. Then print the first 8 characters of `sign(b"s3cret", b"{}", 1714813200)`.
```python
import hashlib, hmac
```
expect: 114b4958
check: sign(b"s3cret", b"{}", 1714813200) == hmac.new(b"s3cret", b"1714813200.{}", hashlib.sha256).hexdigest()
solution: def sign(secret, body, t):
solution:     return hmac.new(secret, f"{t}.".encode("utf-8") + body, hashlib.sha256).hexdigest()
solution: print(sign(b"s3cret", b"{}", 1714813200)[:8])
> The key is the secret and the message is `b"1714813200.{}"`. Change one byte of either and every character of the digest changes.

--- fill
Complete the line so the timestamp prefix is bytes, ready to join with the body.
```python
message = f"{timestamp}.".___("utf-8") + body
```
answer: encode
> `str.encode("utf-8")` turns text into bytes. Adding `str` to `bytes` raises `TypeError`, so both sides must be bytes.

--- predict
What does this print?
```python
import hashlib, hmac
print(len(hmac.new(b"k", b"m", hashlib.sha256).hexdigest()))
```
answer: 64
> SHA-256 produces 32 bytes, and each byte becomes two hex characters. Any other length means the header is not a real signature.

--- teach
### Parse the header defensively
The header looks like `t=1714813200,v1=5f1c...`, and `v1` may repeat while the vendor rotates secrets. Split on commas, strip each pair, and `partition("=")` into key and value; a pair with no `=` is skipped. `t` must be an `int`; a bad one means the whole header is invalid. This is attacker-controlled input, so malformed means `False`, never an exception.
```python
timestamp, sigs = None, []
for pair in value.split(","):
    key, sep, val = pair.strip().partition("=")
    if key.strip() == "t":
        timestamp = int(val.strip())        # wrap in try/except ValueError
    elif key.strip() == "v1":
        sigs.append(val.strip())
```
Look the header up case-insensitively, as in lesson 11.2.

--- code
Parse `value` into `t` (an `int`) and `sigs` (a list of every `v1` value), tolerating the spaces.
```python
value = " t=1714813200 , v1=aaa, v1=bbb "
```
check: t == 1714813200
check: sigs == ["aaa", "bbb"]
solution: t, sigs = None, []
solution: for pair in value.split(","):
solution:     key, sep, val = pair.strip().partition("=")
solution:     if key.strip() == "t":
solution:         t = int(val.strip())
solution:     elif key.strip() == "v1":
solution:         sigs.append(val.strip())
> Split on commas, strip each pair, `partition` at the first `=`. Collecting `v1` into a list keeps both values; a dict would have kept only the last.

--- predict
What does this print?
```python
key, sep, val = " v1=abc ".strip().partition("=")
print(key, sep, val)
```
answer: v1 = abc
> `partition` splits at the first `=` into three parts: before, the separator itself, after. Stripping first removes the padding.

--- teach
### Reject replays with a time window
A valid request captured today could be replayed next week. Because `t` is inside the signed message, the attacker cannot change it, so compare it with `now`: accept only when `abs(now - t) <= tolerance`. `now` is injected, as always, so the test can sit exactly on the boundary. Do this cheap check before computing any HMAC.
```python
if abs(now - timestamp) > tolerance:
    return False
```

--- quiz
The header has `t=1000`, `now=1301` and `tolerance=300`. Is the request accepted?
- [ ] Yes, 301 rounds down to 300
- [x] No, 301 seconds is outside the window
- [ ] Yes, only the past is checked
> `abs(1301 - 1000)` is 301, which is greater than 300. The window is inclusive at exactly 300 and closed on both sides.

--- teach
### Compare with `compare_digest`, never `==`
`==` on strings stops at the first differing character, so a wrong signature that shares a longer prefix takes slightly longer to reject. An attacker can measure that and guess the signature byte by byte. `hmac.compare_digest(a, b)` takes the same time whatever the inputs. With several `v1` values, any match is enough.
```python
expected = sign_payload(secret, body, timestamp)
return any(hmac.compare_digest(expected, sig) for sig in sigs)
```

--- quiz
Why use `hmac.compare_digest(expected, sig)` instead of `expected == sig`?
- [ ] `==` does not work on hex strings
- [x] It takes constant time, so timing does not reveal how much of the signature was right
- [ ] It ignores case and whitespace
> Equality short-circuits at the first mismatch; the time it takes leaks information. `compare_digest` compares every character regardless.

--- exercise 11.5

--- recap
- `hmac.new(secret, b"<t>." + body, hashlib.sha256).hexdigest()`; everything bytes.
- Parse `t=...,v1=...` with `split(",")` and `partition("=")`; malformed means `False`.
- Reject when `abs(now - t) > tolerance`; `now` is injected.
- `hmac.compare_digest`, never `==`; any matching `v1` is enough.
