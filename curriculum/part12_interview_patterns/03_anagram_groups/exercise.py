"""Group names that are letter-scrambles of each other.

The security team suspects that some apps in the fleet inventory are the
same binary registered under scrambled names ("listen", "silent", "enlist").
Write `anagram_groups(names)` that groups anagrams together.

Two names are anagrams when they contain exactly the same characters with
the same counts. Comparison is exact: case matters and so does every
character, including digits and hyphens.

Rules:
- return a list of groups, each group a list of names
- groups appear in the order their first member appears in the input
- inside a group, names keep their input order
- a name with no anagram forms a group of one
- duplicate names are anagrams of each other and stay in the same group
- an empty input gives an empty list

Complexity target: O(n * k log k) time, where n is the number of names and k
the length of the longest one, using a canonical key per name and a dict.
The last test has 5,000 names.

Examples:
    >>> anagram_groups(["listen", "silent", "google", "enlist"])
    [['listen', 'silent', 'enlist'], ['google']]
    >>> anagram_groups(["abc", "Abc"])
    [['abc'], ['Abc']]
"""
from typing import List


def anagram_groups(names: List[str]) -> List[List[str]]:
    raise NotImplementedError("write anagram_groups")
