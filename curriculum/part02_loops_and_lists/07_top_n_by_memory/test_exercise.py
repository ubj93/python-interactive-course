import unittest

from exercise import top_n_by_memory

FLEET = [
    {"hostname": "nuc-01", "memory_gb": 16},
    {"hostname": "mbp-j-doe", "memory_gb": 32},
    {"hostname": "mbp-a-kim", "memory_gb": 32},
    {"hostname": "win-lab-01", "memory_gb": 8},
    {"hostname": "mac-mini-02", "memory_gb": 64},
]


class TestTopNByMemory(unittest.TestCase):
    def test_top_one(self):
        """The single biggest machine comes first"""
        self.assertEqual(top_n_by_memory(FLEET, 1), ["mac-mini-02"])

    def test_sorted_descending(self):
        """Hostnames come back in descending memory order"""
        self.assertEqual(top_n_by_memory(FLEET, 5), ["mac-mini-02", "mbp-a-kim", "mbp-j-doe", "nuc-01", "win-lab-01"])

    def test_ties_by_hostname(self):
        """Equal memory is ordered by hostname ascending"""
        self.assertEqual(top_n_by_memory(FLEET, 3), ["mac-mini-02", "mbp-a-kim", "mbp-j-doe"])
        tied = [{"hostname": "zed", "memory_gb": 8}, {"hostname": "amy", "memory_gb": 8}, {"hostname": "kim", "memory_gb": 8}]
        self.assertEqual(top_n_by_memory(tied, 2), ["amy", "kim"])

    def test_n_larger_than_fleet(self):
        """Asking for more than exist returns everything, still sorted"""
        self.assertEqual(top_n_by_memory(FLEET, 100), ["mac-mini-02", "mbp-a-kim", "mbp-j-doe", "nuc-01", "win-lab-01"])

    def test_n_zero_or_negative(self):
        """n of 0 or less gives an empty list"""
        self.assertEqual(top_n_by_memory(FLEET, 0), [])
        self.assertEqual(top_n_by_memory(FLEET, -3), [])

    def test_empty_fleet(self):
        """An empty fleet gives an empty list"""
        self.assertEqual(top_n_by_memory([], 3), [])

    def test_missing_memory_counts_as_zero(self):
        """Missing or None memory sorts as 0 GB"""
        fleet = [
            {"hostname": "unknown-1"},
            {"hostname": "small", "memory_gb": 4},
            {"hostname": "unknown-2", "memory_gb": None},
        ]
        self.assertEqual(top_n_by_memory(fleet, 3), ["small", "unknown-1", "unknown-2"])

    def test_input_not_reordered(self):
        """The input list keeps its original order"""
        fleet = [dict(d) for d in FLEET]
        top_n_by_memory(fleet, 2)
        self.assertEqual([d["hostname"] for d in fleet], [d["hostname"] for d in FLEET])


if __name__ == "__main__":
    unittest.main()
