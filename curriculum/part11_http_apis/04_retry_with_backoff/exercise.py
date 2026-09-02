"""Retry a request with exponential backoff.

Cloud APIs answer 429 (throttled) and 5xx (their problem) routinely; a fleet
script that gives up on the first one wakes someone at night. Write two
functions.

`backoff_delay(attempt, base=0.5, cap=30.0, jitter=0.0, rand=random.random)`
returns the seconds to wait before retry number `attempt` (0-based):

- delay = min(cap, base * 2 ** attempt)
- then add jitter: delay + delay * jitter * rand(), where rand() returns a float
  in [0, 1). With jitter=0.0 the result is exact, which is how the tests call it;
  with jitter=1.0 and rand=lambda: 0.5 the delay is 1.5 times the base delay.

`retry_with_backoff(send, max_attempts=5, base=0.5, cap=30.0, jitter=0.0,
sleep=time.sleep, rand=random.random)` calls `send()` (no arguments) until it
gets a non-retryable response and returns that response:

- a response has `.status` (int) and `.headers` (dict)
- retryable: status 429, any status 500-599, or `send` raising OSError
  (ConnectionError and friends are subclasses of OSError)
- everything else, including 404 and 401, is returned immediately without
  sleeping
- before each retry call `sleep(seconds)` once. If the failed response carried a
  numeric Retry-After header use that many seconds; otherwise
  backoff_delay(k, ...) where k counts the retries so far (first retry uses k=0,
  so it sleeps `base`)
- after `max_attempts` calls to send with no success raise RetryError (defined
  below) with `.response` set to the last response (None when the last failure
  was an exception) and `.attempts` set to max_attempts. Do not sleep after the
  final failure.
- max_attempts < 1 raises ValueError before calling send
- never call time.sleep or random directly; use the injected `sleep` and `rand`

Examples:
    >>> backoff_delay(0), backoff_delay(3), backoff_delay(10, cap=30.0)
    (0.5, 4.0, 30.0)
    >>> responses = iter([Resp(503), Resp(200)])   # see the tests for a fake `send`
    >>> retry_with_backoff(lambda: next(responses), sleep=lambda s: None).status
    200
"""
import random
import time
from typing import Any, Callable, Optional


class RetryError(Exception):
    def __init__(self, message: str, response: Optional[Any] = None, attempts: int = 0):
        super().__init__(message)
        self.response = response
        self.attempts = attempts


def backoff_delay(
    attempt: int,
    base: float = 0.5,
    cap: float = 30.0,
    jitter: float = 0.0,
    rand: Callable[[], float] = random.random,
) -> float:
    raise NotImplementedError("write backoff_delay")


def retry_with_backoff(
    send: Callable[[], Any],
    max_attempts: int = 5,
    base: float = 0.5,
    cap: float = 30.0,
    jitter: float = 0.0,
    sleep: Callable[[float], None] = time.sleep,
    rand: Callable[[], float] = random.random,
) -> Any:
    raise NotImplementedError("write retry_with_backoff")
