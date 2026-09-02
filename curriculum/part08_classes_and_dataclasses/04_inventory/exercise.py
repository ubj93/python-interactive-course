"""An Inventory container.

We keep the fleet in memory as a collection of `Device` records keyed by serial
(the frozen dataclass below is given; do not change it). Write `Inventory`, a
container that *has* a dict rather than *is* one, so callers can only do what
we allow, and that behaves like a built-in collection with len(), in, for and [].

Methods:
- `__init__(self, devices=None)`: start empty; if an iterable of devices is
  given, add each one with `add` (so duplicates in the input raise too).
- `add(device)`: store by `device.serial`. A serial that is already present
  raises ValueError; the existing record is not replaced.
- `get(serial, default=None)`: the device with that serial, or `default`.
- `__getitem__(serial)`: the device, or KeyError when absent.
- `remove(serial)`: delete and return the device; KeyError when absent.
- `__len__`: number of devices.
- `__iter__`: yield devices in insertion order. Every call must return a fresh
  iterator so the inventory can be looped over more than once.
- `__contains__(item)`: True when `item` is a serial string that is present, or
  a Device whose serial is present. Anything else is False.

Examples:
    >>> inv = Inventory()
    >>> inv.add(Device("C02XG1234ABC", "mbp-j-doe"))
    >>> len(inv), "C02XG1234ABC" in inv, "NOPE" in inv
    (1, True, False)
    >>> inv["C02XG1234ABC"].hostname
    'mbp-j-doe'
    >>> inv.add(Device("C02XG1234ABC", "other-name"))
    Traceback (most recent call last):
    ValueError: duplicate serial: C02XG1234ABC
    >>> [d.hostname for d in inv]
    ['mbp-j-doe']
    >>> inv.remove("C02XG1234ABC").hostname, len(inv)
    ('mbp-j-doe', 0)
"""
from dataclasses import dataclass
from typing import Any, Iterable, Iterator, Optional


@dataclass(frozen=True)
class Device:
    serial: str
    hostname: str


class Inventory:
    def __init__(self, devices: Optional[Iterable[Device]] = None) -> None:
        raise NotImplementedError("write Inventory.__init__")

    def add(self, device: Device) -> None:
        raise NotImplementedError("write Inventory.add")

    def get(self, serial: str, default: Optional[Device] = None) -> Optional[Device]:
        raise NotImplementedError("write Inventory.get")

    def remove(self, serial: str) -> Device:
        raise NotImplementedError("write Inventory.remove")

    def __getitem__(self, serial: str) -> Device:
        raise NotImplementedError("write Inventory.__getitem__")

    def __len__(self) -> int:
        raise NotImplementedError("write Inventory.__len__")

    def __iter__(self) -> Iterator[Device]:
        raise NotImplementedError("write Inventory.__iter__")

    def __contains__(self, item: Any) -> bool:
        raise NotImplementedError("write Inventory.__contains__")
