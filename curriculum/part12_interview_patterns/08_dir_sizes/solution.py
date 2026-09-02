"""Reference solutions for dir_sizes."""
from typing import Dict, List, Tuple, Union

Tree = Dict[str, Union[int, "Tree"]]


# Best practice: a recursive helper that returns the size of the folder it was given
# and records it in the shared result dict. Note `out=None`, never `out={}`: a mutable
# default argument would be shared between calls.
# Time O(nodes), space O(depth) for the call stack plus O(folders) for the result.
def dir_sizes(tree: Tree) -> Dict[str, int]:
    out: Dict[str, int] = {}

    def walk(node: Tree, path: str) -> int:
        total = 0
        for name, child in node.items():
            if isinstance(child, dict):
                total += walk(child, path.rstrip("/") + "/" + name)
            else:
                total += child
        out[path] = total
        return total

    walk(tree, "/")
    return out


# Alternative: iterative post-order with an explicit stack, for trees deeper than the
# recursion limit. First pass collects folders parent-first; second pass sums them
# child-first so each parent adds already-complete child totals.
# Time O(nodes), space O(folders); no call-stack limit.
def dir_sizes_iterative(tree: Tree) -> Dict[str, int]:
    order: List[Tuple[str, str, Tree]] = []  # (path, parent_path, node), parents before children
    stack: List[Tuple[str, str, Tree]] = [("/", "", tree)]
    while stack:
        path, parent, node = stack.pop()
        order.append((path, parent, node))
        for name, child in node.items():
            if isinstance(child, dict):
                stack.append((path.rstrip("/") + "/" + name, path, child))
    out: Dict[str, int] = {path: 0 for path, _, _ in order}
    for path, parent, node in reversed(order):
        out[path] += sum(v for v in node.values() if not isinstance(v, dict))
        if parent:
            out[parent] += out[path]
    return out
