"""Reference solutions for Inventory."""
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Iterator, Optional


@dataclass(frozen=True)
class Device:
    serial: str
    hostname: str


# Best practice: composition. One private dict does the work; every public method is a
# thin, validated door onto it. A dict remembers insertion order, so iteration is free.
# __iter__ hands back the dict's own iterator, which is fresh on every call.
class Inventory:
    def __init__(self, devices: Optional[Iterable[Device]] = None) -> None:
        self._by_serial: Dict[str, Device] = {}
        for device in devices or ():
            self.add(device)

    def add(self, device: Device) -> None:
        if device.serial in self._by_serial:
            raise ValueError(f"duplicate serial: {device.serial}")
        self._by_serial[device.serial] = device

    def get(self, serial: str, default: Optional[Device] = None) -> Optional[Device]:
        return self._by_serial.get(serial, default)

    def remove(self, serial: str) -> Device:
        return self._by_serial.pop(serial)          # KeyError propagates, as specified

    def __getitem__(self, serial: str) -> Device:
        return self._by_serial[serial]

    def __len__(self) -> int:
        return len(self._by_serial)

    def __iter__(self) -> Iterator[Device]:
        return iter(self._by_serial.values())

    def __contains__(self, item: Any) -> bool:
        if isinstance(item, Device):
            return item.serial in self._by_serial
        return isinstance(item, str) and item in self._by_serial


# Clever: the same container, but __iter__ as a generator function. A generator method
# returns a new generator per call automatically, and it lets you filter or transform
# while iterating without building a list. Shown here so you recognise both shapes.
class InventoryGen(Inventory):
    def __iter__(self) -> Iterator[Device]:
        for device in self._by_serial.values():
            yield device
