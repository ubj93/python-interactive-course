# Walking pages with a cursor

--- teach
### Cursor pagination, and an injected `get`
An API that lists thousands of devices sends them a page at a time. Each response holds `items` and a `next_cursor`, an opaque token you send back as `cursor=...` to get the next page; the last page has `next_cursor` set to `null` or missing. The function does not import the network: it takes `get`, a callable `get(url) -> dict`. Tests pass a fake that serves canned bodies by URL and records every call.
```python
def make_get(pages):
    calls = []
    def get(url):
        calls.append(url)
        return pages[url]
    get.calls = calls
    return get
```
Production passes a wrapper around `urllib.request.urlopen`; the loop never knows the difference.

--- quiz
In the tests, what is `get`?
- [ ] A real HTTP call with a short timeout
- [x] A function returning canned dicts keyed by URL and recording the URLs asked for
- [ ] A string naming the endpoint
> The fake lets the test assert both what came back and exactly which URLs were requested, with no network.

--- teach
### The loop
Extend the result with each page's items, read the cursor, and stop when it is falsy (`None`, `""` or missing). `body.get("items") or []` handles a page without `items`. A `for` over `range(max_pages)` gives the loop a budget; finishing the loop means the budget ran out.
```python
items, next_url = [], url
for _ in range(max_pages):
    body = get(next_url)
    items.extend(body.get("items") or [])
    cursor = body.get("next_cursor")
    if not cursor:
        return items
    next_url = _with_cursor(url, cursor)
raise PaginationError(f"more than {max_pages} pages")
```
Do not catch exceptions from `get`; a failed request is the caller's problem.

--- code
Walk the pages starting at `url` with `get`, following `next_cursor` until it is falsy, and set `items` to every item in order. This fake takes the bare cursor as the next URL, so no URL building is needed yet.
```python
pages = {"start": {"items": [1, 2], "next_cursor": "c2"}, "c2": {"items": [3], "next_cursor": None}}
get = pages.__getitem__
url = "start"
```
check: items == [1, 2, 3]
solution: items, next_url = [], url
solution: while True:
solution:     body = get(next_url)
solution:     items.extend(body.get("items") or [])
solution:     next_url = body.get("next_cursor")
solution:     if not next_url:
solution:         break
> Two requests: `"start"` gives `[1, 2]` and a cursor, `"c2"` gives `[3]` and `None`, which ends the loop. The exercise adds the URL building and the two guards.

--- predict
What does this print?
```python
body = {"next_cursor": None}
print(body.get("items") or [], bool(body.get("next_cursor")))
```
answer: [] False
> A missing `items` key gives `None`, and `None or []` is `[]`. A `None` cursor is falsy, so the walk ends.

--- teach
### Build the next URL from the original
The trap is appending `&cursor=` to the previous page's URL: cursors pile up. Always start from the original `url`. `urlsplit` breaks it into parts, `parse_qsl` gives the query as an ordered list of pairs, you drop any existing `cursor`, append the new one last, and `urlunsplit` puts it back together. `parts._replace(query=...)` returns a copy with one field changed.
```python
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

def _with_cursor(url, cursor):
    parts = urlsplit(url)
    query = [(k, v) for k, v in parse_qsl(parts.query) if k != "cursor"]
    query.append(("cursor", cursor))
    return urlunsplit(parts._replace(query=urlencode(query)))
```

--- code
Write `with_cursor(url, cursor)` that drops any existing `cursor` parameter, keeps the others in order and appends the new cursor last. Then print `with_cursor(url, "new")`.
```python
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
url = "https://x.io/v1/devices?cursor=old&limit=2"
```
expect: https://x.io/v1/devices?limit=2&cursor=new
solution: def with_cursor(url, cursor):
solution:     parts = urlsplit(url)
solution:     query = [(k, v) for k, v in parse_qsl(parts.query) if k != "cursor"]
solution:     query.append(("cursor", cursor))
solution:     return urlunsplit(parts._replace(query=urlencode(query)))
solution: print(with_cursor(url, "new"))
> Split, filter the pairs, append, re-encode, reassemble. Because it always starts from the original `url`, calling it for page after page never stacks cursors.

--- predict
What does this print?
```python
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
parts = urlsplit("https://x.io/v1/devices?cursor=old&limit=2")
query = [(k, v) for k, v in parse_qsl(parts.query) if k != "cursor"]
query.append(("cursor", "new"))
print(urlunsplit(parts._replace(query=urlencode(query))))
```
answer: https://x.io/v1/devices?limit=2&cursor=new
> The stale `cursor=old` is filtered out, `limit=2` keeps its place, and the new cursor goes last.

--- teach
### Two guards against a misbehaving API
A broken API can hand back a cursor you already used, and a naive loop would run forever. Keep a `set` of cursors seen and raise `PaginationError` on a repeat. The `max_pages` budget is the second guard: needing more requests than allowed is an error, not a longer wait. Say both before the interviewer asks "what if the API misbehaves?".
```python
seen = set()
...
if cursor in seen:
    raise PaginationError(f"cursor {cursor!r} repeated")
seen.add(cursor)
```

--- fill
Complete the loop guard.
```python
if cursor in ___:
    raise PaginationError(f"cursor {cursor!r} repeated")
seen.add(cursor)
```
answer: seen
> Checking the set before adding to it catches the second appearance of any cursor, which is when the API has started looping.

--- exercise 11.3

--- recap
- `get(url) -> dict` is injected; tests pass a fake that serves canned pages and records calls.
- Extend items, read `next_cursor`, stop when it is falsy; a page without `items` adds nothing.
- Build every next URL from the original with `urlsplit`, `parse_qsl`, `urlencode`, `urlunsplit`.
- A `seen` set catches loops; `max_pages` caps the walk; both raise `PaginationError`.
