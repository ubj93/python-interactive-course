import unittest

from exercise import build_headers, build_url


class TestBuildHeaders(unittest.TestCase):
    def test_with_token(self):
        """A token becomes a Bearer Authorization header alongside the defaults"""
        self.assertEqual(
            build_headers("abc123"),
            {"Accept": "application/json", "User-Agent": "cpe-tools/1.0", "Authorization": "Bearer abc123"},
        )

    def test_none_or_blank_token_omitted(self):
        """None or a blank token produces no Authorization key at all"""
        for token in (None, "", "   "):
            headers = build_headers(token)
            self.assertNotIn("Authorization", headers, repr(token))
            self.assertEqual(headers["Accept"], "application/json")

    def test_token_is_stripped(self):
        """Whitespace around the token is removed"""
        self.assertEqual(build_headers("  abc123\n")["Authorization"], "Bearer abc123")

    def test_extra_overrides_and_is_not_mutated(self):
        """extra wins over defaults, and the caller's dict and the result are independent"""
        extra = {"Accept": "text/csv", "X-Request-Id": "r1"}
        headers = build_headers("t", extra)
        self.assertEqual(headers["Accept"], "text/csv")
        self.assertEqual(headers["X-Request-Id"], "r1")
        self.assertEqual(headers["Authorization"], "Bearer t")
        self.assertEqual(extra, {"Accept": "text/csv", "X-Request-Id": "r1"})
        headers["Accept"] = "changed"
        self.assertEqual(build_headers("t")["Accept"], "application/json")


class TestBuildUrl(unittest.TestCase):
    def test_single_slash_join(self):
        """Exactly one slash between base and path regardless of input slashes"""
        want = "https://mdm.example.com/api/v1/devices"
        self.assertEqual(build_url("https://mdm.example.com/api", "v1/devices"), want)
        self.assertEqual(build_url("https://mdm.example.com/api/", "/v1/devices"), want)
        self.assertEqual(build_url("https://mdm.example.com/api", "/v1/devices"), want)

    def test_params_encoded(self):
        """Params are urlencoded in order; None values are dropped"""
        url = build_url("https://x.io", "devices", {"limit": 50, "q": "mbp lab", "cursor": None})
        self.assertEqual(url, "https://x.io/devices?limit=50&q=mbp+lab")

    def test_list_values_repeat_and_empty_params(self):
        """Lists repeat the key; empty or all-None params add no '?'"""
        self.assertEqual(
            build_url("https://x.io", "devices", {"status": ["active", "stale"]}),
            "https://x.io/devices?status=active&status=stale",
        )
        self.assertEqual(build_url("https://x.io", "devices"), "https://x.io/devices")
        self.assertEqual(build_url("https://x.io", "devices", {}), "https://x.io/devices")
        self.assertEqual(build_url("https://x.io", "devices", {"cursor": None}), "https://x.io/devices")


if __name__ == "__main__":
    unittest.main()
