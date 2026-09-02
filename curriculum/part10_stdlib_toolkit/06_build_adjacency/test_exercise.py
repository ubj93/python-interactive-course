import unittest
from collections import defaultdict

from exercise import build_adjacency, neighbors


class TestBuildAdjacency(unittest.TestCase):
    def test_both_directions(self):
        """An edge appears in both nodes' neighbour sets"""
        adj = build_adjacency([("java8", "java11")])
        self.assertEqual(adj, {"java8": {"java11"}, "java11": {"java8"}})

    def test_chain(self):
        """A chain of edges builds the right sets"""
        adj = build_adjacency([("a", "b"), ("b", "c"), ("c", "d")])
        self.assertEqual(adj, {"a": {"b"}, "b": {"a", "c"}, "c": {"b", "d"}, "d": {"c"}})

    def test_duplicates_collapse(self):
        """The same edge in either direction is stored once"""
        adj = build_adjacency([("a", "b"), ("b", "a"), ("a", "b")])
        self.assertEqual(adj, {"a": {"b"}, "b": {"a"}})

    def test_isolated_nodes_and_self_loops(self):
        """Extra nodes and self-loops register the node with no neighbours"""
        adj = build_adjacency([("a", "b"), ("c", "c")], nodes=["d", "a"])
        self.assertEqual(adj, {"a": {"b"}, "b": {"a"}, "c": set(), "d": set()})

    def test_plain_dict(self):
        """Returns a real dict: unknown nodes raise KeyError instead of being created"""
        adj = build_adjacency([("a", "b")])
        self.assertIs(type(adj), dict)
        self.assertNotIsInstance(adj, defaultdict)
        with self.assertRaises(KeyError):
            adj["zzz"]
        self.assertEqual(set(adj), {"a", "b"})

    def test_empty_and_generator_input(self):
        """No edges gives {}; any iterable of pairs works, not only lists"""
        self.assertEqual(build_adjacency([]), {})
        adj = build_adjacency(((x, y) for x, y in [("a", "b")]))
        self.assertEqual(adj, {"a": {"b"}, "b": {"a"}})

    def test_neighbors_sorted_and_unknown(self):
        """neighbors returns a sorted list and [] for unknown nodes"""
        adj = build_adjacency([("java11", "java8"), ("java11", "java17"), ("java11", "corretto")])
        self.assertEqual(neighbors(adj, "java11"), ["corretto", "java17", "java8"])
        self.assertEqual(neighbors(adj, "nope"), [])


if __name__ == "__main__":
    unittest.main()
