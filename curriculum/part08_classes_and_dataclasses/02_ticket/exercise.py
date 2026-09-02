"""A help-desk ticket as a dataclass.

The service desk exports tickets as dicts and the triage script sorts them by
hand with a pile of lambdas. Replace that with a dataclass whose ordering *is*
the triage order.

Write `Ticket` as a `@dataclass(order=True)` with these fields, in this order:

    priority: int                  1 is most urgent, 4 least
    created: datetime
    title: str
    assignee: Optional[str] = None
    tags: List[str]                defaults to a new empty list per instance

Behaviour:
- Ordering comes from `order=True`: dataclasses compare fields as a tuple in
  declaration order, so tickets sort by priority, then by created time (oldest
  first), then by title. Do not write __lt__ yourself.
- `tags` must use `field(default_factory=list)`; two tickets must never share
  the same list object.
- Validate in `__post_init__`: a priority outside 1..4 raises ValueError.
- `Ticket.from_dict(data)` is a classmethod that builds a ticket from a dict with
  the same keys. `created` arrives as an ISO 8601 string such as
  "2024-05-01T09:30:00" (use `datetime.fromisoformat`). `assignee` and `tags`
  may be missing and then take their defaults. Copy `tags` into a new list.
- `is_urgent` is a property: True when priority == 1.

Examples:
    >>> t = Ticket(2, datetime(2024, 5, 1, 9, 0), "Wi-Fi drops")
    >>> t.assignee is None, t.tags
    (True, [])
    >>> Ticket(1, datetime(2024, 5, 1, 9, 30), "Laptop stolen") < t
    True
    >>> Ticket.from_dict({"priority": 1, "created": "2024-05-01T09:30:00", "title": "Laptop stolen"}).is_urgent
    True
    >>> Ticket(5, datetime(2024, 5, 1), "bad")
    Traceback (most recent call last):
    ValueError: priority must be 1..4, got 5
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


class Ticket:
    # TODO: replace this placeholder with a @dataclass(order=True) declaring the
    # fields from the docstring, then add __post_init__, from_dict and is_urgent.

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError("write Ticket as a dataclass")

    def __post_init__(self) -> None:
        raise NotImplementedError("write Ticket.__post_init__")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Ticket":
        raise NotImplementedError("write Ticket.from_dict")

    @property
    def is_urgent(self) -> bool:
        raise NotImplementedError("write Ticket.is_urgent")
