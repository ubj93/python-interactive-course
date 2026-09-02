"""Reference solutions for backoff_delay / retry_with_backoff."""
import random
import time
from typing import Any, Callable, Optional


class RetryError(Exception):
    def __init__(self, message: str, response: Optional[Any] = None, attempts: int = 0):
        super().__init__(message)
        self.response = response
        self.attempts = attempts


# Pure function: no clock, no randomness of its own. Everything non-deterministic comes in
# through `rand`, so a test can pin it.
def backoff_delay(
    attempt: int,
    base: float = 0.5,
    cap: float = 30.0,
    jitter: float = 0.0,
    rand: Callable[[], float] = random.random,
) -> float:
    delay = min(cap, base * 2 ** attempt)
    return delay + delay * jitter * rand()


def _retry_after(response: Any) -> Optional[float]:
    value = (getattr(response, "headers", None) or {}).get("Retry-After")
    try:
        return float(value) if value is not None else None
    except ValueError:
        return None


def _retryable(response: Any) -> bool:
    return response.status == 429 or 500 <= response.status <= 599


# Best practice: one loop over attempts; each iteration either returns, or records the
# failure and sleeps. The sleep sits at the bottom, guarded by "is there another attempt",
# so the last failure never sleeps.
def retry_with_backoff(
    send: Callable[[], Any],
    max_attempts: int = 5,
    base: float = 0.5,
    cap: float = 30.0,
    jitter: float = 0.0,
    sleep: Callable[[float], None] = time.sleep,
    rand: Callable[[], float] = random.random,
) -> Any:
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")
    last_response: Optional[Any] = None
    last_error: Optional[BaseException] = None
    for attempt in range(max_attempts):
        try:
            response = send()
        except OSError as exc:
            last_response, last_error = None, exc
        else:
            if not _retryable(response):
                return response
            last_response, last_error = response, None
        if attempt + 1 == max_attempts:
            break
        delay = _retry_after(last_response) if last_response is not None else None
        if delay is None:
            delay = backoff_delay(attempt, base, cap, jitter, rand)
        sleep(delay)
    err = RetryError(f"gave up after {max_attempts} attempts", response=last_response, attempts=max_attempts)
    if last_error is not None:
        raise err from last_error
    raise err


# Clever: a decorator factory turns the same loop into something you can stick on any
# function that returns a response. Same injection points, so still testable.
def with_retries(max_attempts: int = 5, sleep: Callable[[float], None] = time.sleep, **kw):
    def decorate(fn):
        def wrapper(*args, **kwargs):
            return retry_with_backoff(lambda: fn(*args, **kwargs), max_attempts=max_attempts, sleep=sleep, **kw)
        return wrapper
    return decorate
