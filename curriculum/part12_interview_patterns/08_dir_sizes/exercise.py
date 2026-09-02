"""Total size of every folder in a tree.

A disk-usage report from a managed Mac arrives as a nested dict: keys are
names, a value is either an int (the size of a file in bytes) or another
dict (a subfolder). Write `dir_sizes(tree)` that returns a dict mapping
every folder path to its total size, counting every file beneath it at any
depth.

Rules:
- the root folder has the path "/"; its children are "/Applications",
  "/Users"; deeper folders join with "/" ("/Users/jdoe/Library")
- every folder appears in the result, including empty ones (size 0) and
  the root; files do not appear
- a folder's size includes the sizes of all its subfolders
- an empty tree gives {"/": 0}
- folder names never contain "/"; sizes are non-negative ints

Complexity target: O(number of files and folders), visiting each node once.
Recursion is the natural fit (the tests nest at most 200 deep, well under
Python's default recursion limit of 1,000), but know how you would rewrite
it with an explicit stack for a deeper tree. The last test has 3,061
folders.

Examples:
    >>> dir_sizes({"Applications": {"Safari.app": 300, "Utilities": {"Terminal.app": 50}}, "swapfile": 1000})
    {'/Applications/Utilities': 50, '/Applications': 350, '/': 1350}
    >>> dir_sizes({})
    {'/': 0}
"""
from typing import Dict, Union

Tree = Dict[str, Union[int, "Tree"]]


def dir_sizes(tree: Tree) -> Dict[str, int]:
    raise NotImplementedError("write dir_sizes")
