import unittest

from exercise import balanced_brackets


class TestBalancedBrackets(unittest.TestCase):
    def test_simple_pairs(self):
        """Single pairs of each kind are balanced"""
        for s in ["()", "[]", "{}", "()[]{}"]:
            self.assertTrue(balanced_brackets(s), s)

    def test_nested(self):
        """Properly nested brackets are balanced"""
        self.assertTrue(balanced_brackets("{[()]}"))
        self.assertTrue(balanced_brackets("([]{()})"))

    def test_ignores_other_characters(self):
        """Letters, quotes and shell syntax are ignored"""
        self.assertTrue(balanced_brackets('if [ -f "$f" ]; then echo "${f}"; fi'))
        self.assertTrue(balanced_brackets("echo hello | grep -c 'x'"))

    def test_wrong_kind(self):
        """A closer of the wrong kind is unbalanced"""
        self.assertFalse(balanced_brackets("(]"))
        self.assertFalse(balanced_brackets("([)]"))

    def test_closer_with_nothing_open(self):
        """A closing bracket before any opener is unbalanced"""
        self.assertFalse(balanced_brackets(")("))
        self.assertFalse(balanced_brackets("]"))

    def test_left_open(self):
        """Brackets still open at the end are unbalanced"""
        self.assertFalse(balanced_brackets("(("))
        self.assertFalse(balanced_brackets("{[()]"))

    def test_empty(self):
        """Empty text is balanced"""
        self.assertTrue(balanced_brackets(""))

    def test_large_input(self):
        """A 60,000-character line nested 5,000 deep, balanced and then broken"""
        deep = "([{" * 5000 + "}])" * 5000
        line = "x" * 15000 + deep + "y" * 15000
        self.assertTrue(balanced_brackets(line))
        self.assertFalse(balanced_brackets(line + ")"))
        self.assertFalse(balanced_brackets("x" * 15000 + deep[:-1] + "y" * 15000))


if __name__ == "__main__":
    unittest.main()
