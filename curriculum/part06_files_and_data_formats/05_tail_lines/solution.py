"""Reference solutions for tail_lines."""
from collections import deque
from pathlib import Path
from typing import List, Union


# Best practice: deque(maxlen=n) drops the oldest item as each new one arrives, so after
# one pass over the file it holds exactly the tail. Strip the line ending on the way in.
def tail_lines(path: Union[str, Path], n: int = 10) -> List[str]:
    if n < 0:
        raise ValueError("n must be >= 0")
    with open(path, encoding="utf-8") as f:
        if n == 0:
            return []
        last = deque((line.rstrip("\r\n") for line in f), maxlen=n)
    return list(last)


# Clever: deque accepts any iterable in its constructor, so the file object can go
# straight in; strip afterwards, only on the n lines that survived.
def tail_lines_direct(path: Union[str, Path], n: int = 10) -> List[str]:
    if n < 0:
        raise ValueError("n must be >= 0")
    with open(path, encoding="utf-8") as f:
        last = deque(f, maxlen=n) if n else deque()
    return [line.rstrip("\r\n") for line in last]
