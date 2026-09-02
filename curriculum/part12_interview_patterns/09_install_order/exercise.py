"""Order packages so dependencies install first.

A Munki-style catalog lists, for each package, the packages it requires.
Write `install_order(packages)` that returns a list with every package in an
order where each one comes after everything it depends on.

`packages` maps a package name to a list of the names it requires. A name
that appears only as a dependency (never as a key) is a real package with no
requirements of its own and must be included in the order.

Rules:
- every package appears exactly once
- a package appears after all of its dependencies
- when several packages are ready to install at the same time, take them in
  alphabetical order (this makes the answer unique and testable)
- duplicate names inside a dependency list are harmless
- a dependency cycle raises ValueError; the message must name every package
  on the cycle, for example "dependency cycle: a -> b -> c -> a"; a package
  that depends on itself is a cycle of one
- an empty dict gives an empty list

Complexity target: O(V log V + E) with Kahn's algorithm (in-degree counting
and a heap of ready packages); the log factor pays for the alphabetical
tie-break. The last test has 3,000 packages in a chain, which a repeated
"scan for anything ready" approach handles at O(V^2) but visibly slower.

Examples:
    >>> install_order({"munki": ["python"], "osquery": [], "python": []})
    ['osquery', 'python', 'munki']
    >>> install_order({"agent": ["sdk"]})
    ['sdk', 'agent']
    >>> install_order({"a": ["b"], "b": ["a"]})
    Traceback (most recent call last):
    ValueError: dependency cycle: a -> b -> a
"""
from typing import Dict, List


def install_order(packages: Dict[str, List[str]]) -> List[str]:
    raise NotImplementedError("write install_order")
