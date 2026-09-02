import unittest

from exercise import group_by_department


class TestGroupByDepartment(unittest.TestCase):
    def test_basic_grouping(self):
        """Hostnames are collected per department"""
        devices = [
            {"hostname": "mbp-1", "department": "Finance"},
            {"hostname": "mbp-2", "department": "IT"},
            {"hostname": "mbp-3", "department": "Finance"},
        ]
        self.assertEqual(group_by_department(devices), {"Finance": ["mbp-1", "mbp-3"], "IT": ["mbp-2"]})

    def test_empty(self):
        """No devices gives an empty dict"""
        self.assertEqual(group_by_department([]), {})

    def test_first_seen_order(self):
        """Departments are ordered by first appearance, hostnames by input order"""
        devices = [
            {"hostname": "c", "department": "Sales"},
            {"hostname": "a", "department": "Eng"},
            {"hostname": "b", "department": "Sales"},
            {"hostname": "a", "department": "Sales"},
        ]
        result = group_by_department(devices)
        self.assertEqual(list(result), ["Sales", "Eng"])
        self.assertEqual(result["Sales"], ["c", "b", "a"])

    def test_unassigned(self):
        """Missing, None and blank departments go under 'unassigned'"""
        devices = [
            {"hostname": "a"},
            {"hostname": "b", "department": None},
            {"hostname": "c", "department": "   "},
            {"hostname": "d", "department": "IT"},
        ]
        self.assertEqual(group_by_department(devices), {"unassigned": ["a", "b", "c"], "IT": ["d"]})

    def test_whitespace_stripped_case_kept(self):
        """Surrounding whitespace is stripped but case is significant"""
        devices = [
            {"hostname": "a", "department": " IT "},
            {"hostname": "b", "department": "IT"},
            {"hostname": "c", "department": "it"},
        ]
        self.assertEqual(group_by_department(devices), {"IT": ["a", "b"], "it": ["c"]})

    def test_devices_without_hostname_skipped(self):
        """Records with no hostname do not create groups or entries"""
        devices = [
            {"department": "Finance"},
            {"hostname": None, "department": "Finance"},
            {"hostname": "x", "department": "IT"},
        ]
        self.assertEqual(group_by_department(devices), {"IT": ["x"]})


if __name__ == "__main__":
    unittest.main()
