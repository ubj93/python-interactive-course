import unittest
from itertools import count, islice

from exercise import batched


class TestBatched(unittest.TestCase):
    def test_exact_batches(self):
        """Input that divides evenly gives equal tuples"""
        self.assertEqual(list(batched(["a", "b", "c", "d"], 2)), [("a", "b"), ("c", "d")])

    def test_last_batch_shorter(self):
        """The final batch holds the leftovers"""
        self.assertEqual(list(batched([1, 2, 3, 4, 5], 2)), [(1, 2), (3, 4), (5,)])
        self.assertEqual(list(batched("abc", 5)), [("a", "b", "c")])

    def test_empty_input(self):
        """An empty input yields no batches"""
        self.assertEqual(list(batched([], 3)), [])
        self.assertEqual(list(batched(iter(()), 1)), [])

    def test_returns_an_iterator_of_tuples(self):
        """The result is lazy (has __next__) and each batch is a tuple, not a list"""
        result = batched([1, 2, 3], 2)
        self.assertNotIsInstance(result, (list, tuple))
        self.assertTrue(hasattr(result, "__next__"))
        first = next(result)
        self.assertIsInstance(first, tuple)
        self.assertEqual(first, (1, 2))

    def test_works_on_one_shot_iterators(self):
        """A generator or iterator input is consumed once, in order"""
        gen = (s for s in ["C02A", "C02B", "C02C"])
        self.assertEqual(list(batched(gen, 2)), [("C02A", "C02B"), ("C02C",)])
        self.assertEqual(list(batched(iter(range(3)), 1)), [(0,), (1,), (2,)])

    def test_is_lazy_on_infinite_input(self):
        """Only the requested batches are pulled from an infinite iterator"""
        self.assertEqual(list(islice(batched(count(1), 3), 2)), [(1, 2, 3), (4, 5, 6)])
        source = iter(range(100))
        batches = batched(source, 10)
        next(batches)
        self.assertEqual(next(source), 10)

    def test_invalid_n_raises_at_call_time(self):
        """n < 1 raises ValueError immediately, without iterating"""
        with self.assertRaises(ValueError):
            batched([1, 2, 3], 0)
        with self.assertRaises(ValueError):
            batched([], -1)


if __name__ == "__main__":
    unittest.main()
