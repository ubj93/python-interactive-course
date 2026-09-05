import random
import unittest

from exercise import two_sum


class TestTwoSum(unittest.TestCase):
    def test_example(self):
        """Finds the pair from the description"""
        self.assertEqual(two_sum([120, 40, 75, 60], 100), (1, 3))

    def test_no_pair(self):
        """Returns None when no two sizes add up to the target"""
        self.assertIsNone(two_sum([1, 2, 3], 100))

    def test_no_self_pairing(self):
        """An element cannot be paired with itself"""
        self.assertIsNone(two_sum([5, 3], 10))

    def test_equal_values_at_different_indexes(self):
        """Two equal values at different indexes are a valid pair"""
        self.assertEqual(two_sum([4, 4], 8), (0, 1))
        self.assertEqual(two_sum([1, 4, 2, 4], 8), (1, 3))

    def test_zero_and_negative(self):
        """Zero and negative sizes are ordinary values"""
        self.assertEqual(two_sum([0, 7, -7], 0), (1, 2))
        self.assertEqual(two_sum([3, 0], 3), (0, 1))

    def test_empty_and_single(self):
        """Empty list and single element give None"""
        self.assertIsNone(two_sum([], 0))
        self.assertIsNone(two_sum([9], 9))

    def test_any_valid_pair(self):
        """When several pairs match, the returned pair is valid and ordered"""
        sizes = [1, 9, 2, 8, 3, 7]
        result = two_sum(sizes, 10)
        self.assertIsInstance(result, tuple)
        i, j = result
        self.assertLess(i, j)
        self.assertEqual(sizes[i] + sizes[j], 10)

    def test_large_input(self):
        """20,000 sizes with one valid pair far apart (nested loop: seconds; dict: instant)"""
        n = 20000
        sizes = [2 * ((i * 7919) % 99991) + 2 for i in range(n - 1)] + [12345]
        target = sizes[5000] + sizes[-1]
        self.assertEqual(two_sum(sizes, target), (5000, n - 1))

    def test_generalization_seeded(self):
        """Generalization: varied sizes agree with a small all-pairs oracle (seed 1201)"""
        rng = random.Random(1201)
        cases = [([], 0), ([0], 0), ([0, 0, 0], 0), ([-9, -9], -18),
                 ([2 ** 60, 1, 2 ** 60 + 2], 2 ** 60 + 1),
                 ([2 ** 60, 2], 2 ** 60 + 1)]
        for case in range(80):
            sizes = [rng.randint(-25, 25) for _ in range(rng.randint(0, 18))]
            target = rng.randint(-50, 50)
            if len(sizes) >= 2 and case % 2 == 0:
                i, j = rng.sample(range(len(sizes)), 2)
                target = sizes[i] + sizes[j]
            cases.append((sizes, target))
        for sizes, target in cases:
            # Deliberately use the simple quadratic oracle only on small lists.
            pairs = {(i, j) for i in range(len(sizes)) for j in range(i + 1, len(sizes))
                     if sizes[i] + sizes[j] == target}
            result = two_sum(sizes[:], target)
            context = f"sizes={sizes!r}, target={target}"
            if not pairs:
                self.assertIsNone(result, context)
            else:
                self.assertIsInstance(result, tuple, context)
                self.assertEqual(len(result), 2, context)
                self.assertTrue(all(isinstance(index, int) for index in result), context)
                self.assertTrue(result in pairs, f"{context}; expected valid distinct indexes, got {result!r}")


if __name__ == "__main__":
    unittest.main()
