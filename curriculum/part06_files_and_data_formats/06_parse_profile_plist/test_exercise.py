import plistlib
import unittest

from exercise import parse_profile_plist


def profile(**overrides):
    base = {
        "PayloadType": "Configuration",
        "PayloadIdentifier": "com.corp.wifi",
        "PayloadDisplayName": "Corp Wi-Fi",
        "PayloadContent": [
            {
                "PayloadType": "com.apple.wifi.managed",
                "PayloadIdentifier": "com.corp.wifi.net",
                "PayloadDisplayName": "Wi-Fi network",
                "SSID_STR": "CorpNet",
            }
        ],
    }
    base.update(overrides)
    return base


class TestParseProfilePlist(unittest.TestCase):
    def test_minimal_profile(self):
        """Reads identifier, display name and one payload"""
        result = parse_profile_plist(plistlib.dumps(profile()))
        self.assertEqual(result["identifier"], "com.corp.wifi")
        self.assertEqual(result["display_name"], "Corp Wi-Fi")
        self.assertEqual(result["payload_count"], 1)
        self.assertEqual(result["payload_types"], ["com.apple.wifi.managed"])
        self.assertEqual(
            result["payloads"],
            [{"type": "com.apple.wifi.managed", "identifier": "com.corp.wifi.net", "display_name": "Wi-Fi network"}],
        )

    def test_defaults_for_missing_keys(self):
        """Missing organization, display name, removal flag and content get defaults"""
        data = plistlib.dumps({"PayloadType": "Configuration", "PayloadIdentifier": "com.corp.empty"})
        self.assertEqual(
            parse_profile_plist(data),
            {
                "identifier": "com.corp.empty",
                "display_name": "",
                "organization": "",
                "removal_disallowed": False,
                "payload_count": 0,
                "payload_types": [],
                "payloads": [],
            },
        )

    def test_organization_and_removal(self):
        """PayloadOrganization and PayloadRemovalDisallowed are carried over"""
        data = plistlib.dumps(profile(PayloadOrganization="Example Corp", PayloadRemovalDisallowed=True))
        result = parse_profile_plist(data)
        self.assertEqual(result["organization"], "Example Corp")
        self.assertIs(result["removal_disallowed"], True)

    def test_payload_fallbacks_and_distinct_types(self):
        """Payload display name falls back to type; types are sorted and unique"""
        content = [
            {"PayloadType": "com.apple.wifi.managed", "PayloadIdentifier": "a"},
            {"PayloadType": "com.apple.MCX.FileVault2", "PayloadIdentifier": "b", "PayloadDisplayName": "FileVault"},
            {"PayloadType": "com.apple.wifi.managed"},
        ]
        result = parse_profile_plist(plistlib.dumps(profile(PayloadContent=content)))
        self.assertEqual(result["payload_count"], 3)
        self.assertEqual(result["payload_types"], ["com.apple.MCX.FileVault2", "com.apple.wifi.managed"])
        self.assertEqual(
            result["payloads"],
            [
                {"type": "com.apple.wifi.managed", "identifier": "a", "display_name": "com.apple.wifi.managed"},
                {"type": "com.apple.MCX.FileVault2", "identifier": "b", "display_name": "FileVault"},
                {"type": "com.apple.wifi.managed", "identifier": "", "display_name": "com.apple.wifi.managed"},
            ],
        )

    def test_binary_plist(self):
        """A binary-format plist parses the same as XML"""
        xml = plistlib.dumps(profile())
        binary = plistlib.dumps(profile(), fmt=plistlib.FMT_BINARY)
        self.assertEqual(parse_profile_plist(binary), parse_profile_plist(xml))

    def test_fixture_file(self):
        """Summarizes the shipped fixtures/profile.mobileconfig"""
        with open("fixtures/profile.mobileconfig", "rb") as f:
            result = parse_profile_plist(f.read())
        self.assertEqual(result["identifier"], "com.corp.profile.wifi-and-security")
        self.assertEqual(result["display_name"], "Corp Wi-Fi and Security")
        self.assertEqual(result["organization"], "Example Corp")
        self.assertIs(result["removal_disallowed"], True)
        self.assertEqual(result["payload_count"], 4)
        self.assertEqual(
            result["payload_types"],
            ["com.apple.MCX.FileVault2", "com.apple.security.pem", "com.apple.wifi.managed"],
        )
        self.assertEqual(
            [p["display_name"] for p in result["payloads"]],
            ["Corp Wi-Fi", "Corp Root CA", "com.apple.MCX.FileVault2", "Guest Wi-Fi"],
        )

    def test_not_a_configuration_raises(self):
        """A plist that is not a Configuration profile raises ValueError"""
        with self.assertRaises(ValueError):
            parse_profile_plist(plistlib.dumps({"PayloadType": "com.apple.wifi.managed"}))
        with self.assertRaises(ValueError):
            parse_profile_plist(plistlib.dumps(["not", "a", "dict"]))

    def test_garbage_raises_value_error(self):
        """Bytes that are not a plist raise ValueError with the original chained"""
        for data in [b"", b"this is not xml", b"<?xml version='1.0'?><plist><dict><key>x</key>"]:
            with self.assertRaises(ValueError, msg=repr(data)) as cm:
                parse_profile_plist(data)
            self.assertIsNotNone(cm.exception.__cause__, repr(data))


if __name__ == "__main__":
    unittest.main()
