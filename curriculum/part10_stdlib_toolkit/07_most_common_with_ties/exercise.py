"""Most installed apps, with ties handled deterministically.

Given the app names collected from every device (one entry per installed copy),
report the top `n`. `Counter.most_common` orders equal counts by first
appearance, so the report changes whenever the inventory arrives in a different
order. Nobody wants a diff in a dashboard because two devices swapped places.

Write `most_common_with_ties(items, n, include_ties=False)` that returns a list
of (item, count) tuples:

- sorted by count descending, then by item ascending (ties alphabetical)
- at most `n` entries when include_ties is False
- when include_ties is True, every item whose count equals the count of the
  n-th entry is also included, so the list may be longer than n
- n larger than the number of distinct items returns all of them
- n <= 0, or an empty `items`, returns []
- `items` is any iterable of strings (list, generator, ...)

Examples:
    >>> apps = ["Slack", "Zoom", "Slack", "Chrome", "Zoom", "Firefox"]
    >>> most_common_with_ties(apps, 2)
    [('Slack', 2), ('Zoom', 2)]
    >>> most_common_with_ties(apps, 3)
    [('Slack', 2), ('Zoom', 2), ('Chrome', 1)]
    >>> most_common_with_ties(apps, 3, include_ties=True)
    [('Slack', 2), ('Zoom', 2), ('Chrome', 1), ('Firefox', 1)]
"""
from collections import Counter
from typing import Iterable, List, Tuple


def most_common_with_ties(items: Iterable[str], n: int, include_ties: bool = False) -> List[Tuple[str, int]]:
    raise NotImplementedError("write most_common_with_ties")
