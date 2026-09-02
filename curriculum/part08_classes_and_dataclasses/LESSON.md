# Part 8 · Classes and dataclasses

> **What you will be able to do:** model the things a fleet tool talks about (a
> device, a ticket, a platform, an inventory, a version number, a rate limiter) as
> Python objects that print well, compare correctly, live in sets and dicts, sort, and
> keep their invariants. Budget about two hours; the exercises are the longest so far.

## Why classes here

You have written functions that take dicts and return dicts. That works until three
functions each assume a slightly different set of keys and one of them writes
`d["lastSeen"]` while another reads `d["last_seen"]`. A class gives the data a name, a
constructor that validates it, and a home for the behaviour that belongs to it.

Interviewers use class questions to see whether you know the *protocols*: what Python
calls when it prints your object, compares it, hashes it, sorts it, or asks for its
length. Each of those is a dunder ("double underscore") method. This part is a tour of
the ones that matter.

## 1. A class is a namespace with a constructor

```python
>>> class Device:
...     fleet = "corp"                       # class attribute: shared by every instance
...
...     def __init__(self, hostname, serial):
...         self.hostname = hostname.strip().lower()   # instance attributes: per object
...         self.serial = serial
...
...     def describe(self):
...         return f"{self.hostname} ({self.serial})"
...
>>> d = Device("  MBP-J-DOE ", "C02XG1234ABC")
>>> d.hostname
'mbp-j-doe'
>>> d.describe()
'mbp-j-doe (C02XG1234ABC)'
>>> Device.describe(d)          # exactly the same call; `self` is just the first argument
'mbp-j-doe (C02XG1234ABC)'
```

- `__init__` runs right after the object is created. Normalise and validate here, once,
  so nothing else has to.
- `self` is the instance. Python passes it for you when you call `d.describe()`.
- A **class attribute** lives on the class and is shared. An **instance attribute** is
  set on `self`. Reading `d.fleet` finds the class attribute; writing `d.fleet = "lab"`
  creates a new instance attribute that shadows it.

**Gotcha:** a mutable class attribute is shared by *all* instances.

```python
>>> class Group:
...     members = []                     # one list, shared by every Group
...     def add(self, name):
...         self.members.append(name)    # mutates the shared list
...
>>> a, b = Group(), Group()
>>> a.add("x"); b.members
['x']
```

Create per-instance containers inside `__init__` (`self.members = []`).

## 2. `__repr__` and `__str__`

```python
>>> d
<__main__.Device object at 0x10ad0c1f0>      # useless
```

Define `__repr__` to return the constructor call that rebuilds the object. Use `!r` so
strings get their quotes:

```python
def __repr__(self):
    return f"Device(hostname={self.hostname!r}, serial={self.serial!r})"
```

`__str__` is the friendly form used by `print` and `f"{d}"`. If you only define one,
define `__repr__`: `str()` falls back to it, and it is what shows in the REPL, in
lists, and in failing test output.

## 3. Equality and hashing

By default two objects are equal only when they are the *same* object. Override
`__eq__` when the domain says otherwise: two device records are the same device when
their serials match.

```python
def __eq__(self, other):
    if not isinstance(other, Device):
        return NotImplemented          # let Python try the other side, then fall back to False
    return self.serial == other.serial

def __hash__(self):
    return hash(self.serial)
```

Three rules interviewers probe:

1. Return `NotImplemented` (not `False`) for foreign types. Python then tries
   `other.__eq__(self)` and only then answers `False`.
2. **Defining `__eq__` sets `__hash__` to `None`.** Your objects stop working as dict
   keys and set members until you define `__hash__` too.
3. Equal objects must have equal hashes. Hash on the same fields you compare.

```python
>>> {Device("a", "S1"), Device("b", "S1")}
{Device(hostname='a', serial='S1')}          # one element: same serial
```

Only hash on fields that never change. If `serial` could be reassigned after the
object is in a set, the set silently breaks.

## 4. Properties

A property is a method that reads like an attribute. Use it for values computed from
other fields, or to validate on assignment.

```python
>>> class Disk:
...     def __init__(self, used, total):
...         self.used, self.total = used, total
...     @property
...     def pct(self):
...         return self.used / self.total
...
>>> Disk(80, 100).pct
0.8
```

Add a setter with `@pct.setter` if you need assignment. Do not turn every attribute
into a property; plain attributes are fine until you need to intercept access.

## 5. `classmethod` and `staticmethod`

A **classmethod** receives the class (`cls`) instead of the instance. The classic use
is an alternative constructor:

```python
@classmethod
def from_dict(cls, data):
    return cls(data["hostname"], data["serial"])
```

Naming them `from_dict`, `from_string`, `from_row` is a convention people recognise.
Calling `cls(...)` rather than `Device(...)` means subclasses get the right type.

A **staticmethod** gets neither `self` nor `cls`. It is a plain function stored on the
class because it belongs there logically (`Version.is_valid(text)`). Use it rarely; a
module-level function is usually clearer.

## 6. Dataclasses

Most classes are "a record with a few methods". `@dataclass` writes `__init__`,
`__repr__` and `__eq__` for you from the annotated fields:

```python
>>> from dataclasses import dataclass, field
>>> from typing import List, Optional
>>> @dataclass
... class Ticket:
...     priority: int
...     title: str
...     assignee: Optional[str] = None
...     tags: List[str] = field(default_factory=list)
...
>>> Ticket(2, "Wi-Fi drops")
Ticket(priority=2, title='Wi-Fi drops', assignee=None, tags=[])
>>> Ticket(2, "a") == Ticket(2, "a")
True
```

| Option | Effect |
|---|---|
| `field(default_factory=list)` | a *new* list per instance (a bare `= []` is rejected: it would be shared) |
| `field(compare=False)` | leave this field out of `__eq__` and ordering |
| `field(repr=False)` | hide it from `__repr__` |
| `@dataclass(order=True)` | generate `<`, `<=`, `>`, `>=` comparing fields as a tuple, in declaration order |
| `@dataclass(frozen=True)` | assignment raises; instances become hashable |
| `__post_init__(self)` | runs after the generated `__init__`; validate or derive fields here |
| `dataclasses.asdict(t)` | back to a plain dict (recursively) |

Ordering compares the fields *as a tuple in declaration order*. Put the fields you want
to sort by first: a `Ticket` with `priority` then `created` sorts by priority, ties
broken by creation time. That is the whole trick behind exercise 2.

**Gotchas**

- Fields without defaults must come before fields with defaults, exactly like function
  parameters.
- `@dataclass` without `frozen=True` but with `eq=True` (the default) gives you
  `__hash__ = None`, the same trap as section 3. Use `frozen=True` or `unsafe_hash=True`
  when instances need to go in sets.
- `order=True` compares `None` with `str` if two records tie on every earlier field and
  differ there: `TypeError`. Keep optional fields late in the declaration or exclude
  them with `compare=False`.

## 7. Enum

An `Enum` is a fixed set of named constants. Members are singletons, compare by
identity, and print by name.

```python
>>> from enum import Enum
>>> class Platform(Enum):
...     MAC = "mac"
...     WINDOWS = "windows"
...
>>> Platform.MAC
<Platform.MAC: 'mac'>
>>> Platform.MAC.value, Platform.MAC.name
('mac', 'MAC')
>>> Platform("mac") is Platform.MAC        # lookup by value
True
>>> Platform("darwin")
ValueError: 'darwin' is not a valid Platform
>>> list(Platform)
[<Platform.MAC: 'mac'>, <Platform.WINDOWS: 'windows'>]
```

Real input is messier than the values, so pair the enum with a `from_string`
classmethod that normalises and maps aliases. Two gotchas:

- Every non-dunder name in the class body becomes a member, **including a dict of
  aliases**. Keep lookup tables at module level, below the class.
- `Platform.MAC == "mac"` is `False`. Compare members with members, or compare `.value`.

## 8. Ordering with `functools.total_ordering`

Sorting needs `__lt__`; a complete comparable type needs all six operators. Write
`__eq__` and `__lt__`, decorate the class with `@functools.total_ordering`, and the
other four are derived.

```python
@total_ordering
class Version:
    def __init__(self, text):
        self.parts = tuple(int(p) for p in text.split("."))
    def __eq__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self.parts == other.parts
    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self.parts < other.parts
```

Tuples compare element by element, so `(1, 10) > (1, 9)`, which is exactly what a
version needs and exactly what string comparison gets wrong (`"1.10" < "1.9"`).
Remember `__hash__` if you define `__eq__`.

## 9. Container protocols

Make your collection feel like a built-in one by implementing the dunders `len`,
`in`, `for` and `[]` call:

| You write | Python calls |
|---|---|
| `len(inv)` | `inv.__len__()` |
| `x in inv` | `inv.__contains__(x)` (falls back to iterating if absent) |
| `for d in inv` | `inv.__iter__()` then `next()` on the result |
| `inv["C02X"]` | `inv.__getitem__("C02X")`; raise `KeyError` for a missing key |
| `bool(inv)` | `__bool__`, else `__len__() != 0` |

`__iter__` must return a *fresh* iterator each time. The easy way is to return the
iterator of an internal container (`return iter(self._by_serial.values())`) or to
write `__iter__` as a generator function with `yield`. Returning `self` and
implementing `__next__` means the object can only be iterated once.

## 10. Composition over inheritance

Inheritance ("an Inventory *is a* dict") leaks the whole parent API and breaks the
moment you need `add` to validate: `dict.update`, `setdefault` and `__setitem__` all
bypass it. Composition ("an Inventory *has a* dict") exposes only the operations you
mean to support:

```python
class Inventory:
    def __init__(self):
        self._by_serial = {}        # leading underscore: internal, not part of the API
    def add(self, device):
        if device.serial in self._by_serial:
            raise ValueError(f"duplicate serial {device.serial}")
        self._by_serial[device.serial] = device
```

Inherit when you truly want to *be* the base type and change a little (custom
exceptions, `unittest.TestCase`). Compose for everything else.

## 11. State machines and injected clocks

A rate limiter, a retry policy, a session cache: objects that change over time. Two
rules make them testable:

1. Keep every piece of state on `self`, updated in one place.
2. Never call `time.time()` inside the class. Take a `now` callable in `__init__` and
   call `self._now()`. Tests pass a fake clock they can move by hand.

```python
class TokenBucket:
    def __init__(self, capacity, refill_per_second, now):
        self.capacity = capacity
        self.rate = refill_per_second
        self._now = now
        self._tokens = float(capacity)
        self._last = now()

    def _refill(self):
        t = self._now()
        self._tokens = min(self.capacity, self._tokens + (t - self._last) * self.rate)
        self._last = t
```

A fake clock is three lines:

```python
class FakeClock:
    def __init__(self): self.t = 0.0
    def __call__(self): return self.t
```

The same pattern applies to `sleep`, `random`, and anything that reads the outside
world.

## Interview notes for this part

- **Say which protocol you are implementing.** "I will define `__eq__` on serial, and
  `__hash__` to match so devices can go in a set." That sentence shows you know the
  hash/eq contract without being asked.
- **Reach for `@dataclass` first.** Hand-writing `__init__`/`__repr__`/`__eq__` for a
  record is not impressive, it is slow. Write the dataclass, then add only the methods
  the problem needs.
- **Ask what equality means.** Same serial? Same object? All fields? The answer
  changes `__eq__`, `__hash__`, and the tests.
- **Inject the clock.** If the problem mentions time, say "I will take a `now` callable
  so the tests are deterministic" before you write a line.
- **The trap:** `class Foo: items = []`. Mutable class attributes and mutable default
  arguments are the same bug wearing two hats.

## Exercises

Run `course list 8`, then `course show 8.1`.

1. `Device` · a hand-written class: `__init__`, `__repr__`, `__eq__`/`__hash__`, a method
2. `Ticket` · `@dataclass(order=True)`, `default_factory`, `__post_init__`, `from_dict`
3. `Platform` · `Enum` plus a tolerant `from_string` classmethod and a property
4. `Inventory` · composition and the container protocols
5. `Version` · a comparable value type with `total_ordering`, correct hashing, parsing
6. `TokenBucket` · a stateful object driven by an injected clock
