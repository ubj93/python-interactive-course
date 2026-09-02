import unittest

from exercise import most_common_with_ties

APPS = ["Slack", "Zoom", "Slack", "Chrome", "Zoom", "Firefox", "Slack"]


class TestMostCommonWithTies(unittest.TestCase):
    def test_top_n(self):
        """Returns the n most frequent items with their counts"""
        self.assertEqual(most_common_with_ties(APPS, 2), [("Slack", 3), ("Zoom", 2)])

    def test_ties_alphabetical(self):
        """Equal counts are ordered by name, whatever the input order"""
        a = most_common_with_ties(["Zoom", "Chrome", "Zoom", "Chrome"], 2)
        b = most_common_with_ties(["Chrome", "Zoom", "Chrome", "Zoom"], 2)
        self.assertEqual(a, [("Chrome", 2), ("Zoom", 2)])
        self.assertEqual(a, b)

    def test_n_larger_than_distinct(self):
        """Asking for more than there are gives everything, still ordered"""
        self.assertEqual(
            most_common_with_ties(APPS, 10),
            [("Slack", 3), ("Zoom", 2), ("Chrome", 1), ("Firefox", 1)],
        )

    def test_include_ties_extends(self):
        """include_ties pulls in every item tied with the n-th one"""
        self.assertEqual(
            most_common_with_ties(APPS, 3, include_ties=True),
            [("Slack", 3), ("Zoom", 2), ("Chrome", 1), ("Firefox", 1)],
        )
        self.assertEqual(most_common_with_ties(APPS, 3), [("Slack", 3), ("Zoom", 2), ("Chrome", 1)])

    def test_include_ties_no_tie_at_boundary(self):
        """include_ties changes nothing when the n-th entry is not tied"""
        self.assertEqual(most_common_with_ties(APPS, 2, include_ties=True), [("Slack", 3), ("Zoom", 2)])

    def test_empty_and_nonpositive_n(self):
        """Empty input or n <= 0 gives []"""
        self.assertEqual(most_common_with_ties([], 3), [])
        self.assertEqual(most_common_with_ties(APPS, 0), [])
        self.assertEqual(most_common_with_ties(APPS, -1, include_ties=True), [])

    def test_accepts_generator(self):
        """Any iterable works, not only lists"""
        gen = (a for a in APPS)
        self.assertEqual(most_common_with_ties(gen, 1), [("Slack", 3)])


if __name__ == "__main__":
    unittest.main()
