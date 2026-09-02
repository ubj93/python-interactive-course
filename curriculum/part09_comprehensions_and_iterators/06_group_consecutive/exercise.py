"""Runs of build results.

CI reports a list of builds in the order they ran, each as `(build_id, status)`
where status is "pass" or "fail". The release dashboard wants the *runs*: how
many builds in a row had the same status, and which failing streak was the
longest. Two functions, both built on `itertools.groupby`.

`group_consecutive(results)`
- Returns a list of `(status, [build_ids])` tuples, one per run of adjacent
  builds with the same status, in order.
- Only adjacent builds are grouped: "pass, fail, pass" is three runs, not two.
  That is what groupby does on unsorted data, and here it is exactly right.
- Empty input returns an empty list. Statuses are compared exactly.

`longest_failing_streak(results)`
- Returns the list of build ids in the longest run whose status is "fail".
- When several runs tie for longest, return the earliest one.
- No failing builds: return an empty list.

Examples:
    >>> results = [("b1", "pass"), ("b2", "fail"), ("b3", "fail"), ("b4", "pass"), ("b5", "fail")]
    >>> group_consecutive(results)
    [('pass', ['b1']), ('fail', ['b2', 'b3']), ('pass', ['b4']), ('fail', ['b5'])]
    >>> longest_failing_streak(results)
    ['b2', 'b3']
    >>> longest_failing_streak([("b1", "pass")])
    []
"""
from itertools import groupby
from typing import List, Sequence, Tuple


def group_consecutive(results: Sequence[Tuple[str, str]]) -> List[Tuple[str, List[str]]]:
    raise NotImplementedError("write group_consecutive")


def longest_failing_streak(results: Sequence[Tuple[str, str]]) -> List[str]:
    raise NotImplementedError("write longest_failing_streak")
