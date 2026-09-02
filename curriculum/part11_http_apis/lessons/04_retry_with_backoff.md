# Retry with backoff

--- teach
### Exponential backoff, capped
When a server says "not now" (429) or is broken (5xx), wait and try again, waiting longer each time so it gets breathing room. Attempt `k` waits `base * 2 ** k`, and `min(cap, ...)` stops attempt 20 from waiting a week. Jitter adds a random fraction so a thousand laptops that got throttled together do not all retry in the same second.
```python
def backoff_delay(attempt, base=0.5, cap=30.0, jitter=0.0, rand=random.random):
    delay = min(cap, base * 2 ** attempt)
    return delay + delay * jitter * rand()
```
With `jitter=0.0` the result is exact: 0.5, 1, 2, 4, 8, 16, 30, 30, ...

--- code
Write `backoff_delay(attempt, base=0.5, cap=30.0)` returning `min(cap, base * 2 ** attempt)`, then print the delays for attempts 0 to 6 as a list.
```python
# your code here
```
expect: [0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 30.0]
solution: def backoff_delay(attempt, base=0.5, cap=30.0):
solution:     return min(cap, base * 2 ** attempt)
solution: print([backoff_delay(k) for k in range(7)])
> The delay doubles each attempt until `0.5 * 64 = 32.0` would exceed the cap, so attempt 6 gives 30.0.

--- predict
What does this print?
```python
print(min(30.0, 0.5 * 2 ** 3))
```
answer: 4.0
> `2 ** 3` is 8, times 0.5 is 4.0, well under the cap. The cap only bites from attempt 6 onward.

--- fill
Complete the line so the delay never exceeds `cap`.
```python
delay = min(___, base * 2 ** attempt)
```
answer: cap
> `min` picks the smaller of the cap and the doubled delay, so growth stops at the cap.

--- teach
### Which responses to retry
Retry only what might succeed next time: 429, any 500 to 599, and `OSError` from `send` (connection errors are subclasses). Everything else, including 404 and 401, comes back immediately: retrying a 400 with the same body is just a slower 400.
```python
def _retryable(response):
    return response.status == 429 or 500 <= response.status <= 599
```
A response here is any object with `.status` (an int) and `.headers` (a dict).

--- quiz
Which of these responses should be retried?
- [ ] 404
- [ ] 401
- [x] 503
> 503 is the server's problem and may clear up. 404 and 401 will not change on their own; return them at once.

--- teach
### Inject `sleep` and `rand`
A retry loop that calls `time.sleep` makes a test wait for real, and one that calls `random.random` gives a different delay every run. So both come in as parameters, with the real ones as defaults. A test passes a recorder for `sleep` and asserts on the list of delays instead of waiting for them, and `rand=lambda: 0.5` to pin the jitter.
```python
def retry_with_backoff(send, max_attempts=5, ..., sleep=time.sleep, rand=random.random):
    ...
    sleep(delay)          # never time.sleep(delay)

delays = []
retry_with_backoff(send, sleep=delays.append)
assert delays == [0.5, 1.0]
```

--- code
Call `wait_all([0.5, 1.0, 2.0], sleep=...)` with a `sleep` that appends to a list instead of waiting, then print that list.
```python
def wait_all(delays, sleep):
    for d in delays:
        sleep(d)
```
expect: [0.5, 1.0, 2.0]
solution: recorded = []
solution: wait_all([0.5, 1.0, 2.0], sleep=recorded.append)
solution: print(recorded)
> `recorded.append` is a one-argument callable, exactly the shape `sleep` needs. The test finishes instantly and can assert on the delays.

--- predict
What does this print?
```python
delays = []
sleep = delays.append
for k in range(3):
    sleep(min(30.0, 0.5 * 2 ** k))
print(delays)
```
answer: [0.5, 1.0, 2.0]
> `delays.append` is a function that takes one argument, so it stands in for `sleep` and records instead of waiting.

--- teach
### The loop
Check `max_attempts < 1` first and raise `ValueError` before touching `send`. Then loop once per attempt: call `send`, treating `OSError` as a failure with no response; return a non-retryable response at once; if this was the last attempt, stop without sleeping; otherwise sleep a numeric `Retry-After` from the failed response if there is one, else `backoff_delay(attempt, ...)`. After the loop raise `RetryError` with `.response` (the last response, or `None` after an exception) and `.attempts`.
```python
for attempt in range(max_attempts):
    try:
        response = send()
    except OSError:
        last = None
    else:
        if not _retryable(response):
            return response
        last = response
    if attempt + 1 == max_attempts:
        break
    sleep(_retry_after(last) or backoff_delay(attempt, base, cap, jitter, rand))
raise RetryError("gave up", response=last, attempts=max_attempts)
```

--- quiz
`max_attempts=3` and every `send()` returns 503. How many times is `sleep` called?
- [ ] 3
- [x] 2
- [ ] 1
> There is a sleep between attempts, not after the last one. Three attempts have two gaps, then `RetryError` is raised.

--- exercise 11.4

--- recap
- `delay = min(cap, base * 2 ** attempt)`, plus `delay * jitter * rand()`.
- Retry 429, 5xx and `OSError`; return everything else immediately.
- Inject `sleep` and `rand`; tests record delays instead of waiting.
- A numeric `Retry-After` replaces the computed delay; never sleep after the final failure.
- Give up with `RetryError(response=last, attempts=max_attempts)`.
