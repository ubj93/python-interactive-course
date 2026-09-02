"""Package conflicts as an undirected graph.

Our package catalog lists conflicts as pairs: ("java8", "java11") means the two
cannot be installed together. Conflicts are symmetric, so this is an undirected
graph. Write `build_adjacency(edges, nodes=())` that returns a plain dict mapping
every node to the set of its neighbours, and `neighbors(adj, node)`.

Rules for build_adjacency:
- every node named in any edge, or listed in `nodes`, is a key, even when it has
  no neighbours (empty set)
- each edge adds both directions: a in adj[b] and b in adj[a]
- duplicate edges, in either direction, are recorded once (sets do this for you)
- a self-loop ("x", "x") registers the node but adds no neighbour
- `edges` is any iterable of 2-tuples; empty input gives {}
- return a real `dict`, not a defaultdict: looking up an unknown node must raise
  KeyError instead of silently creating it. `collections.defaultdict(set)` is the
  right tool while building; convert before returning.

Rules for neighbors:
- returns the sorted list of neighbours of `node`
- returns [] for a node that is not in the graph (no KeyError here)

Examples:
    >>> adj = build_adjacency([("java8", "java11"), ("java11", "java17"), ("java8", "java11")])
    >>> adj == {"java8": {"java11"}, "java11": {"java8", "java17"}, "java17": {"java11"}}
    True
    >>> neighbors(adj, "java11")
    ['java17', 'java8']
"""
from collections import defaultdict
from typing import Dict, Iterable, List, Set, Tuple


def build_adjacency(edges: Iterable[Tuple[str, str]], nodes: Iterable[str] = ()) -> Dict[str, Set[str]]:
    raise NotImplementedError("write build_adjacency")


def neighbors(adj: Dict[str, Set[str]], node: str) -> List[str]:
    raise NotImplementedError("write neighbors")
