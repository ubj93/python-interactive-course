import unittest

from exercise import count_online


class TestCountOnline(unittest.TestCase):
    def test_empty_list(self):
        """An empty fleet has zero online devices"""
        self.assertEqual(count_online([]), 0)

    def test_counts_exact_matches(self):
        """Counts records whose status is 'online'"""
        fleet = [
            {"hostname": "a", "status": "online"},
            {"hostname": "b", "status": "offline"},
            {"hostname": "c", "status": "online"},
        ]
        self.assertEqual(count_online(fleet), 2)

    def test_all_online(self):
        """Every record online gives the list length"""
        fleet = [{"hostname": str(i), "status": "online"} for i in range(5)]
        self.assertEqual(count_online(fleet), 5)

    def test_case_and_whitespace(self):
        """Status matching ignores case and surrounding whitespace"""
        fleet = [
            {"hostname": "a", "status": "Online"},
            {"hostname": "b", "status": " ONLINE "},
            {"hostname": "c", "status": "\tonline\n"},
            {"hostname": "d", "status": "on line"},
        ]
        self.assertEqual(count_online(fleet), 3)

    def test_missing_or_none_status(self):
        """Records without a status, or with None, are not online"""
        fleet = [
            {"hostname": "a"},
            {"hostname": "b", "status": None},
            {"hostname": "c", "status": "online"},
        ]
        self.assertEqual(count_online(fleet), 1)

    def test_does_not_modify_records(self):
        """The input records are left unchanged"""
        fleet = [{"hostname": "a", "status": " Online "}]
        count_online(fleet)
        self.assertEqual(fleet, [{"hostname": "a", "status": " Online "}])


if __name__ == "__main__":
    unittest.main()
