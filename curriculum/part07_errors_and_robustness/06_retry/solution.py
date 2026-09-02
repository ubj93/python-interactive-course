"""Reference solutions for retry."""
import functools
import time
from typing import Any, Callable, Tuple, Type


# Best practice: three nested functions (options -> decorator -> wrapper). The loop
# counts attempts; a bare `raise` on the last one re-raises the same exception object.
# `except exceptions` with a tuple keeps everything else propagating untouched.
def retry(
    times: int = 3,
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    sleep: Callable[[float], Any] = time.sleep,
    delay: float = 1.0,
    backoff: float = 2.0,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    if times < 1:
        raise ValueError("times must be >= 1")

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            wait = delay
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise
                    sleep(wait)
                    wait *= backoff

        return wrapper

    return decorator


# Clever: compute the wait from the attempt number instead of mutating a variable, and
# let the final attempt run outside the loop so the "re-raise" case needs no branch.
def retry_closed_form(
    times: int = 3,
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    sleep: Callable[[float], Any] = time.sleep,
    delay: float = 1.0,
    backoff: float = 2.0,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    if times < 1:
        raise ValueError("times must be >= 1")

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for i in range(times - 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    sleep(delay * backoff ** i)
            return func(*args, **kwargs)      # last attempt: whatever it raises, propagates

        return wrapper

    return decorator
