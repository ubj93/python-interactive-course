"""Reference solutions for Platform."""
import re
from enum import Enum
from typing import Optional


# Best practice: normalise once, then a small ladder of lookups. The alias table lives
# *below* the class because anything assigned inside an Enum body becomes a member.
# `cls._value2member_map_` is internal; `cls(value)` inside try/except is the public way.
class Platform(Enum):
    MAC = "mac"
    WINDOWS = "windows"
    LINUX = "linux"
    IOS = "ios"

    @classmethod
    def from_string(cls, raw: Optional[str]) -> "Platform":
        if raw is None or not raw.strip():
            raise ValueError(f"unknown platform: {raw!r}")
        text = re.split(r"\d", raw.strip().lower(), maxsplit=1)[0]
        text = " ".join(text.split())
        for candidate in (text, text.split(" ", 1)[0]):
            member = _lookup(cls, candidate)
            if member is not None:
                return member
        raise ValueError(f"unknown platform: {raw!r}")

    @property
    def is_apple(self) -> bool:
        return self in (Platform.MAC, Platform.IOS)


ALIASES = {
    "macos": Platform.MAC, "mac os": Platform.MAC, "mac os x": Platform.MAC,
    "os x": Platform.MAC, "osx": Platform.MAC, "darwin": Platform.MAC,
    "win": Platform.WINDOWS, "win32": Platform.WINDOWS, "microsoft windows": Platform.WINDOWS,
    "ubuntu": Platform.LINUX, "debian": Platform.LINUX, "fedora": Platform.LINUX,
    "rhel": Platform.LINUX, "centos": Platform.LINUX, "gnu/linux": Platform.LINUX,
    "ipados": Platform.IOS, "iphone os": Platform.IOS,
}


def _lookup(cls, text: str) -> Optional[Platform]:
    try:
        return cls(text)            # rule 3: exact member value
    except ValueError:
        return ALIASES.get(text)    # rule 4: alias table, or None


# Clever: fold the member values into the alias table once, so the lookup is a single
# dict.get. Same rules, fewer branches; the cost is that the table must be built after
# the class exists, which is true of any alias table for an Enum anyway.
_ALL = {**{p.value: p for p in Platform}, **ALIASES}


def platform_from_string_table(raw: Optional[str]) -> Platform:
    if raw is None or not raw.strip():
        raise ValueError(f"unknown platform: {raw!r}")
    text = " ".join(re.split(r"\d", raw.strip().lower(), maxsplit=1)[0].split())
    member = _ALL.get(text) or _ALL.get(text.split(" ", 1)[0])
    if member is None:
        raise ValueError(f"unknown platform: {raw!r}")
    return member
