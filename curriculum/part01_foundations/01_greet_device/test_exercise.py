import unittest

from exercise import greet_device


class TestGreetDevice(unittest.TestCase):
    def test_example(self):
        """Matches the example in the description"""
        self.assertEqual(
            greet_device("MBP-J-DOE", "macOS", 16),
            "Hello, MBP-J-DOE! You are running macOS with 16 GB of RAM.",
        )

    def test_other_values(self):
        """Works for a Windows box with 8 GB"""
        self.assertEqual(
            greet_device("win-lab-01", "Windows", 8),
            "Hello, win-lab-01! You are running Windows with 8 GB of RAM.",
        )

    def test_returns_a_string_not_prints(self):
        """Returns the string instead of printing it"""
        result = greet_device("x", "Linux", 1)
        self.assertIsInstance(result, str)
        self.assertFalse(result.endswith("\n"))


if __name__ == "__main__":
    unittest.main()
