import unittest

from exercise import parse_port


class TestParsePort(unittest.TestCase):
    def test_valid_strings(self):
        """Digit strings with whitespace and leading zeros parse"""
        self.assertEqual(parse_port("8080"), 8080)
        self.assertEqual(parse_port(" 443 "), 443)
        self.assertEqual(parse_port("080"), 80)
        self.assertEqual(parse_port("65535"), 65535)
        self.assertEqual(parse_port("1"), 1)

    def test_valid_ints(self):
        """Ints in range are returned unchanged"""
        self.assertEqual(parse_port(22), 22)
        self.assertEqual(parse_port(65535), 65535)

    def test_empty_string(self):
        """Empty or whitespace-only strings raise 'port is empty'"""
        for s in ["", "   ", "\t\n"]:
            with self.assertRaises(ValueError, msg=repr(s)) as cm:
                parse_port(s)
            self.assertIn("empty", str(cm.exception))

    def test_non_digit_strings_name_the_input(self):
        """Non-digit text raises ValueError whose message quotes the input"""
        for s in ["80a", "-1", "+80", "8.0", "8 0", "http"]:
            with self.assertRaises(ValueError, msg=repr(s)) as cm:
                parse_port(s)
            self.assertIn(repr(s.strip()), str(cm.exception), s)
            self.assertNotIn("out of range", str(cm.exception), s)

    def test_out_of_range_names_the_number(self):
        """Out-of-range values raise ValueError mentioning the number"""
        for value in ["0", "65536", "70000", 0, -5, 100000]:
            with self.assertRaises(ValueError, msg=repr(value)) as cm:
                parse_port(value)
            message = str(cm.exception)
            self.assertIn("out of range", message, value)
            self.assertIn(str(int(value)), message, value)

    def test_wrong_type_raises_type_error(self):
        """None, floats, bools and lists raise TypeError naming the type"""
        for value, name in [(None, "NoneType"), (8.0, "float"), (True, "bool"), ([80], "list")]:
            with self.assertRaises(TypeError, msg=repr(value)) as cm:
                parse_port(value)
            self.assertIn(name, str(cm.exception), value)


if __name__ == "__main__":
    unittest.main()
