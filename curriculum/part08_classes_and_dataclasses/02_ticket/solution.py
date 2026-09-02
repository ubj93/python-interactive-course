"""Reference solutions for Ticket."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


# Best practice: let the dataclass generate __init__/__repr__/__eq__ and the ordering.
# Declaration order is sort order, so priority and created go first. default_factory
# gives each instance its own list; __post_init__ is the one place validation lives.
@dataclass(order=True)
class Ticket:
    priority: int
    created: datetime
    title: str
    assignee: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not 1 <= self.priority <= 4:
            raise ValueError(f"priority must be 1..4, got {self.priority}")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Ticket":
        return cls(
            priority=int(data["priority"]),
            created=datetime.fromisoformat(data["created"]),
            title=data["title"],
            assignee=data.get("assignee"),
            tags=list(data.get("tags", [])),
        )

    @property
    def is_urgent(self) -> bool:
        return self.priority == 1


# Clever: when the sort order is *not* the declaration order, add a hidden sort key.
# init=False keeps it out of the constructor, repr=False out of the output, and because
# it is the first field the generated comparisons use it alone (the rest is compare=False).
@dataclass(order=True)
class TicketSortKey:
    sort_key: tuple = field(init=False, repr=False)
    title: str = field(compare=False)
    priority: int = field(compare=False)
    created: datetime = field(compare=False)
    assignee: Optional[str] = field(default=None, compare=False)
    tags: List[str] = field(default_factory=list, compare=False)

    def __post_init__(self) -> None:
        if not 1 <= self.priority <= 4:
            raise ValueError(f"priority must be 1..4, got {self.priority}")
        self.sort_key = (self.priority, self.created, self.title)
