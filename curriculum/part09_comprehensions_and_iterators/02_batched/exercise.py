"""Batch an iterable into fixed-size tuples.

The MDM API accepts at most 50 serials per request, and the serial list may
come from a file, a database cursor or another generator, so we cannot index
it or know its length. Write `batched(iterable, n)` that yields tuples of `n`
items, the last one shorter if the input runs out.

Rules:
- Works on any iterable, including one-shot iterators and infinite ones, and
  pulls items only as batches are requested (lazy). Do not call `list()` or
  `len()` on the input.
- Each batch is a tuple. The last batch may have fewer than `n` items; an
  empty batch is never yielded, and an empty input yields nothing.
- `n < 1` raises ValueError at call time, before any iteration happens:
  `batched([], 0)` must raise on its own, without `next()` or `list()`.
  A generator function delays its body, so validate in a normal function and
  return the generator from there.

Examples:
    >>> list(batched(["a", "b", "c", "d", "e"], 2))
    [('a', 'b'), ('c', 'd'), ('e',)]
    >>> list(batched(range(4), 2))
    [(0, 1), (2, 3)]
    >>> list(batched([], 3))
    []
    >>> from itertools import count, islice
    >>> list(islice(batched(count(1), 3), 2))
    [(1, 2, 3), (4, 5, 6)]
    >>> batched([1], 0)
    Traceback (most recent call last):
    ValueError: n must be >= 1
"""
from itertools import islice
from typing import Iterable, Iterator, Tuple, TypeVar

T = TypeVar("T")


def batched(iterable: Iterable[T], n: int) -> Iterator[Tuple[T, ...]]:
    raise NotImplementedError("write batched")
