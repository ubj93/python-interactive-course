"""Top k by a key.

"Which ten devices are closest to running out of disk?" The fleet is fifty
thousand machines and the answer is ten. Sorting everything works, but a heap
does the job while holding only ten items. Write `top_k(items, k, key)`.

- `items` is any iterable (list, generator, ...). Do not modify it, and do not
  assume it can be iterated twice or indexed.
- `key` is a function mapping an item to something comparable (a number, a
  string, a tuple). The result is ordered by that key, largest first.
- Return a list of at most `k` items (the items themselves, not their keys).
- `k <= 0` returns an empty list. `k` larger than the number of items returns
  every item, still ordered largest first.
- Ties keep their original input order, exactly like
  `sorted(items, key=key, reverse=True)[:k]`; `heapq.nlargest` guarantees the
  same.

Use `heapq.nlargest`. In the solution comments, and out loud in an interview,
say when you would prefer it over a full sort: O(n log k) memory and time for
small k on a large or streaming input, versus the simplicity of `sorted` when
k is close to n.

Examples:
    >>> usage = [("mbp-j-doe", 0.91), ("win-lab-01", 0.42), ("mbp-a-lee", 0.97), ("srv-01", 0.91)]
    >>> top_k(usage, 2, key=lambda d: d[1])
    [('mbp-a-lee', 0.97), ('mbp-j-doe', 0.91)]
    >>> top_k(usage, 10, key=lambda d: d[1])
    [('mbp-a-lee', 0.97), ('mbp-j-doe', 0.91), ('srv-01', 0.91), ('win-lab-01', 0.42)]
    >>> top_k(usage, 0, key=lambda d: d[1])
    []
"""
import heapq
from typing import Any, Callable, Iterable, List, TypeVar

T = TypeVar("T")


def top_k(items: Iterable[T], k: int, key: Callable[[T], Any]) -> List[T]:
    raise NotImplementedError("write top_k")
