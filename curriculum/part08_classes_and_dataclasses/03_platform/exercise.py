"""A Platform enum that tolerates messy input.

Every inventory source spells the operating system differently: "macOS 14.5",
"Mac OS X 10.15.7", "Microsoft Windows 11 Enterprise", "Ubuntu 22.04 LTS",
"darwin", "win32". Downstream code should only ever see one of four members.

`Platform` is an Enum with members MAC = "mac", WINDOWS = "windows",
LINUX = "linux" and IOS = "ios" (already declared). Add:

`Platform.from_string(raw)` classmethod, applying these rules in order:
1. `None`, an empty string or whitespace only: raise ValueError.
2. Normalise: strip, lowercase, cut off everything from the first digit
   onwards (that drops version numbers), strip again, and collapse any run
   of whitespace to a single space. "Mac OS X 10.15.7" becomes "mac os x".
3. If the normalised text equals a member value, return that member.
4. Otherwise look it up in the alias table below.
5. Otherwise try the first word of the normalised text against rules 3 and 4,
   so "windows server" -> WINDOWS and "ubuntu lts" -> LINUX.
6. Anything else: raise ValueError with the original input in the message.

Aliases (all already lowercase):
    MAC:     macos, mac os, mac os x, os x, osx, darwin
    WINDOWS: win, win32, microsoft windows
    LINUX:   ubuntu, debian, fedora, rhel, centos, gnu/linux
    IOS:     ipados, iphone os

Note: "win32" never reaches the table intact because rule 2 cuts the digits; it
is listed so the table is honest about what people type. Do not put the alias
dict inside the class body: an Enum turns every non-dunder class attribute
into a member. Define it at module level, after the class.

`Platform.is_apple` property: True for MAC and IOS.

Examples:
    >>> Platform.from_string("  macOS 14.5 ")
    <Platform.MAC: 'mac'>
    >>> Platform.from_string("Microsoft Windows 11 Enterprise") is Platform.WINDOWS
    True
    >>> Platform.from_string("Debian GNU/Linux 12")
    <Platform.LINUX: 'linux'>
    >>> Platform.from_string("FreeBSD 14")
    Traceback (most recent call last):
    ValueError: unknown platform: 'FreeBSD 14'
    >>> Platform.IOS.is_apple, Platform.LINUX.is_apple
    (True, False)
"""
from enum import Enum
from typing import Optional


class Platform(Enum):
    MAC = "mac"
    WINDOWS = "windows"
    LINUX = "linux"
    IOS = "ios"

    @classmethod
    def from_string(cls, raw: Optional[str]) -> "Platform":
        raise NotImplementedError("write Platform.from_string")

    @property
    def is_apple(self) -> bool:
        raise NotImplementedError("write Platform.is_apple")
