import hashlib
import hmac
import unittest

from exercise import sign_payload, verify_webhook_signature

SECRET = "s3cret"
BODY = b'{"event":"device.enrolled","serial":"C02XG1234ABC"}'
T = 1714813200


def header(sig, t=T):
    return {"X-Signature": f"t={t},v1={sig}"}


class TestSignPayload(unittest.TestCase):
    def test_matches_hmac_sha256(self):
        """Signature is hex HMAC-SHA256 of '<t>.' + body under the secret"""
        want = hmac.new(b"s3cret", b"%d." % T + BODY, hashlib.sha256).hexdigest()
        self.assertEqual(sign_payload(SECRET, BODY, T), want)
        self.assertEqual(len(sign_payload(SECRET, BODY, T)), 64)

    def test_str_and_bytes_equivalent(self):
        """str inputs are encoded as UTF-8 and give the same signature as bytes"""
        self.assertEqual(sign_payload("s3cret", BODY.decode(), T), sign_payload(b"s3cret", BODY, T))
        self.assertNotEqual(sign_payload(SECRET, BODY, T), sign_payload(SECRET, BODY, T + 1))


class TestVerifyWebhookSignature(unittest.TestCase):
    def test_valid(self):
        """A freshly signed payload verifies"""
        h = header(sign_payload(SECRET, BODY, T))
        self.assertTrue(verify_webhook_signature(SECRET, BODY, h, now=T + 60))
        self.assertTrue(verify_webhook_signature(SECRET, BODY, h, now=T - 60))

    def test_tampered_body_or_wrong_secret(self):
        """Changing the body or using another secret fails"""
        h = header(sign_payload(SECRET, BODY, T))
        self.assertFalse(verify_webhook_signature(SECRET, BODY + b" ", h, now=T))
        self.assertFalse(verify_webhook_signature("other", BODY, h, now=T))

    def test_stale_timestamp(self):
        """A timestamp outside the tolerance window fails, on either side"""
        h = header(sign_payload(SECRET, BODY, T))
        self.assertFalse(verify_webhook_signature(SECRET, BODY, h, now=T + 301))
        self.assertFalse(verify_webhook_signature(SECRET, BODY, h, now=T - 301))
        self.assertTrue(verify_webhook_signature(SECRET, BODY, h, now=T + 300))
        self.assertTrue(verify_webhook_signature(SECRET, BODY, h, now=T + 20, tolerance=30))
        self.assertFalse(verify_webhook_signature(SECRET, BODY, h, now=T + 31, tolerance=30))

    def test_header_name_case_and_whitespace(self):
        """Header lookup is case-insensitive and spaces around pairs are fine"""
        sig = sign_payload(SECRET, BODY, T)
        self.assertTrue(verify_webhook_signature(SECRET, BODY, {"x-signature": f" t={T} , v1={sig} "}, now=T))

    def test_missing_or_malformed_header(self):
        """Missing or malformed headers give False, never an exception"""
        sig = sign_payload(SECRET, BODY, T)
        for headers in [
            {},
            {"X-Signature": ""},
            {"X-Signature": "garbage"},
            {"X-Signature": f"v1={sig}"},
            {"X-Signature": f"t=soon,v1={sig}"},
            {"X-Signature": f"t={T}"},
            {"X-Signature": f"t={T},v1=nothex"},
        ]:
            self.assertFalse(verify_webhook_signature(SECRET, BODY, headers, now=T), headers)

    def test_multiple_v1_any_match(self):
        """Several v1 values are accepted if any of them matches (secret rotation)"""
        good = sign_payload(SECRET, BODY, T)
        bad = sign_payload("retired", BODY, T)
        self.assertTrue(verify_webhook_signature(SECRET, BODY, {"X-Signature": f"t={T},v1={bad},v1={good}"}, now=T))
        self.assertFalse(verify_webhook_signature(SECRET, BODY, {"X-Signature": f"t={T},v1={bad},v1={bad}"}, now=T))


if __name__ == "__main__":
    unittest.main()
