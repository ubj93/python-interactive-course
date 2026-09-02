import unittest

from exercise import chunk_serials


class TestChunkSerials(unittest.TestCase):
    def test_even_split(self):
        """A list that divides evenly gives equal batches and no empty tail"""
        self.assertEqual(chunk_serials(["A", "B", "C", "D"], 2), [["A", "B"], ["C", "D"]])

    def test_last_batch_shorter(self):
        """The last batch holds the remainder"""
        self.assertEqual(chunk_serials(["A", "B", "C", "D", "E"], 2), [["A", "B"], ["C", "D"], ["E"]])
        self.assertEqual(chunk_serials(list("ABCDEFG"), 3), [["A", "B", "C"], ["D", "E", "F"], ["G"]])

    def test_size_larger_than_list(self):
        """A size bigger than the list gives one batch with everything"""
        self.assertEqual(chunk_serials(["A", "B"], 10), [["A", "B"]])

    def test_size_one(self):
        """Size 1 wraps every item in its own list"""
        self.assertEqual(chunk_serials(["A", "B", "C"], 1), [["A"], ["B"], ["C"]])

    def test_empty_input(self):
        """An empty list gives no batches at all"""
        self.assertEqual(chunk_serials([], 3), [])

    def test_invalid_size_raises(self):
        """Size 0 or negative raises ValueError"""
        with self.assertRaises(ValueError):
            chunk_serials(["A"], 0)
        with self.assertRaises(ValueError):
            chunk_serials(["A"], -2)

    def test_input_not_modified(self):
        """The original list is untouched and batches are independent copies"""
        serials = ["A", "B", "C"]
        batches = chunk_serials(serials, 2)
        batches[0].append("Z")
        self.assertEqual(serials, ["A", "B", "C"])


if __name__ == "__main__":
    unittest.main()
