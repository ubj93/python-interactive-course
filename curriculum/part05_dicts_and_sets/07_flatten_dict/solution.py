"""Reference solutions for flatten_dict and unflatten_dict."""
from typing import Any, Dict


# Best practice: recursion with an accumulator and a prefix. "Is it a non-empty dict?"
# is the recurse test, so an empty dict falls through to the leaf branch as the spec wants.
def flatten_dict(d: Dict[str, Any], sep: str = ".") -> Dict[str, Any]:
    flat: Dict[str, Any] = {}

    def walk(node: Dict[str, Any], prefix: str) -> None:
        for key, value in node.items():
            path = f"{prefix}{sep}{key}" if prefix else key
            if isinstance(value, dict) and value:
                walk(value, path)
            else:
                flat[path] = value

    walk(d, "")
    return flat


# Best practice: walk down the parts of each key, creating dicts as needed. A conflict is
# meeting a non-dict where a dict is needed (leaf then prefix), or a dict where the leaf
# goes (prefix then leaf). Both checks are explicit so the error is raised in either order.
def unflatten_dict(flat: Dict[str, Any], sep: str = ".") -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in flat.items():
        *parents, last = key.split(sep)
        node = result
        for part in parents:
            child = node.setdefault(part, {})
            if not isinstance(child, dict):
                raise ValueError(f"key {key!r} conflicts with leaf {part!r}")
            node = child
        if isinstance(node.get(last), dict) and node[last]:
            raise ValueError(f"key {key!r} conflicts with nested keys under it")
        node[last] = value
    return result


# Clever: a generator version of flatten. yield from makes the recursion a one-liner per
# branch and dict() collects the pairs; the same walker powers a "print all paths" tool.
def flatten_dict_generator(d: Dict[str, Any], sep: str = ".") -> Dict[str, Any]:
    def pairs(node: Dict[str, Any], prefix: str):
        for key, value in node.items():
            path = f"{prefix}{sep}{key}" if prefix else key
            if isinstance(value, dict) and value:
                yield from pairs(value, path)
            else:
                yield path, value

    return dict(pairs(d, ""))
