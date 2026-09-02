"""Reference solutions for batched."""
from itertools import islice
from typing import Iterable, Iterator, Tuple, TypeVar

T = TypeVar("T")


# Best practice: validate eagerly in a plain function, then hand off to a generator.
# islice(it, n) on a shared iterator pulls at most n items per call; tuple() of an empty
# slice is (), which is the "input exhausted" signal. This is the shape of 3.12's
# itertools.batched.
def batched(iterable: Iterable[T], n: int) -> Iterator[Tuple[T, ...]]:
    if n < 1:
        raise ValueError("n must be >= 1")
    return _batches(iter(iterable), n)


def _batches(it: Iterator[T], n: int) -> Iterator[Tuple[T, ...]]:
    while True:
        batch = tuple(islice(it, n))
        if not batch:
            return
        yield batch


# Clever: the two-argument form of iter() calls a function until it returns the sentinel.
# Here the function is "take the next n as a tuple" and the sentinel is the empty tuple.
# No explicit loop, and it is still lazy because iter() only calls on demand.
def batched_iter_sentinel(iterable: Iterable[T], n: int) -> Iterator[Tuple[T, ...]]:
    if n < 1:
        raise ValueError("n must be >= 1")
    it = iter(iterable)
    return iter(lambda: tuple(islice(it, n)), ())
