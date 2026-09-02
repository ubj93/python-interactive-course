import unittest

from exercise import build_command


class TestBuildCommand(unittest.TestCase):
    def test_defaults(self):
        """Only the package gives an install command"""
        self.assertEqual(build_command("zoom"), ["pkgctl", "install", "zoom"])

    def test_action_positional_and_keyword(self):
        """The action can be passed positionally or by keyword"""
        self.assertEqual(build_command("zoom", "remove"), ["pkgctl", "remove", "zoom"])
        self.assertEqual(build_command("zoom", action="update"), ["pkgctl", "update", "zoom"])

    def test_verbose_flag(self):
        """verbose=True adds --verbose after the package"""
        self.assertEqual(build_command("zoom", verbose=True), ["pkgctl", "install", "zoom", "--verbose"])
        self.assertEqual(build_command("zoom", verbose=False), ["pkgctl", "install", "zoom"])

    def test_timeout_is_stringified(self):
        """timeout adds --timeout and a string value"""
        self.assertEqual(build_command("zoom", timeout=30), ["pkgctl", "install", "zoom", "--timeout", "30"])
        self.assertEqual(build_command("zoom", timeout=2.5), ["pkgctl", "install", "zoom", "--timeout", "2.5"])
        self.assertEqual(build_command("zoom", timeout=0), ["pkgctl", "install", "zoom", "--timeout", "0"])

    def test_everything_in_order(self):
        """Flags, timeout and extra args appear in the documented order"""
        result = build_command("slack", action="update", verbose=True, timeout=60, extra_args=["--force", "--no-cache"])
        self.assertEqual(result, ["pkgctl", "update", "slack", "--verbose", "--timeout", "60", "--force", "--no-cache"])
        self.assertTrue(all(isinstance(x, str) for x in result))

    def test_extra_args_accepts_tuple(self):
        """extra_args may be any sequence, not only a list"""
        self.assertEqual(build_command("zoom", extra_args=("--force",)), ["pkgctl", "install", "zoom", "--force"])

    def test_invalid_input_raises(self):
        """An unknown action or an empty package raises ValueError"""
        with self.assertRaises(ValueError):
            build_command("zoom", action="purge")
        with self.assertRaises(ValueError):
            build_command("")

    def test_fresh_list_each_call(self):
        """Modifying one result does not leak into the next call"""
        first = build_command("zoom")
        first.append("--oops")
        self.assertEqual(build_command("zoom"), ["pkgctl", "install", "zoom"])
        extras = ["--force"]
        result = build_command("zoom", extra_args=extras)
        result.append("--oops")
        self.assertEqual(extras, ["--force"])


if __name__ == "__main__":
    unittest.main()
