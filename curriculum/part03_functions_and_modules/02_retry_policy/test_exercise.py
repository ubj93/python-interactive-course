import unittest

from exercise import retry_policy

EXPECTED_DEFAULTS = {
    "max_attempts": 3,
    "base_delay": 1.0,
    "max_delay": 30.0,
    "backoff": 2.0,
    "retry_on": (429, 500, 502, 503, 504),
}


class TestRetryPolicy(unittest.TestCase):
    def test_defaults(self):
        """No overrides gives the documented defaults"""
        self.assertEqual(retry_policy(), EXPECTED_DEFAULTS)

    def test_single_override(self):
        """One override changes only that key"""
        policy = retry_policy(max_attempts=5)
        self.assertEqual(policy["max_attempts"], 5)
        self.assertEqual(policy["base_delay"], 1.0)
        self.assertEqual(set(policy), set(EXPECTED_DEFAULTS))

    def test_several_overrides(self):
        """Several overrides are all applied"""
        policy = retry_policy(base_delay=0.5, max_delay=8.0, backoff=1.5)
        self.assertEqual((policy["base_delay"], policy["max_delay"], policy["backoff"]), (0.5, 8.0, 1.5))

    def test_retry_on_normalised(self):
        """retry_on accepts any iterable and is stored as a sorted tuple without duplicates"""
        self.assertEqual(retry_policy(retry_on=[503, 429, 503])["retry_on"], (429, 503))
        self.assertEqual(retry_policy(retry_on={500, 429})["retry_on"], (429, 500))
        self.assertEqual(retry_policy(retry_on=range(500, 503))["retry_on"], (500, 501, 502))
        self.assertEqual(retry_policy(retry_on=[])["retry_on"], ())

    def test_unknown_key_raises_type_error(self):
        """A misspelled or unknown key raises TypeError naming the key"""
        with self.assertRaises(TypeError) as ctx:
            retry_policy(max_attemps=5)
        self.assertIn("max_attemps", str(ctx.exception))

    def test_invalid_values_raise_value_error(self):
        """Out-of-range values raise ValueError"""
        for bad in [dict(max_attempts=0), dict(max_attempts=2.5), dict(base_delay=-1), dict(max_delay=-0.1),
                    dict(base_delay=5, max_delay=2), dict(backoff=0.5)]:
            with self.assertRaises(ValueError, msg=str(bad)):
                retry_policy(**bad)

    def test_boundary_values_accepted(self):
        """The edges of the valid ranges are accepted"""
        policy = retry_policy(max_attempts=1, base_delay=0, max_delay=0, backoff=1)
        self.assertEqual((policy["max_attempts"], policy["base_delay"], policy["max_delay"], policy["backoff"]), (1, 0, 0, 1))

    def test_results_are_independent(self):
        """Modifying one policy does not change the defaults or later policies"""
        first = retry_policy()
        first["max_attempts"] = 99
        first["extra"] = True
        self.assertEqual(retry_policy(), EXPECTED_DEFAULTS)


if __name__ == "__main__":
    unittest.main()
