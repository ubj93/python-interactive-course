import unittest

from exercise import word_frequency_top_k


class TestWordFrequencyTopK(unittest.TestCase):
    def test_basic(self):
        """Counts words and returns the most frequent first"""
        self.assertEqual(word_frequency_top_k("a b b c c c", 5), [("c", 3), ("b", 2), ("a", 1)])

    def test_case_insensitive(self):
        """Words are lowercased before counting"""
        self.assertEqual(word_frequency_top_k("Timeout TIMEOUT timeout", 1), [("timeout", 3)])

    def test_ties_alphabetical(self):
        """Equal counts are ordered alphabetically"""
        self.assertEqual(
            word_frequency_top_k("Timeout waiting for MDM. timeout again; mdm down", 2),
            [("mdm", 2), ("timeout", 2)],
        )
        self.assertEqual(word_frequency_top_k("zeta alpha beta", 3), [("alpha", 1), ("beta", 1), ("zeta", 1)])

    def test_punctuation_splits_words(self):
        """Punctuation and brackets separate words; digits count as words"""
        self.assertEqual(
            word_frequency_top_k("mdmclient[512]: disk-full, disk-full!", 4),
            [("disk", 2), ("full", 2), ("512", 1), ("mdmclient", 1)],
        )

    def test_k_larger_than_distinct(self):
        """k beyond the number of distinct words returns them all"""
        self.assertEqual(word_frequency_top_k("x y x", 10), [("x", 2), ("y", 1)])

    def test_k_zero_and_empty_text(self):
        """k <= 0 or empty text gives an empty list"""
        self.assertEqual(word_frequency_top_k("a b c", 0), [])
        self.assertEqual(word_frequency_top_k("a b c", -3), [])
        self.assertEqual(word_frequency_top_k("", 3), [])
        self.assertEqual(word_frequency_top_k("   \n\t ", 3), [])

    def test_large_input(self):
        """5,050 interleaved words where word wNN appears NN times"""
        words = [f"w{i}" for r in range(100) for i in range(r + 1, 101)]
        text = " ".join(words)
        self.assertEqual(len(words), 5050)
        self.assertEqual(word_frequency_top_k(text, 3), [("w100", 100), ("w99", 99), ("w98", 98)])
        bottom = word_frequency_top_k(text, 100)[-3:]
        self.assertEqual(bottom, [("w3", 3), ("w2", 2), ("w1", 1)])


if __name__ == "__main__":
    unittest.main()
