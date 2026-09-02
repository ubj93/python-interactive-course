"""Reference solutions for chunk_serials."""
from typing import List


# Best practice: range with a step gives the start index of every batch, and a slice
# past the end simply stops early, so the short last batch needs no special case.
def chunk_serials(serials: List[str], size: int) -> List[List[str]]:
    if size < 1:
        raise ValueError(f"size must be at least 1, got {size}")
    batches = []
    for start in range(0, len(serials), size):
        batches.append(serials[start:start + size])
    return batches


# Clever: the same thing as a list comprehension. Preferred once you have read Part 9;
# for now notice that it is the loop above with the append folded into the brackets.
def chunk_serials_comprehension(serials: List[str], size: int) -> List[List[str]]:
    if size < 1:
        raise ValueError(f"size must be at least 1, got {size}")
    return [serials[i:i + size] for i in range(0, len(serials), size)]
