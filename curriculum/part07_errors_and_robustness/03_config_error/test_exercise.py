import unittest

from exercise import ConfigError, InvalidValueError, MissingKeyError, get_int, get_required


class TestConfigError(unittest.TestCase):
    def test_get_required_returns_value(self):
        """Present keys are returned, even when the value is None or empty"""
        config = {"mdm_url": "https://mdm", "token": "", "proxy": None}
        self.assertEqual(get_required(config, "mdm_url"), "https://mdm")
        self.assertEqual(get_required(config, "token"), "")
        self.assertIsNone(get_required(config, "proxy"))

    def test_missing_key_error(self):
        """A missing key raises MissingKeyError with .key and the exact message"""
        with self.assertRaises(MissingKeyError) as cm:
            get_required({"port": "1"}, "mdm_url")
        self.assertEqual(cm.exception.key, "mdm_url")
        self.assertEqual(str(cm.exception), "missing required key: mdm_url")

    def test_get_int_converts(self):
        """get_int converts strings and passes ints through"""
        self.assertEqual(get_int({"port": "8443"}, "port"), 8443)
        self.assertEqual(get_int({"port": 22}, "port"), 22)
        self.assertEqual(get_int({"retries": " 3 "}, "retries"), 3)

    def test_get_int_missing(self):
        """get_int on a missing key raises MissingKeyError"""
        with self.assertRaises(MissingKeyError) as cm:
            get_int({}, "port")
        self.assertEqual(cm.exception.key, "port")

    def test_invalid_value_error_attributes_and_message(self):
        """A non-numeric value raises InvalidValueError with .key, .value and message"""
        with self.assertRaises(InvalidValueError) as cm:
            get_int({"port": "https"}, "port")
        self.assertEqual(cm.exception.key, "port")
        self.assertEqual(cm.exception.value, "https")
        self.assertEqual(str(cm.exception), "invalid value for port: 'https'")

    def test_invalid_value_is_chained(self):
        """InvalidValueError keeps the original ValueError/TypeError as __cause__"""
        with self.assertRaises(InvalidValueError) as cm:
            get_int({"port": "x"}, "port")
        self.assertIsInstance(cm.exception.__cause__, ValueError)
        with self.assertRaises(InvalidValueError) as cm:
            get_int({"port": None}, "port")
        self.assertIsInstance(cm.exception.__cause__, TypeError)
        self.assertEqual(str(cm.exception), "invalid value for port: None")

    def test_hierarchy(self):
        """Both errors are ConfigError and Exception, so one except clause catches all"""
        self.assertTrue(issubclass(MissingKeyError, ConfigError))
        self.assertTrue(issubclass(InvalidValueError, ConfigError))
        self.assertTrue(issubclass(ConfigError, Exception))
        caught = []
        for config, key in [({}, "a"), ({"a": "nope"}, "a"), ({"a": "1"}, "a")]:
            try:
                get_int(config, key)
            except ConfigError as e:
                caught.append(type(e).__name__)
        self.assertEqual(caught, ["MissingKeyError", "InvalidValueError"])

    def test_direct_construction(self):
        """The exceptions can be raised directly with the documented signatures"""
        e = MissingKeyError("token")
        self.assertEqual((e.key, str(e)), ("token", "missing required key: token"))
        e2 = InvalidValueError("port", 3.5)
        self.assertEqual((e2.key, e2.value, str(e2)), ("port", 3.5, "invalid value for port: 3.5"))


if __name__ == "__main__":
    unittest.main()
