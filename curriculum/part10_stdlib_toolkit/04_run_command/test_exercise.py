import subprocess
import unittest

from exercise import CommandError, CommandResult, query_osquery, run_command


def make_runner(stdout="", stderr="", returncode=0, raises=None):
    """A fake subprocess.run: records every call, never executes anything."""
    calls = []

    def runner(argv, **kwargs):
        calls.append((argv, kwargs))
        if raises is not None:
            raise raises
        return subprocess.CompletedProcess(argv, returncode, stdout=stdout, stderr=stderr)

    runner.calls = calls
    return runner


class TestRunCommand(unittest.TestCase):
    def test_passes_argv_and_captures(self):
        """Calls the runner with the argv list, capture_output and text, and returns a CommandResult"""
        fake = make_runner(stdout="14.5\n")
        result = run_command(["sw_vers", "-productVersion"], runner=fake)
        self.assertIsInstance(result, CommandResult)
        self.assertEqual(result.stdout, "14.5\n")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.argv, ["sw_vers", "-productVersion"])
        argv, kwargs = fake.calls[0]
        self.assertEqual(argv, ["sw_vers", "-productVersion"])
        self.assertTrue(kwargs.get("capture_output"))
        self.assertTrue(kwargs.get("text"))
        self.assertEqual(kwargs.get("timeout"), 30)

    def test_string_command_uses_shlex(self):
        """A string command is split so quoted arguments stay together"""
        fake = make_runner()
        run_command('osqueryi --json "select * from users"', runner=fake)
        self.assertEqual(fake.calls[0][0], ["osqueryi", "--json", "select * from users"])

    def test_never_uses_shell(self):
        """shell=True is never passed and argv is always a list"""
        fake = make_runner()
        run_command("echo hi", runner=fake, timeout=5)
        argv, kwargs = fake.calls[0]
        self.assertIsInstance(argv, list)
        self.assertFalse(kwargs.get("shell", False))
        self.assertEqual(kwargs.get("timeout"), 5)

    def test_nonzero_raises(self):
        """A non-zero exit raises CommandError carrying returncode and stderr"""
        fake = make_runner(stderr="No such profile", returncode=1)
        with self.assertRaises(CommandError) as ctx:
            run_command(["profiles", "show"], runner=fake)
        self.assertEqual(ctx.exception.returncode, 1)
        self.assertEqual(ctx.exception.stderr, "No such profile")
        self.assertIn("1", str(ctx.exception))
        self.assertIn("profiles", str(ctx.exception))

    def test_check_false_returns_result(self):
        """With check=False a failure is returned, not raised"""
        fake = make_runner(stderr="boom", returncode=3)
        result = run_command(["false"], runner=fake, check=False)
        self.assertEqual(result.returncode, 3)
        self.assertEqual(result.stderr, "boom")

    def test_empty_command_rejected_before_running(self):
        """An empty list or blank string raises ValueError and never calls the runner"""
        fake = make_runner()
        for cmd in ([], "", "   "):
            with self.assertRaises(ValueError, msg=repr(cmd)):
                run_command(cmd, runner=fake)
        self.assertEqual(fake.calls, [])

    def test_timeout_becomes_command_error(self):
        """subprocess.TimeoutExpired from the runner becomes CommandError with returncode None"""
        fake = make_runner(raises=subprocess.TimeoutExpired(["slow"], 30))
        with self.assertRaises(CommandError) as ctx:
            run_command(["slow"], runner=fake)
        self.assertIsNone(ctx.exception.returncode)
        self.assertIn("timed out", str(ctx.exception).lower())

    def test_query_osquery_parses_json(self):
        """query_osquery builds the osqueryi argv and parses JSON rows; empty output is []"""
        rows = '[{"uid":"501","username":"jdoe"},{"uid":"502","username":"svc"}]'
        fake = make_runner(stdout=rows)
        result = query_osquery("select uid, username from users", runner=fake)
        self.assertEqual(result, [{"uid": "501", "username": "jdoe"}, {"uid": "502", "username": "svc"}])
        self.assertEqual(fake.calls[0][0], ["osqueryi", "--json", "select uid, username from users"])
        self.assertEqual(query_osquery("select 1", runner=make_runner(stdout="  \n")), [])
        with self.assertRaises(CommandError):
            query_osquery("select 1", runner=make_runner(returncode=2, stderr="parse error"))


if __name__ == "__main__":
    unittest.main()
