# Headers and URLs

--- teach
### Headers are a dict, built fresh each call
An HTTP request carries headers: a dict of name to value. Start from a literal inside the function so every call gets a new dict; a shared module-level dict would leak one caller's changes into the next. Add `Authorization` only when there is a real token, because `"Bearer None"` is a bug servers reject with a confusing 401.
```python
def build_headers(token, extra=None):
    headers = {"Accept": "application/json", "User-Agent": "cpe-tools/1.0"}
    token = (token or "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    ...
```
`(token or "").strip()` turns `None`, `""` and `"   "` into the same empty string, which is falsy.

--- code
Write `build_auth(token)` that returns `{}` for a `None` or blank token and `{"Authorization": "Bearer <token>"}` with the stripped token otherwise. Then print `build_auth("  abc ")`.
```python
# your code here
```
expect: {'Authorization': 'Bearer abc'}
check: build_auth(None) == {}
check: build_auth("   ") == {}
solution: def build_auth(token):
solution:     token = (token or "").strip()
solution:     return {"Authorization": f"Bearer {token}"} if token else {}
solution: print(build_auth("  abc "))
> `(token or "").strip()` folds `None`, `""` and `"   "` into one empty string, and the conditional expression sends nothing rather than `"Bearer None"`.

--- predict
What does this print?
```python
token = "   "
print(bool((token or "").strip()))
```
answer: False
> `"   "` is truthy, so `or` keeps it, but `strip()` makes it `""`, and an empty string is `False`.

--- teach
### Merge `extra` last, into your own dict
`dict.update(other)` copies every key from `other` into the dict it is called on, overwriting existing keys. Call it on **your** new dict so the caller's dict is untouched and their values win over the defaults. `extra` may be `None`, so guard it.
```python
    if extra:
        headers.update(extra)
    return headers
```

--- quiz
Which line lets `extra` override the defaults without changing the caller's dict?
- [x] `headers.update(extra)` where `headers` is the new dict
- [ ] `extra.update(headers)`
- [ ] `headers = extra`
> `update` writes into the dict on the left. Writing into `extra` would change the caller's object; assigning `headers = extra` would return the caller's dict itself.

--- teach
### Join base and path with exactly one slash
Callers write `base` with or without a trailing slash and `path` with or without a leading one. `rstrip("/")` and `lstrip("/")` remove whatever is there, and you put one `/` back. That beats `urljoin`, whose rules for absolute paths surprise people in interviews.
```python
url = base.rstrip("/") + "/" + path.lstrip("/")
```

--- predict
What does this print?
```python
base = "https://x.io/api/"
path = "/v1/devices"
print(base.rstrip("/") + "/" + path.lstrip("/"))
```
answer: https://x.io/api/v1/devices
> Both stray slashes are stripped and a single one is added back, so the join is the same whatever the caller wrote.

--- teach
### Query strings with `urlencode`
`urllib.parse.urlencode(params, doseq=True)` turns a dict into `key=value&key=value`, percent-encoding spaces and special characters; with `doseq=True` a list value becomes the key repeated once per item. Drop `None` values first with a dict comprehension, and add the `?` only when something is left.
```python
>>> from urllib.parse import urlencode
>>> urlencode({"limit": 50, "q": "mbp lab"}, doseq=True)
'limit=50&q=mbp+lab'
>>> urlencode({"status": ["active", "stale"]}, doseq=True)
'status=active&status=stale'
```
Never hand-roll the encoding; `urlencode` knows the rules.

--- code
Set `query` to the encoded form of `params` with `None` values dropped and the list value repeated.
```python
from urllib.parse import urlencode
params = {"limit": 50, "cursor": None, "status": ["active", "stale"]}
```
check: query == "limit=50&status=active&status=stale"
solution: clean = {k: v for k, v in params.items() if v is not None}
solution: query = urlencode(clean, doseq=True)
> The comprehension removes `cursor`; `doseq=True` turns the list into two `status=` pairs. Without it you would get `status=%5B%27active%27...`, the encoded text of the list.

--- predict
What does this print?
```python
from urllib.parse import urlencode
print(urlencode({"limit": 50, "q": "mbp lab", "status": ["a", "b"]}, doseq=True))
```
answer: limit=50&q=mbp+lab&status=a&status=b
> Keys keep dict order, the space becomes `+`, and `doseq=True` repeats `status` for each list item.

--- fill
Complete the comprehension that drops parameters whose value is `None`.
```python
clean = {k: v for k, v in (params or {}).items() if v ___ None}
if clean:
    url += "?" + urlencode(clean, doseq=True)
```
answer: is not
> `is not None` keeps every real value, including `0` and `""`. `(params or {})` handles a `None` params argument.

--- exercise 11.1

--- recap
- Build the headers dict fresh in the function; add `Authorization` only for a non-blank token.
- `headers.update(extra)` merges the caller's overrides into your dict, not theirs.
- `base.rstrip("/") + "/" + path.lstrip("/")` joins with exactly one slash.
- `urlencode(params, doseq=True)` encodes values and repeats list keys; drop `None` first.
