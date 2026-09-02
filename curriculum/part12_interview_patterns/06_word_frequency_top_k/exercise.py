"""Top offenders in an error log.

Given the text of an error log, report the k most frequent words so the
on-call engineer sees at a glance whether it is "timeout", "certificate" or
"disk" that dominates. Write `word_frequency_top_k(text, k)` that returns a
list of `(word, count)` tuples.

Rules:
- lowercase the text first; "Timeout" and "timeout" are the same word
- a word is a maximal run of letters, digits and underscores (the regex
  `\\w+`); every other character separates words, so "disk-full" is two
  words and "mdmclient[512]:" contributes "mdmclient" and "512"
- order by count descending; equal counts are ordered alphabetically
- return at most k entries; when k is larger than the number of distinct
  words return them all
- k <= 0 or an empty/whitespace-only text gives an empty list

Complexity target: O(n) to count n words plus O(d log k) to pick the top k
of d distinct words, using collections.Counter and heapq (or a sort with a
key on (-count, word)). The last test has 5,050 words.

Examples:
    >>> word_frequency_top_k("Timeout waiting for MDM. timeout again; mdm down", 2)
    [('mdm', 2), ('timeout', 2)]
    >>> word_frequency_top_k("a b b c c c", 5)
    [('c', 3), ('b', 2), ('a', 1)]
"""
import re
from typing import List, Tuple


def word_frequency_top_k(text: str, k: int) -> List[Tuple[str, int]]:
    raise NotImplementedError("write word_frequency_top_k")
