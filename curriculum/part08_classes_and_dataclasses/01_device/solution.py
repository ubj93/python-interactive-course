"""Reference solutions for Device."""
from dataclasses import dataclass, field


# Best practice: normalise in __init__, repr rebuilds the object, eq and hash agree on the
# same field (serial), and __eq__ returns NotImplemented for foreign types instead of False.
class Device:
    def __init__(self, hostname: str, serial: str, os_name: str, ram_gb: int) -> None:
        self.hostname = hostname.strip().lower()
        self.serial = serial
        self.os_name = os_name
        self.ram_gb = ram_gb

    def __repr__(self) -> str:
        return (
            f"Device(hostname={self.hostname!r}, serial={self.serial!r}, "
            f"os_name={self.os_name!r}, ram_gb={self.ram_gb!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Device):
            return NotImplemented
        return self.serial == other.serial

    def __hash__(self) -> int:
        return hash(self.serial)

    def describe(self) -> str:
        return f"{self.hostname}: {self.os_name}, {self.ram_gb} GB RAM"


# Clever: the same contract as a dataclass. compare=False keeps three fields out of the
# generated __eq__, __post_init__ normalises, and eq=True + frozen=False would set __hash__
# to None, so we spell out __hash__ ourselves. Preview of the next exercise.
@dataclass
class DeviceDC:
    hostname: str = field(compare=False)
    serial: str
    os_name: str = field(compare=False)
    ram_gb: int = field(compare=False)

    def __post_init__(self) -> None:
        self.hostname = self.hostname.strip().lower()

    def __hash__(self) -> int:
        return hash(self.serial)

    def describe(self) -> str:
        return f"{self.hostname}: {self.os_name}, {self.ram_gb} GB RAM"
