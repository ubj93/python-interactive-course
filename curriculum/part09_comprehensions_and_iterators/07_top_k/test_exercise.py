import unittest
from operator import itemgetter

from exercise import top_k

USAGE = [("mbp-j-doe", 0.91), ("win-lab-01", 0.42), ("mbp-a-lee", 0.97), ("srv-01", 0.91), ("win-lab-02", 0.10)]


class TestTopK(unittest.TestCase):
    def test_basic(self):
        """The k items with the largest keys, largest first"""
        self.assertEqual(top_k(USAGE, 2, key=itemgetter(1)), [("mbp-a-lee", 0.97), ("mbp-j-doe", 0.91)])

    def test_k_covers_everything(self):
        """k equal to or larger than the input returns all items, ordered"""
        expected = [("mbp-a-lee", 0.97), ("mbp-j-doe", 0.91), ("srv-01", 0.91), ("win-lab-01", 0.42), ("win-lab-02", 0.10)]
        self.assertEqual(top_k(USAGE, 5, key=itemgetter(1)), expected)
        self.assertEqual(top_k(USAGE, 50, key=itemgetter(1)), expected)

    def test_k_zero_or_negative(self):
        """k <= 0 gives an empty list"""
        self.assertEqual(top_k(USAGE, 0, key=itemgetter(1)), [])
        self.assertEqual(top_k(USAGE, -3, key=itemgetter(1)), [])
        self.assertEqual(top_k([], 3, key=itemgetter(1)), [])

    def test_ties_keep_input_order(self):
        """Items with equal keys appear in their original order"""
        rows = [("d", 5), ("a", 7), ("c", 5), ("b", 7), ("e", 5)]
        self.assertEqual(top_k(rows, 4, key=itemgetter(1)), [("a", 7), ("b", 7), ("d", 5), ("c", 5)])

    def test_key_over_dicts_and_strings(self):
        """Any key function works: dict fields, and string keys"""
        devices = [{"name": "a", "ram": 8}, {"name": "b", "ram": 64}, {"name": "c", "ram": 16}]
        self.assertEqual([d["name"] for d in top_k(devices, 2, key=lambda d: d["ram"])], ["b", "c"])
        self.assertEqual(top_k(["14.5", "14.10", "13.6"], 1, key=lambda s: tuple(int(p) for p in s.split("."))), ["14.10"])

    def test_generator_input(self):
        """A one-shot generator is accepted and consumed once"""
        gen = ((f"host-{i}", (i * 7) % 11) for i in range(20))
        result = top_k(gen, 3, key=itemgetter(1))
        self.assertEqual([r[1] for r in result], [10, 10, 9])
        self.assertEqual([r[0] for r in result], ["host-3", "host-14", "host-6"])

    def test_does_not_mutate_input(self):
        """The input list is left in its original order"""
        rows = list(USAGE)
        top_k(rows, 3, key=itemgetter(1))
        self.assertEqual(rows, USAGE)


if __name__ == "__main__":
    unittest.main()
