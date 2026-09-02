import unittest

from exercise import LRUCache


class TestLRUCache(unittest.TestCase):
    def test_put_and_get(self):
        """Stored values come back; a missing key gives None"""
        cache = LRUCache(2)
        cache.put("a", 1)
        self.assertEqual(cache.get("a"), 1)
        self.assertIsNone(cache.get("b"))

    def test_len(self):
        """len() reports the number of entries, never above capacity"""
        cache = LRUCache(2)
        self.assertEqual(len(cache), 0)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        self.assertEqual(len(cache), 2)

    def test_evicts_least_recently_used(self):
        """Inserting into a full cache evicts the entry used longest ago"""
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        self.assertIsNone(cache.get("a"))
        self.assertEqual(cache.get("b"), 2)
        self.assertEqual(cache.get("c"), 3)

    def test_get_refreshes(self):
        """A get makes the key most recently used, so something else is evicted"""
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.get("a")
        cache.put("c", 3)
        self.assertEqual(cache.get("a"), 1)
        self.assertIsNone(cache.get("b"))

    def test_update_refreshes_without_evicting(self):
        """Updating an existing key changes its value, refreshes it and evicts nothing"""
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("a", 10)
        self.assertEqual(len(cache), 2)
        cache.put("c", 3)
        self.assertEqual(cache.get("a"), 10)
        self.assertIsNone(cache.get("b"))

    def test_capacity_one_and_invalid(self):
        """Capacity 1 keeps only the latest key; capacity < 1 raises ValueError"""
        cache = LRUCache(1)
        cache.put("a", 1)
        cache.put("b", 2)
        self.assertIsNone(cache.get("a"))
        self.assertEqual(cache.get("b"), 2)
        with self.assertRaises(ValueError):
            LRUCache(0)
        with self.assertRaises(ValueError):
            LRUCache(-5)

    def test_miss_does_not_refresh_or_insert(self):
        """A miss changes nothing: no entry is created and the order is unchanged"""
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.get("zzz")
        self.assertEqual(len(cache), 2)
        cache.put("c", 3)
        self.assertIsNone(cache.get("a"))
        self.assertEqual(cache.get("b"), 2)

    def test_large_sequence(self):
        """11,000 operations on a 1,000-entry cache with one refreshed survivor"""
        cache = LRUCache(1000)
        for i in range(10000):
            cache.put(i, i * 2)
        self.assertEqual(len(cache), 1000)
        self.assertIsNone(cache.get(8999))
        self.assertEqual(cache.get(9000), 18000)  # refresh the oldest survivor
        for i in range(10000, 10999):
            cache.put(i, i * 2)
        self.assertEqual(len(cache), 1000)
        self.assertEqual(cache.get(9000), 18000)
        self.assertIsNone(cache.get(9001))
        self.assertIsNone(cache.get(9999))
        self.assertEqual(cache.get(10000), 20000)
        self.assertEqual(cache.get(10998), 21996)


if __name__ == "__main__":
    unittest.main()
