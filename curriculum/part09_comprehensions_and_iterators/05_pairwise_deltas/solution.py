"""Reference solutions for pairwise_deltas."""
from datetime import datetime
from typing import Iterable, List, Sequence


# Best practice: zip a sequence with itself shifted by one; zip stops at the shorter side,
# so a single element gives no pairs and no special case is needed. enumerate(..., 1)
# gives the index of the later element for the error message.
def pairwise_deltas(checkins: Sequence[datetime]) -> List[float]:
    deltas = []
    for i, (earlier, later) in enumerate(zip(checkins, checkins[1:]), start=1):
        if later < earlier:
            raise ValueError(f"check-in {i} is earlier than check-in {i - 1}")
        deltas.append((later - earlier).total_seconds())
    return deltas


# Clever: works on any iterable, not just sequences, by pulling the first item with next()
# and remembering the previous one. This is what itertools.pairwise does internally, and
# it is the shape to use when the check-ins stream from a file or an API cursor.
def pairwise_deltas_stream(checkins: Iterable[datetime]) -> List[float]:
    it = iter(checkins)
    previous = next(it, None)
    if previous is None:
        return []
    deltas = []
    for i, current in enumerate(it, start=1):
        if current < previous:
            raise ValueError(f"check-in {i} is earlier than check-in {i - 1}")
        deltas.append((current - previous).total_seconds())
        previous = current
    return deltas
