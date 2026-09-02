import unittest

from exercise import camel_to_snake, snake_to_camel


class TestSnakeToCamel(unittest.TestCase):
    def test_basic(self):
        """Words after the first get a capital letter"""
        self.assertEqual(snake_to_camel("device_name"), "deviceName")
        self.assertEqual(snake_to_camel("last_check_in_time"), "lastCheckInTime")

    def test_single_word_and_empty(self):
        """A single word and an empty string pass through"""
        self.assertEqual(snake_to_camel("serial"), "serial")
        self.assertEqual(snake_to_camel(""), "")
        self.assertEqual(snake_to_camel("___"), "")

    def test_extra_underscores_and_case(self):
        """Doubled, leading and trailing underscores collapse; input case is ignored"""
        self.assertEqual(snake_to_camel("__OS_VERSION__"), "osVersion")
        self.assertEqual(snake_to_camel("mdm__Check_In"), "mdmCheckIn")

    def test_digits_stay_put(self):
        """Digits do not trigger capitalisation of the following letter"""
        self.assertEqual(snake_to_camel("v2_build"), "v2Build")
        self.assertEqual(snake_to_camel("check_in2go_flag"), "checkIn2goFlag")

    def test_camel_basic(self):
        """Each capital letter starts a new lowercase word"""
        self.assertEqual(camel_to_snake("deviceName"), "device_name")
        self.assertEqual(camel_to_snake("lastCheckInTime"), "last_check_in_time")
        self.assertEqual(camel_to_snake("serial"), "serial")
        self.assertEqual(camel_to_snake(""), "")

    def test_camel_digits(self):
        """A capital after a digit starts a new word"""
        self.assertEqual(camel_to_snake("v2Build"), "v2_build")
        self.assertEqual(camel_to_snake("osVersion14"), "os_version14")

    def test_round_trip(self):
        """camel_to_snake undoes snake_to_camel for plain names"""
        for name in ["device_name", "last_check_in_time", "v2_build", "serial"]:
            self.assertEqual(camel_to_snake(snake_to_camel(name)), name, name)

    def test_camel_acronyms(self):
        """A run of capitals is one word"""
        self.assertEqual(camel_to_snake("deviceID"), "device_id")
        self.assertEqual(camel_to_snake("IPAddress"), "ip_address")
        self.assertEqual(camel_to_snake("HTTPSProxyURL"), "https_proxy_url")


if __name__ == "__main__":
    unittest.main()
