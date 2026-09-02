"""Compose functions into one.

Hostname clean-up is a chain of small functions: strip, lowercase, drop the
domain. Rather than calling them one inside the other every time, write
`compose(*funcs)` that returns a single new function. Calling that function
with one argument applies the composed functions right to left, the way
mathematical composition works:

    compose(f, g, h)(x)  ==  f(g(h(x)))

Rules:
- the LAST function given is applied first; the first one is applied last
- compose() with no functions returns an identity function: compose()(x) == x
- compose(f) with one function behaves like f
- every argument must be callable; a non-callable raises TypeError at
  compose time (when compose is called), not later when the result is used
- the returned function takes exactly one positional argument and can be
  called any number of times; two composed functions must not share state

Examples:
    >>> clean = compose(str.lower, str.strip)
    >>> clean("  MBP-J-DOE ")
    'mbp-j-doe'
    >>> compose(lambda x: x + 1, lambda x: x * 10)(4)
    41
    >>> compose()("unchanged")
    'unchanged'
"""
from typing import Any, Callable


def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    raise NotImplementedError("write compose")
