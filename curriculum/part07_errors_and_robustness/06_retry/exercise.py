"""A retry decorator with an injected sleep.

Calls to the MDM API fail now and then with a transient error. Write a
decorator factory `retry(times=3, exceptions=(Exception,), sleep=time.sleep,
delay=1.0, backoff=2.0)` so that this works:

    @retry(times=3, exceptions=(ConnectionError,), sleep=fake_sleep)
    def fetch_devices():
        ...

Behaviour of the decorated function:
- call the wrapped function; if it returns, return its value immediately
- if it raises an exception that is an instance of one of `exceptions`, and
  attempts remain, call sleep(wait) and try again. The first wait is `delay`;
  each following wait is the previous one multiplied by `backoff`
  (1.0, 2.0, 4.0 ... with the defaults)
- `times` is the total number of attempts, so times=3 means at most 3 calls
  and at most 2 sleeps
- when the last attempt also fails, re-raise that exception (the original
  object, not a new one); do not sleep after the final failure
- an exception that is not in `exceptions` propagates at once: no retry, no
  sleep
- arguments and keyword arguments are passed through to the wrapped function
  unchanged on every attempt
- use functools.wraps so the decorated function keeps its __name__ and __doc__
- times < 1 raises ValueError when retry(...) is called (at decoration time,
  not when the function is used)

`sleep` is a parameter so tests can pass a fake that records the delays instead
of waiting; never call time.sleep directly in the wrapper.

Examples:
    >>> waits = []
    >>> calls = iter([ConnectionError("down"), ConnectionError("down"), "ok"])
    >>> @retry(times=3, exceptions=(ConnectionError,), sleep=waits.append)
    ... def fetch():
    ...     r = next(calls)
    ...     if isinstance(r, Exception):
    ...         raise r
    ...     return r
    >>> fetch()
    'ok'
    >>> waits
    [1.0, 2.0]
"""
import functools
import time
from typing import Any, Callable, Tuple, Type


def retry(
    times: int = 3,
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    sleep: Callable[[float], Any] = time.sleep,
    delay: float = 1.0,
    backoff: float = 2.0,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    raise NotImplementedError("write retry")
