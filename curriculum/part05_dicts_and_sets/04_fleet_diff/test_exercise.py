import unittest

from exercise import fleet_diff


class TestFleetDiff(unittest.TestCase):
    def test_all_in_both(self):
        """Identical sources: everything is in 'both'"""
        self.assertEqual(
            fleet_diff(["A", "B"], ["A", "B"]),
            {"only_mdm": [], "only_inventory": [], "both": ["A", "B"], "neither": []},
        )

    def test_only_sides(self):
        """Serials missing from one side land in the right bucket"""
        result = fleet_diff(["A", "B", "C"], ["B", "C", "D"])
        self.assertEqual(result["only_mdm"], ["A"])
        self.assertEqual(result["only_inventory"], ["D"])
        self.assertEqual(result["both"], ["B", "C"])

    def test_empty_inputs(self):
        """Empty inputs give four empty lists"""
        self.assertEqual(fleet_diff([], []), {"only_mdm": [], "only_inventory": [], "both": [], "neither": []})
        self.assertEqual(fleet_diff(["A"], [])["only_mdm"], ["A"])

    def test_sorted_output(self):
        """Every list is sorted regardless of input order"""
        result = fleet_diff(["Z", "M", "A"], ["M", "B", "A", "Y"])
        self.assertEqual(result["both"], ["A", "M"])
        self.assertEqual(result["only_mdm"], ["Z"])
        self.assertEqual(result["only_inventory"], ["B", "Y"])

    def test_neither_uses_purchased(self):
        """Purchased serials seen by nobody are 'neither'"""
        result = fleet_diff(["A"], ["B"], ["A", "B", "C", "D"])
        self.assertEqual(result["neither"], ["C", "D"])
        self.assertEqual(result["only_mdm"], ["A"])

    def test_normalisation_and_duplicates(self):
        """Whitespace, case and repeats do not create false differences"""
        result = fleet_diff([" c02a ", "C02A", "c02b"], ["C02B", "C02A "], ["c02a", "C02Z", " "])
        self.assertEqual(result, {"only_mdm": [], "only_inventory": [], "both": ["C02A", "C02B"], "neither": ["C02Z"]})

    def test_accepts_any_iterable(self):
        """Sets, tuples and generators work as inputs"""
        result = fleet_diff({"A", "B"}, ("B",), (s for s in ["A", "B", "C"]))
        self.assertEqual(result, {"only_mdm": ["A"], "only_inventory": [], "both": ["B"], "neither": ["C"]})


if __name__ == "__main__":
    unittest.main()
