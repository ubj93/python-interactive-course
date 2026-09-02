"""Model a device as a class.

The fleet tool passes device records around as dicts, and every function that
touches one has to remember which keys exist and how they are spelled. Replace
the dict with a class that normalises its input once and knows how to print,
compare and describe itself.

Write `Device` with:

- `__init__(self, hostname, serial, os_name, ram_gb)`: store the four values as
  attributes with the same names. Normalise `hostname` on the way in: strip
  surrounding whitespace and lowercase it. Store the other three exactly as given.
- `__repr__`: return the constructor call that would rebuild the object, with
  keyword arguments in the order above and `!r` formatting so strings are quoted:
  `Device(hostname='mbp-j-doe', serial='C02XG1234ABC', os_name='macOS', ram_gb=16)`
- `__eq__`: two devices are equal when their serials are equal; hostname, OS and
  RAM do not matter. When `other` is not a Device return `NotImplemented`, so
  `device == "C02XG1234ABC"` is simply False and does not raise.
- `__hash__`: hash on the serial. Defining `__eq__` without `__hash__` makes
  instances unhashable, and we want devices to work as set members and dict keys.
- `describe(self)`: return "<hostname>: <os_name>, <ram_gb> GB RAM".

Examples:
    >>> d = Device("  MBP-J-DOE ", "C02XG1234ABC", "macOS", 16)
    >>> d.hostname
    'mbp-j-doe'
    >>> d
    Device(hostname='mbp-j-doe', serial='C02XG1234ABC', os_name='macOS', ram_gb=16)
    >>> d == Device("spare-laptop", "C02XG1234ABC", "macOS", 32)
    True
    >>> len({d, Device("spare-laptop", "C02XG1234ABC", "macOS", 32)})
    1
    >>> d.describe()
    'mbp-j-doe: macOS, 16 GB RAM'
"""


class Device:
    def __init__(self, hostname: str, serial: str, os_name: str, ram_gb: int) -> None:
        raise NotImplementedError("write Device.__init__")

    def __repr__(self) -> str:
        raise NotImplementedError("write Device.__repr__")

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError("write Device.__eq__")

    def __hash__(self) -> int:
        raise NotImplementedError("write Device.__hash__")

    def describe(self) -> str:
        raise NotImplementedError("write Device.describe")
