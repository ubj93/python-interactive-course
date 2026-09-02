"""Reference solutions for rolling_average."""
from typing import List


# Best practice: one slice per output. max(0, i - n + 1) clamps the window start so the
# early windows are short instead of wrapping to the end (a negative start would do that).
def rolling_average(samples: List[float], n: int) -> List[float]:
    if n < 1:
        raise ValueError(f"window must be at least 1, got {n}")
    out = []
    for i in range(len(samples)):
        window = samples[max(0, i - n + 1):i + 1]
        out.append(round(sum(window) / len(window), 2))
    return out


# Clever: keep a running sum and subtract the sample that falls out of the window. Same
# answers, but O(len) instead of O(len * n); worth mentioning when n is large.
def rolling_average_running_sum(samples: List[float], n: int) -> List[float]:
    if n < 1:
        raise ValueError(f"window must be at least 1, got {n}")
    out = []
    total = 0.0
    for i, value in enumerate(samples):
        total += value
        if i >= n:
            total -= samples[i - n]
        count = min(i + 1, n)
        out.append(round(total / count, 2))
    return out
