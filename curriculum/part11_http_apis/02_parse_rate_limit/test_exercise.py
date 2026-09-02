import unittest

from exercise import RateLimit, parse_rate_limit, wait_seconds


class TestParseRateLimit(unittest.TestCase):
    def test_remaining_and_reset(self):
        """Remaining is an int and reset_in is seconds until the reset time"""
        rl = parse_rate_limit({"X-RateLimit-Remaining": "12", "X-RateLimit-Reset": "1000"}, now=940.0)
        self.assertEqual(rl, RateLimit(remaining=12, reset_in=60.0))
        self.assertIsInstance(rl.remaining, int)

    def test_case_insensitive_and_whitespace(self):
        """Header names match in any case and values may carry whitespace"""
        rl = parse_rate_limit({"x-ratelimit-remaining": " 3 ", "X-RATELIMIT-RESET": "1000 "}, now=990.0)
        self.assertEqual(rl, RateLimit(remaining=3, reset_in=10.0))

    def test_missing_headers(self):
        """Missing headers give None for both fields"""
        self.assertEqual(parse_rate_limit({}, now=0.0), RateLimit(None, None))
        self.assertEqual(parse_rate_limit({"Content-Type": "application/json"}, now=0.0), RateLimit(None, None))

    def test_non_numeric_values(self):
        """Garbage values are treated as missing"""
        rl = parse_rate_limit({"X-RateLimit-Remaining": "lots", "X-RateLimit-Reset": "soon"}, now=0.0)
        self.assertEqual(rl, RateLimit(None, None))

    def test_retry_after_wins(self):
        """Retry-After overrides the reset header"""
        rl = parse_rate_limit({"Retry-After": "30", "X-RateLimit-Reset": "1000", "X-RateLimit-Remaining": "0"}, now=940.0)
        self.assertEqual(rl, RateLimit(remaining=0, reset_in=30.0))

    def test_reset_in_past_clamped(self):
        """A reset time already behind now gives 0.0, never negative"""
        rl = parse_rate_limit({"X-RateLimit-Reset": "1000"}, now=1200.0)
        self.assertEqual(rl.reset_in, 0.0)


class TestWaitSeconds(unittest.TestCase):
    def test_wait_rules(self):
        """Wait on Retry-After or when nothing is left; otherwise 0.0"""
        self.assertEqual(wait_seconds({"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1000"}, now=940.0), 60.0)
        self.assertEqual(wait_seconds({"Retry-After": "7"}, now=0.0), 7.0)
        self.assertEqual(wait_seconds({"X-RateLimit-Remaining": "5", "X-RateLimit-Reset": "1000"}, now=940.0), 0.0)
        self.assertEqual(wait_seconds({"X-RateLimit-Remaining": "0"}, now=0.0), 0.0)
        self.assertEqual(wait_seconds({}, now=0.0), 0.0)


if __name__ == "__main__":
    unittest.main()
