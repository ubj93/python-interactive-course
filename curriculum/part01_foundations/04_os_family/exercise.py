"""Classify a platform string.

Inventory systems report the operating system in wildly different ways:
"macOS 14.5", "Mac OS X 10.15.7", "Microsoft Windows 11 Enterprise",
"Ubuntu 22.04.4 LTS", "ChromeOS 125", "iOS 17.5.1". Write `os_family(os_string)`
that maps any of those to one of five families:

- "mac"     when the string mentions mac OS in any form ("macOS", "Mac OS X", "OS X")
- "windows" when it contains "windows"
- "linux"   when it contains "linux", "ubuntu", "debian", "fedora", "rhel", or "centos"
- "ios"     when it starts with "iOS" or "iPadOS"
- "other"   for anything else, including empty input and None

Matching must be case-insensitive and tolerate surrounding whitespace.
Order matters: check iOS before mac, or "iOS" would never win over "OS".

Examples:
    >>> os_family("Mac OS X 10.15.7")
    'mac'
    >>> os_family("  microsoft windows 11 enterprise ")
    'windows'
    >>> os_family("iPadOS 17.5")
    'ios'
    >>> os_family("FreeBSD 14")
    'other'
"""
from typing import Optional


def os_family(os_string: Optional[str]) -> str:
    raise NotImplementedError("write os_family")
