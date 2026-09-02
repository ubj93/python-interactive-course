# Part 11 · HTTP APIs with a fake client

> **What you will be able to do:** write the scripts that talk to Jamf, Kandji,
> Intune or Okta-style REST APIs: build URLs and headers, read JSON, walk pages,
> respect rate limits, retry with backoff, verify webhooks, and push a local
> inventory to a remote one. And write all of it so it can be tested without a
> network. Two to three hours with the exercises.

## Why this part matters

Half of Client Platform Engineering is moving data between systems that expose a
REST API. The Python needed is not exotic; what separates good candidates is that
their API code is **testable**: every function takes the thing that does I/O as a
parameter, so a test can pass a fake that returns canned responses. Every exercise
in this part follows that rule. No test here opens a socket, sleeps, or reads the
clock.

## 1. The real thing: urllib.request

For completeness, this is how a request is made with the standard library. You will
not run it in the exercises, but you must be able to write it on a whiteboard.

```python
import json
import urllib.request
import urllib.error

def get_json(url, token, timeout=30):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "cpe-tools/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:     # urlopen: the I/O
            return resp.status, dict(resp.headers), json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:                                # 4xx / 5xx
        return e.code, dict(e.headers), None
```

Points to say out loud:

- `urlopen` raises `HTTPError` for 4xx/5xx and `URLError` for DNS/connection
  problems. `HTTPError` has `.code` and `.headers`; both are subclasses of `OSError`.
- Sending JSON: `data=json.dumps(payload).encode("utf-8")` plus a
  `Content-Type: application/json` header; `method="POST"` (or `PUT`, `PATCH`,
  `DELETE`) on the `Request`.
- Always pass `timeout`. The default is "forever".
- `requests` is nicer, but it is not in the standard library; interviewers often say
  "no third-party packages" and watch what you do.

## 2. Make the I/O a parameter

The shape that makes everything testable:

```python
def fetch_device(client, serial):
    status, headers, body = client("GET", f"/v1/devices/{serial}")
    if status == 404:
        return None
    return body
```

`client` is *any* callable that takes a method and a path and returns
`(status, headers, body)`. In production it wraps `urlopen`. In tests:

```python
def fake_client(method, path, body=None):
    canned = {"/v1/devices/C02X": (200, {}, {"serial": "C02X", "name": "mbp-1"})}
    return canned.get(path, (404, {}, None))

assert fetch_device(fake_client, "C02X")["name"] == "mbp-1"
assert fetch_device(fake_client, "NOPE") is None
```

A recording fake is even better: it appends every call to a list so the test can
assert *what* was sent, not just what came back.

```python
class FakeClient:
    def __init__(self, responses):
        self.responses, self.calls = list(responses), []
    def __call__(self, method, path, body=None):
        self.calls.append((method, path, body))
        return self.responses.pop(0)
```

The exercises use the simplest signature that fits: `get(url) -> dict` for
pagination, `send() -> response` for retries, an object with `create/update/delete`
for the sync. The idea is always the same: **the function never imports the network,
it receives it.** Same for `sleep`, `rand` and `now`.

## 3. URLs and headers

```python
>>> from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl, quote
>>> urlencode({"limit": 50, "q": "mbp lab"})
'limit=50&q=mbp+lab'
>>> urlencode({"status": ["active", "stale"]}, doseq=True)
'status=active&status=stale'
>>> quote("C02X/G 12", safe="")                     # for path segments
'C02X%2FG%2012'
>>> parts = urlsplit("https://mdm.example.com/v1/devices?limit=2&cursor=old")
>>> parts.path, parse_qsl(parts.query)
('/v1/devices', [('limit', '2'), ('cursor', 'old')])
>>> urlunsplit(parts._replace(query=urlencode([("limit", "2"), ("cursor", "new")])))
'https://mdm.example.com/v1/devices?limit=2&cursor=new'
```

Join base and path with `base.rstrip("/") + "/" + path.lstrip("/")`. (`urljoin` has
surprising rules about absolute paths; most people get it wrong in interviews.)

Headers are a dict. Two rules: never send `"Bearer None"`, so build the
`Authorization` entry conditionally; and HTTP header **names are
case-insensitive**, so when you *read* headers from a response compare with
`.lower()`. Values are strings, sometimes with whitespace.

## 4. Status codes and JSON bodies

| Code | Meaning for a script |
|---|---|
| 200 / 201 / 204 | ok / created / ok with no body (do not call `json.loads` on empty) |
| 400 / 422 | your request is wrong; fix the code, do not retry |
| 401 / 403 | token missing, expired, or lacking scope; do not retry |
| 404 | resource absent; often a normal outcome (`return None`) |
| 409 | conflict: someone else changed it; re-read then decide |
| 429 | throttled: wait `Retry-After` seconds, then retry |
| 5xx | their problem: retry with backoff |

```python
>>> import json
>>> body = json.loads('{"items": [{"serial": "C02X"}], "next_cursor": null}')
>>> body["next_cursor"] is None, body.get("missing", [])
(True, [])
```

`dict.get` with a default is your friend: APIs omit keys they do not have values
for, and a `KeyError` at 3 am is the wrong way to find out.

## 5. Pagination

Two styles you will meet:

**Cursor**: the response carries an opaque token; you send it back as a query
parameter until it comes back `null`.

```python
def fetch_all(get, url, max_pages=100):
    items, seen, next_url = [], set(), url
    for _ in range(max_pages):
        body = get(next_url)
        items.extend(body.get("items") or [])
        cursor = body.get("next_cursor")
        if not cursor:
            return items
        if cursor in seen:                 # a broken API can loop forever; do not let it
            raise PaginationError(cursor)
        seen.add(cursor)
        next_url = with_cursor(url, cursor)
    raise PaginationError("too many pages")
```

**Page/limit**: you send `page=1&limit=100`, then `page=2`, until a page comes back
shorter than `limit` (or empty). Same loop, different termination test.

Both need a **budget** (`max_pages`) and a **loop guard**. Say so before the
interviewer asks "what if the API misbehaves?".

## 6. Rate limits, backoff, jitter

Read the headers: `X-RateLimit-Remaining`, `X-RateLimit-Reset` (a unix timestamp),
and on a 429, `Retry-After` (seconds). If the server tells you how long to wait,
obey it. Otherwise back off exponentially:

```python
def backoff_delay(attempt, base=0.5, cap=30.0, jitter=0.0, rand=random.random):
    delay = min(cap, base * 2 ** attempt)          # 0.5, 1, 2, 4, ... capped
    return delay + delay * jitter * rand()         # jitter spreads out a thundering herd
```

- **Exponential** so a struggling server gets breathing room.
- **Capped** so attempt 20 does not wait a week.
- **Jitter** so a thousand laptops that all got a 429 at 09:00:00 do not all retry
  at 09:00:01. In tests set `jitter=0.0` or inject `rand=lambda: 0.5`.
- **Inject `sleep`**: `sleep=time.sleep` as the default, `sleep=lambda s: None` in
  tests, and assert on the list of delays instead of waiting for them.
- Retry **only** 429 and 5xx (and connection errors). Retrying a 400 with the same
  body is just a slower 400.

Idempotency: a `GET` or `PUT` or `DELETE` can be retried freely. A `POST` that
creates something can double-create on retry; real APIs accept an
`Idempotency-Key` header for this. If you retry POSTs, generate a key once
(`uuid.uuid4()`) and send the same one on every attempt.

## 7. Webhooks and HMAC

When the vendor calls *you*, you must know it is really them. The standard trick is
a shared secret and an HMAC over the body, with a timestamp folded in against
replays:

```python
>>> import hmac, hashlib
>>> sig = hmac.new(b"s3cret", b"1714813200." + b'{"event":"enrolled"}', hashlib.sha256).hexdigest()
>>> hmac.compare_digest(sig, sig)
True
```

- `hmac.new(key, msg, digestmod)`: all bytes; `.hexdigest()` for the header.
- **`hmac.compare_digest`, never `==`.** String equality returns at the first
  differing byte, which leaks timing an attacker can measure.
- Reject timestamps outside a tolerance window (five minutes is common).
- Parse the header defensively: it is attacker-controlled input. Malformed means
  `False`, not an exception.

## 8. Reconciling local and remote state

The capstone pattern: you have the truth (a CSV, a directory, a database) and a
remote copy; compute the difference and apply it as create/update/delete calls.

```python
local_by  = {norm(r["serial"]): r for r in local}
remote_by = {norm(r["serial"]): r for r in remote}
to_create = sorted(set(local_by) - set(remote_by))
to_delete = sorted(set(remote_by) - set(local_by))
both      = sorted(set(local_by) & set(remote_by))
```

- Normalise the key first (serials arrive as `" c02x "` and `"C02X"`).
- Validate everything **before** the first call: duplicates and blanks should fail
  the run, not half of it.
- **Plan, then apply.** Compute the actions as data, then loop over them calling
  the client. `dry_run` becomes "skip the second half", and the planner is a pure
  function you can test with no client at all.
- Send only the fields that changed (`PATCH` semantics); it makes logs readable and
  avoids clobbering fields you do not own.
- Deterministic order (sorted by key) makes logs diffable and tests simple.

## Interview notes for this part

- **Start with the signature.** `def fetch_all(get, url, max_pages=100)`, then say
  "get is injected so I can test with a fake". That sentence is worth more than the
  loop body.
- **Name the failure modes** before writing code: 401, 404, 429, 5xx, a looping
  cursor, a malformed body. Decide which are errors, which are retries, which are
  `None`.
- **Never sleep in a test.** If the interviewer asks how you would test the retry,
  say `sleep=lambda s: None` and assert the recorded delays.
- **`compare_digest`**, case-insensitive header lookup, `Retry-After` beats your own
  maths, plan-then-apply. Each is a small thing that signals experience.
- The trap: building the paging URL from the *previous* page's URL, so cursors pile
  up. Build from the original.

## Exercises

Run `course list 11`, then `course show 11.1`. Edit the file it names, run
`course run 11.1`, repeat until green. Then compare with `course solution 11.1`.

1. `build_headers` · bearer token that is omitted when absent; URL join and `urlencode`
2. `parse_rate_limit` · case-insensitive header lookup, `Retry-After` over reset time
3. `fetch_all_pages` · cursor pagination with a loop guard and a page budget
4. `retry_with_backoff` · exponential backoff, cap, injected `sleep` and `rand`, `RetryError`
5. `verify_webhook_signature` · HMAC-SHA256, `compare_digest`, replay window, defensive parsing
6. `sync_devices` · diff local vs remote into create/update/delete calls on a fake client
