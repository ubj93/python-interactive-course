"""Reference solutions for read_lines_lazy."""
from typing import Iterable, Iterator


# Best practice: a generator that does one line of work per line of input. Iterating the
# file object directly is what keeps memory flat; str.partition drops the comment whether
# or not there is one; the `if` skips whatever is left empty.
def read_lines_lazy(lines: Iterable[str]) -> Iterator[str]:
    for line in lines:
        text = line.partition("#")[0].strip()
        if text:
            yield text


# Clever: a generator expression does the same job and is also lazy. It reads well for a
# two-step pipeline; once there is a third rule (say, lowercasing or validation), the
# generator function above is easier to grow.
def read_lines_lazy_genexp(lines: Iterable[str]) -> Iterator[str]:
    return (text for text in (line.partition("#")[0].strip() for line in lines) if text)
