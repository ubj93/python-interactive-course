import unittest

from exercise import parse_flags


class TestParseFlags(unittest.TestCase):
    def test_no_args(self):
        """No arguments gives an empty dict"""
        self.assertEqual(parse_flags(), {})

    def test_bare_flags(self):
        """Flags without a value map to True"""
        self.assertEqual(parse_flags("--verbose", "--force"), {"verbose": True, "force": True})

    def test_key_value(self):
        """--key=value maps to a string value"""
        self.assertEqual(parse_flags("--target=mbp-j-doe", "--retries=3"), {"target": "mbp-j-doe", "retries": "3"})

    def test_mixed(self):
        """Flags and key=value pairs can be mixed in any order"""
        self.assertEqual(
            parse_flags("--verbose", "--target=nuc-01", "--dry-run"),
            {"verbose": True, "target": "nuc-01", "dry_run": True},
        )

    def test_value_containing_equals(self):
        """Only the first = splits; the rest belongs to the value"""
        self.assertEqual(parse_flags("--url=http://x/?a=b&c=d"), {"url": "http://x/?a=b&c=d"})
        self.assertEqual(parse_flags("--expr=a=b"), {"expr": "a=b"})

    def test_empty_value_and_hyphens(self):
        """--key= gives an empty string and hyphens in keys become underscores"""
        self.assertEqual(parse_flags("--note="), {"note": ""})
        self.assertEqual(parse_flags("--max-retry-count=2"), {"max_retry_count": "2"})

    def test_last_one_wins(self):
        """A repeated key keeps the last value, even changing type"""
        self.assertEqual(parse_flags("--retries=3", "--retries=5"), {"retries": "5"})
        self.assertEqual(parse_flags("--debug=no", "--debug"), {"debug": True})

    def test_invalid_arguments_raise(self):
        """Arguments without -- or with an empty key raise ValueError"""
        for bad in ["verbose", "-v", "--", "--=x", "install zoom"]:
            with self.assertRaises(ValueError, msg=bad):
                parse_flags(bad)


if __name__ == "__main__":
    unittest.main()
