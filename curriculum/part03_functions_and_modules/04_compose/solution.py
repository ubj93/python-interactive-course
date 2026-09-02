"""Reference solutions for compose."""
from functools import reduce
from typing import Any, Callable


# Best practice: a closure over the tuple of functions. Validation happens in the outer
# function, so a bad argument fails where it was written, not on first use; the inner
# loop walks the functions in reverse so the last one runs first.
def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    for f in funcs:
        if not callable(f):
            raise TypeError(f"compose() arguments must be callable, got {f!r}")

    def composed(x: Any) -> Any:
        for f in reversed(funcs):
            x = f(x)
        return x

    return composed


# Clever: functools.reduce folds the functions pairwise, building f(g(h(x))) from the
# inside out. The initial value is the identity, which also handles compose() with no
# arguments. Dense, but it is the textbook definition and interviewers recognise it.
def compose_reduce(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    for f in funcs:
        if not callable(f):
            raise TypeError(f"compose() arguments must be callable, got {f!r}")
    return reduce(lambda f, g: (lambda x: f(g(x))), funcs, lambda x: x)
