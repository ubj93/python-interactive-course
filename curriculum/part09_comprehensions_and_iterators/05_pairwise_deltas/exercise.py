"""Time between consecutive check-ins.

The MDM logs a timestamp every time a device checks in. To spot devices that
go quiet we want the gap between each check-in and the next. Write
`pairwise_deltas(checkins)`.

- `checkins` is a sequence (list or tuple) of `datetime` objects in
  chronological order.
- Return a list of floats: the seconds between each consecutive pair, so the
  result has one element fewer than the input. Use `timedelta.total_seconds()`.
- Fewer than two check-ins: return an empty list.
- Two equal timestamps give 0.0. Sub-second gaps give fractional seconds.
- A timestamp earlier than the one before it means the log is out of order:
  raise ValueError with a message that includes the index of the offending
  entry.

Pair each element with the next one using `zip(checkins, checkins[1:])`.
`itertools.pairwise` does the same but only exists from Python 3.10, and the
zip idiom is what you will write in interviews.

Examples:
    >>> ts = [datetime(2024, 5, 1, 9, 0, 0), datetime(2024, 5, 1, 9, 0, 30), datetime(2024, 5, 1, 9, 15, 0)]
    >>> pairwise_deltas(ts)
    [30.0, 870.0]
    >>> pairwise_deltas([datetime(2024, 5, 1, 9, 0, 0)])
    []
    >>> pairwise_deltas([datetime(2024, 5, 1, 9, 1), datetime(2024, 5, 1, 9, 0)])
    Traceback (most recent call last):
    ValueError: check-in 1 is earlier than check-in 0
"""
from datetime import datetime
from typing import List, Sequence


def pairwise_deltas(checkins: Sequence[datetime]) -> List[float]:
    raise NotImplementedError("write pairwise_deltas")
