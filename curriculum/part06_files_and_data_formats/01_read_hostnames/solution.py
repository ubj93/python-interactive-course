"""Reference solutions for read_hostnames."""
from pathlib import Path
from typing import List, Union


# Best practice: iterate the file inside `with`, strip first, then test the two skip
# rules with `continue`. Memory is constant however long the list grows.
def read_hostnames(path: Union[str, Path]) -> List[str]:
    hosts: List[str] = []
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            hosts.append(line)
    return hosts


# Clever: Path.read_text + a comprehension. Shorter, but it loads the whole file, so
# say so out loud if you write it in an interview.
def read_hostnames_comprehension(path: Union[str, Path]) -> List[str]:
    lines = (line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines())
    return [line for line in lines if line and not line.startswith("#")]
