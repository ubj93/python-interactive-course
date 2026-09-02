import unittest

from exercise import extract_ips


class TestExtractIps(unittest.TestCase):
    def test_single(self):
        """Finds one address in a sentence"""
        self.assertEqual(extract_ips("gateway is 192.168.1.1 today"), ["192.168.1.1"])

    def test_several_with_punctuation(self):
        """Ports, brackets and commas around an address are fine"""
        text = "connected to 10.0.0.5:443 from (192.168.1.20), dns=8.8.8.8,"
        self.assertEqual(extract_ips(text), ["10.0.0.5", "192.168.1.20", "8.8.8.8"])

    def test_boundaries_of_range(self):
        """0.0.0.0 and 255.255.255.255 are valid"""
        self.assertEqual(extract_ips("0.0.0.0 -> 255.255.255.255"), ["0.0.0.0", "255.255.255.255"])

    def test_empty(self):
        """Empty text gives an empty list"""
        self.assertEqual(extract_ips(""), [])
        self.assertEqual(extract_ips("no addresses here"), [])

    def test_octet_out_of_range(self):
        """A group above 255 invalidates the whole candidate"""
        self.assertEqual(extract_ips("256.1.1.1 and 1.1.1.999 but 10.0.0.1"), ["10.0.0.1"])

    def test_leading_zero(self):
        """Groups with a leading zero are invalid, a lone 0 is fine"""
        self.assertEqual(extract_ips("010.0.0.1 10.0.00.1 10.0.0.1"), ["10.0.0.1"])

    def test_not_part_of_longer_dotted_number(self):
        """Extra dotted groups or digits glued on either side disqualify"""
        self.assertEqual(extract_ips("10.1.2.3.4 1234.1.2.3 1.2.3.4567 v1.2.3.4"), ["1.2.3.4"])

    def test_duplicates_kept_in_order(self):
        """Duplicates are kept and order is preserved"""
        self.assertEqual(extract_ips("1.1.1.1 2.2.2.2 1.1.1.1"), ["1.1.1.1", "2.2.2.2", "1.1.1.1"])


if __name__ == "__main__":
    unittest.main()
