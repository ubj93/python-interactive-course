"""Reference solutions for build_adjacency / neighbors."""
from collections import defaultdict
from typing import Dict, Iterable, List, Set, Tuple


# Best practice: defaultdict(set) means every "adj[x].add(y)" just works, and touching
# adj[a] and adj[b] for a self-loop registers the node with an empty set. dict(adj) at the
# end freezes it so callers get KeyError, not phantom nodes.
def build_adjacency(edges: Iterable[Tuple[str, str]], nodes: Iterable[str] = ()) -> Dict[str, Set[str]]:
    adj: Dict[str, Set[str]] = defaultdict(set)
    for node in nodes:
        adj[node]
    for a, b in edges:
        adj[a]
        adj[b]
        if a != b:
            adj[a].add(b)
            adj[b].add(a)
    return dict(adj)


# dict.get with a default avoids the KeyError; sorted() turns the set into a stable list.
def neighbors(adj: Dict[str, Set[str]], node: str) -> List[str]:
    return sorted(adj.get(node, ()))


# Clever: setdefault does the same job without importing defaultdict, and the result is a
# plain dict from the start. Slightly noisier, but you will see it in older code.
def build_adjacency_setdefault(edges: Iterable[Tuple[str, str]], nodes: Iterable[str] = ()) -> Dict[str, Set[str]]:
    adj: Dict[str, Set[str]] = {}
    for node in nodes:
        adj.setdefault(node, set())
    for a, b in edges:
        adj.setdefault(a, set())
        adj.setdefault(b, set())
        if a != b:
            adj[a].add(b)
            adj[b].add(a)
    return adj
