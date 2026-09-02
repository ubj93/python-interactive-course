"""Reference solutions for group_consecutive and longest_failing_streak."""
from itertools import groupby
from operator import itemgetter
from typing import List, Sequence, Tuple


# Best practice: groupby with the status as key yields (key, iterator-of-items) for each run
# of adjacent equal keys. The group iterator is only valid until the next key is pulled,
# so it is materialised right away inside the comprehension.
def group_consecutive(results: Sequence[Tuple[str, str]]) -> List[Tuple[str, List[str]]]:
    return [
        (status, [build_id for build_id, _ in run])
        for status, run in groupby(results, key=itemgetter(1))
    ]


# max() with key=len returns the *first* maximal element, which is the tie rule we want;
# default=[] covers the no-failures case without a separate branch.
def longest_failing_streak(results: Sequence[Tuple[str, str]]) -> List[str]:
    failing_runs = [ids for status, ids in group_consecutive(results) if status == "fail"]
    return max(failing_runs, key=len, default=[])


# Clever (or rather: honest): what groupby does, written out. If you blank on itertools
# in an interview, this loop is the fallback. Compare the previous key, start a new run
# on change, and do not forget to flush the last run after the loop.
def group_consecutive_loop(results: Sequence[Tuple[str, str]]) -> List[Tuple[str, List[str]]]:
    runs: List[Tuple[str, List[str]]] = []
    for build_id, status in results:
        if runs and runs[-1][0] == status:
            runs[-1][1].append(build_id)
        else:
            runs.append((status, [build_id]))
    return runs
