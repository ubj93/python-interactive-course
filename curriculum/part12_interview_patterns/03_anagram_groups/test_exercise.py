import unittest

from exercise import anagram_groups


class TestAnagramGroups(unittest.TestCase):
    def test_example(self):
        """Groups the anagrams from the description"""
        self.assertEqual(
            anagram_groups(["listen", "silent", "google", "enlist"]),
            [["listen", "silent", "enlist"], ["google"]],
        )

    def test_singletons(self):
        """Names without anagrams form groups of one"""
        self.assertEqual(anagram_groups(["munki", "jamf", "osquery"]), [["munki"], ["jamf"], ["osquery"]])

    def test_group_order_by_first_appearance(self):
        """Groups are ordered by the first member's position"""
        self.assertEqual(
            anagram_groups(["bat", "tar", "rat", "tab", "art"]),
            [["bat", "tab"], ["tar", "rat", "art"]],
        )

    def test_case_and_characters_matter(self):
        """Different case or extra characters are not anagrams"""
        self.assertEqual(anagram_groups(["abc", "Abc", "ab-c", "c-ab"]), [["abc"], ["Abc"], ["ab-c", "c-ab"]])

    def test_duplicates_kept(self):
        """Repeated names stay together in one group"""
        self.assertEqual(anagram_groups(["app", "app", "ppa"]), [["app", "app", "ppa"]])

    def test_empty(self):
        """Empty input gives an empty list; empty names group together"""
        self.assertEqual(anagram_groups([]), [])
        self.assertEqual(anagram_groups(["", ""]), [["", ""]])

    def test_large_input(self):
        """5,000 names made of rotations of 25 base words"""
        bases = [f"pkg{c}{c}base" for c in "abcdefghijklmnopqrstuvwxy"]
        names = []
        i = 0
        while len(names) < 5000:
            base = bases[i % len(bases)]
            shift = (i // len(bases)) % len(base)
            names.append(base[shift:] + base[:shift])
            i += 1
        groups = anagram_groups(names)
        self.assertEqual(len(groups), 25)
        self.assertEqual(sum(len(g) for g in groups), 5000)
        self.assertEqual(groups[0][:2], ["pkgaabase", "kgaabasep"])
        for g in groups:
            keys = {"".join(sorted(name)) for name in g}
            self.assertEqual(len(keys), 1, g[:3])


if __name__ == "__main__":
    unittest.main()
