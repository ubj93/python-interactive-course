# Dataclasses

--- teach #card-de4c8fd4a2715256
### `@dataclass` writes the boring methods for you
Most classes are a record with a few methods. Put `@dataclass` above the class, list the fields with type annotations, and Python generates `__init__`, `__repr__` and `__eq__` from them, in the order you wrote them.
```python
from dataclasses import dataclass

@dataclass
class Ticket:
    priority: int
    title: str

>>> Ticket(2, "Wi-Fi drops")
Ticket(priority=2, title='Wi-Fi drops')
```
No `self.priority = priority` lines. The annotation `priority: int` is what makes it a field.

--- code #card-34d05762631051a3
Declare a dataclass `Ticket` with fields `priority: int` and `title: str`, then print `Ticket(2, "Wi-Fi drops")`.
```python
from dataclasses import dataclass
```
expect: Ticket(priority=2, title='Wi-Fi drops')
check: Ticket(2, "a") == Ticket(2, "a")
solution: @dataclass
solution: class Ticket:
solution:     priority: int
solution:     title: str
solution: print(Ticket(2, "Wi-Fi drops"))
> Two annotated lines are the whole class. The decorator generates the constructor, the repr you see printed, and the field-by-field `__eq__` that makes the check true.

--- teach #card-aaa1373ffe4155ef
### Defaults, and the `default_factory` rule
A field can have a default, but fields without defaults must come first, like function parameters. For a list default never write `= []`: that one list would be shared by every ticket. Use `field(default_factory=list)` to get a fresh list per instance. `Optional[str] = None` is the usual default for a value that may be missing.
```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Ticket:
    priority: int
    title: str
    assignee: Optional[str] = None
    tags: List[str] = field(default_factory=list)
```

--- quiz #card-d67ed13bb89b5878
Why does `tags: List[str] = []` fail in a dataclass?
- [ ] Lists cannot be type-annotated
- [x] One list object would be shared by every instance
- [ ] Defaults must be strings or numbers
> A default is created once, when the class is defined. `field(default_factory=list)` calls `list()` for each new instance instead, so `a.tags.append(...)` never shows up in `b.tags`. Python rejects the bare `[]` to save you from this bug.

--- teach #card-924c693689a35c3e
### `order=True`: sort by the fields, in order
`@dataclass(order=True)` generates `<`, `<=`, `>` and `>=`. They compare instances as if each were a tuple of its fields, in declaration order. So put the field you want to sort by first, the tie-breaker second, and `sorted()` needs no key at all.
```python
@dataclass(order=True)
class Ticket:
    priority: int
    created: datetime
    title: str
```
Tuples compare element by element: the first difference decides.

--- predict #card-6afef208acb85c72
What does this print?
```python
print((1, "zebra") < (2, "apple"))
```
answer: True
> The first elements differ, `1 < 2`, so the comparison is decided there. The strings are never looked at. That is exactly how an ordered dataclass compares priorities before anything else.

--- teach #card-b98c0e7fdab45a8e
### `__post_init__`: validate after the generated `__init__`
You do not write `__init__`, so where do checks go? `__post_init__(self)` runs right after the generated `__init__` has stored the fields. Raise there if a value is out of range.
```python
def __post_init__(self):
    if not 1 <= self.priority <= 4:
        raise ValueError(f"priority must be 1..4, got {self.priority}")
```

--- fill #card-0291928646875109
Complete the method name so the check runs on every new ticket.
```python
def ___(self):
    if not 1 <= self.priority <= 4:
        raise ValueError(f"priority must be 1..4, got {self.priority}")
```
answer: __post_init__
> The dataclass machinery calls `__post_init__` automatically at the end of the generated `__init__`. Any other name is just a method nobody calls.

--- teach #card-4e068c6caaed59ba
### `@classmethod` builders and `@property` readers
A **classmethod** gets the class as `cls` instead of an instance. It is the standard way to write an alternative constructor: parse the input, then call `cls(...)`. `datetime.fromisoformat` turns `"2024-05-01T09:30:00"` into a `datetime`; `data.get("tags", [])` handles a missing key; `list(...)` copies so the caller's list is not shared.
A **property** is a method that reads like an attribute: `t.is_urgent`, no parentheses.
```python
@classmethod
def from_dict(cls, data):
    return cls(data["priority"], datetime.fromisoformat(data["created"]),
               data["title"], data.get("assignee"), list(data.get("tags", [])))

@property
def is_urgent(self):
    return self.priority == 1
```

--- code #card-019b3fee49845a47
Set `created` to the `datetime` parsed from `data["created"]`, and `tags` to a copy of `data["tags"]` that falls back to an empty list when the key is missing.
```python
from datetime import datetime
data = {"priority": 1, "created": "2024-05-01T09:30:00", "title": "Laptop stolen"}
```
check: created == datetime(2024, 5, 1, 9, 30)
check: tags == [] and tags is not data.get("tags")
solution: created = datetime.fromisoformat(data["created"])
solution: tags = list(data.get("tags", []))
> `fromisoformat` parses the ISO string in one call. `data.get("tags", [])` returns the default when the key is absent, and `list(...)` makes a copy so the caller's list is never shared with the ticket.

--- exercise 8.2 #card-5b7882171fe759f7

--- recap #card-b9575c20dbb75c12
- `@dataclass` generates `__init__`, `__repr__`, `__eq__` from annotated fields.
- Fields without defaults come first; list defaults use `field(default_factory=list)`.
- `order=True` compares fields as a tuple in declaration order.
- `__post_init__` is where validation goes.
- `@classmethod` + `cls(...)` for alternative constructors; `@property` for computed reads.
