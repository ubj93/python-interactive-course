import unittest

from exercise import mask_secrets


class TestMaskSecrets(unittest.TestCase):
    def test_password_kept_last_four(self):
        """All but the last four characters of a password become '*'"""
        self.assertEqual(mask_secrets("user=jdoe password=hunter2secret"), "user=jdoe password=*********cret")

    def test_no_secrets_unchanged(self):
        """Text without secrets is returned unchanged"""
        text = "user=jdoe host=mbp-1 status=ok"
        self.assertEqual(mask_secrets(text), text)
        self.assertEqual(mask_secrets(""), "")

    def test_short_values_fully_masked(self):
        """Values of four characters or fewer are masked completely"""
        self.assertEqual(mask_secrets("token=abcd"), "token=****")
        self.assertEqual(mask_secrets("secret=ab"), "secret=**")

    def test_bearer_token(self):
        """Bearer tokens keep the word Bearer and the last four characters"""
        self.assertEqual(
            mask_secrets("Authorization: Bearer abc123def456ghi7"),
            "Authorization: Bearer ************ghi7",
        )

    def test_key_case_and_separators(self):
        """Keys match case-insensitively with '=' or ':' and optional spaces"""
        self.assertEqual(mask_secrets("PASSWORD = hunter2secret"), "PASSWORD = *********cret")
        self.assertEqual(mask_secrets("Api_Key:sk-live-0123456789"), "Api_Key:**************6789")

    def test_value_stops_at_delimiters(self):
        """A value ends at whitespace, ';', ',' or '&'"""
        self.assertEqual(mask_secrets("passwd=abcdefgh;user=x"), "passwd=****efgh;user=x")
        self.assertEqual(mask_secrets("a=1&token=zyxwvuts&b=2"), "a=1&token=****vuts&b=2")

    def test_several_in_one_line(self):
        """Every secret on the line is masked, everything else preserved"""
        line = "login user=jdoe password=hunter2secret token=t0k3n-value-99 ok"
        self.assertEqual(line.count(" "), mask_secrets(line).count(" "))
        self.assertEqual(
            mask_secrets(line),
            "login user=jdoe password=*********cret token=**********e-99 ok",
        )

    def test_empty_value_left_alone(self):
        """A key with no value is not changed"""
        self.assertEqual(mask_secrets("user=jdoe password="), "user=jdoe password=")
        self.assertEqual(mask_secrets("password=;user=jdoe"), "password=;user=jdoe")


if __name__ == "__main__":
    unittest.main()
