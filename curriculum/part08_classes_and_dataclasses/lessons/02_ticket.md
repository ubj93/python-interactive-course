# Dataclasses

--- teach
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

--- predict
What does this print?
```python
print(Ticket(2, "a") == Ticket(2, "a"))
```
answer: True
> The generated `__eq__` compares field by field. Two tickets with the same values are equal, even though they are different objects.

--- teach
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

--- quiz
Why does `tags: List[str] = []` fail in a dataclass?
- [ ] Lists cannot be type-annotated
- [x] One list object would be shared by every instance
- [ ] Defaults must be strings or numbers
> A default is created once, when the class is defined. `field(default_factory=list)` calls `list()` for each new instance instead, so `a.tags.append(...)` never shows up in `b.tags`. Python rejects the bare `[]` to save you from this bug.

--- teach
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

--- predict
What does this print?
```python
print((1, "zebra") < (2, "apple"))
```
answer: True
> The first elements differ, `1 < 2`, so the comparison is decided there. The strings are never looked at. That is exactly how an ordered dataclass compares priorities before anything else.

--- teach
### `__post_init__`: validate after the generated `__init__`
You do not write `__init__`, so where do checks go? `__post_init__(self)` runs right after the generated `__init__` has stored the fields. Raise there if a value is out of range.
```python
def __post_init__(self):
    if not 1 <= self.priority <= 4:
        raise ValueError(f"priority must be 1..4, got {self.priority}")
```

--- fill
Complete the method name so the check runs on every new ticket.
```python
def ___(self):
    if not 1 <= self.priority <= 4:
        raise ValueError(f"priority must be 1..4, got {self.priority}")
```
answer: __post_init__
> The dataclass machinery calls `__post_init__` automatically at the end of the generated `__init__`. Any other name is just a method nobody calls.

--- teach
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

--- fill
Complete the call that parses the ISO timestamp string.
```python
created = datetime.___(data["created"])
```
answer: fromisoformat
> `datetime.fromisoformat("2024-05-01T09:30:00")` returns a `datetime`. `strptime` would work too but needs a format string you would have to get exactly right.

--- exercise 8.2

--- recap
- `@dataclass` generates `__init__`, `__repr__`, `__eq__` from annotated fields.
- Fields without defaults come first; list defaults use `field(default_factory=list)`.
- `order=True` compares fields as a tuple in declaration order.
- `__post_init__` is where validation goes.
- `@classmethod` + `cls(...)` for alternative constructors; `@property` for computed reads.
