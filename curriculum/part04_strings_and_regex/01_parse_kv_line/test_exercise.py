import unittest

from exercise import parse_kv_line


class TestParseKvLine(unittest.TestCase):
    def test_simple(self):
        """Splits fields on ';' and pairs on '='"""
        self.assertEqual(parse_kv_line("a=1;b=2"), {"a": "1", "b": "2"})

    def test_whitespace_tolerant(self):
        """Strips spaces and tabs around keys and values"""
        self.assertEqual(
            parse_kv_line("serial=C02XG1234ABC; os = macOS 14.5 ;\tmanaged=true"),
            {"serial": "C02XG1234ABC", "os": "macOS 14.5", "managed": "true"},
        )

    def test_empty_fields_skipped(self):
        """Trailing and doubled semicolons do not produce entries"""
        self.assertEqual(parse_kv_line("a=1;;b=2; ;"), {"a": "1", "b": "2"})

    def test_value_may_contain_equals(self):
        """Only the first '=' separates key from value"""
        self.assertEqual(parse_kv_line("token=abc=def; x=1"), {"token": "abc=def", "x": "1"})

    def test_empty_value_allowed(self):
        """A key with nothing after '=' maps to an empty string"""
        self.assertEqual(parse_kv_line("note=; a=1"), {"note": "", "a": "1"})

    def test_later_key_wins(self):
        """Duplicate keys keep the last value"""
        self.assertEqual(parse_kv_line("os=macOS; os=Windows"), {"os": "Windows"})

    def test_blank_line(self):
        """Empty and whitespace-only lines give an empty dict"""
        self.assertEqual(parse_kv_line(""), {})
        self.assertEqual(parse_kv_line(" \t "), {})

    def test_malformed_raises(self):
        """A field without '=' or with an empty key raises ValueError"""
        with self.assertRaises(ValueError):
            parse_kv_line("a=1; broken")
        with self.assertRaises(ValueError):
            parse_kv_line("=1")


if __name__ == "__main__":
    unittest.main()
