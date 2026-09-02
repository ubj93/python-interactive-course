import unittest

from exercise import retry


class Flaky:
    """Calls fail with the queued exceptions, then return the final value."""

    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)
        self.calls = []

    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


class TestRetry(unittest.TestCase):
    def setUp(self):
        self.waits = []

    def sleep(self, seconds):
        self.waits.append(seconds)

    def test_success_first_time(self):
        """A call that succeeds is made once with no sleep"""
        target = Flaky("ok")
        wrapped = retry(times=3, sleep=self.sleep)(target)
        self.assertEqual(wrapped(), "ok")
        self.assertEqual(len(target.calls), 1)
        self.assertEqual(self.waits, [])

    def test_retries_then_succeeds(self):
        """Two failures then success gives the result after two sleeps with backoff"""
        target = Flaky(ConnectionError("down"), ConnectionError("down"), "ok")
        wrapped = retry(times=3, exceptions=(ConnectionError,), sleep=self.sleep)(target)
        self.assertEqual(wrapped(), "ok")
        self.assertEqual(len(target.calls), 3)
        self.assertEqual(self.waits, [1.0, 2.0])

    def test_custom_delay_and_backoff(self):
        """delay and backoff shape the wait sequence"""
        target = Flaky(OSError(), OSError(), OSError(), "ok")
        wrapped = retry(times=4, exceptions=(OSError,), sleep=self.sleep, delay=0.5, backoff=3.0)(target)
        self.assertEqual(wrapped(), "ok")
        self.assertEqual(self.waits, [0.5, 1.5, 4.5])

    def test_gives_up_and_reraises_last(self):
        """After `times` failures the last exception object is re-raised, no extra sleep"""
        last = ConnectionError("still down")
        target = Flaky(ConnectionError("down"), ConnectionError("down"), last)
        wrapped = retry(times=3, exceptions=(ConnectionError,), sleep=self.sleep)(target)
        with self.assertRaises(ConnectionError) as cm:
            wrapped()
        self.assertIs(cm.exception, last)
        self.assertEqual(len(target.calls), 3)
        self.assertEqual(self.waits, [1.0, 2.0])

    def test_unlisted_exception_propagates_immediately(self):
        """An exception not in `exceptions` is not retried and does not sleep"""
        target = Flaky(KeyError("serial"), "never reached")
        wrapped = retry(times=3, exceptions=(ConnectionError,), sleep=self.sleep)(target)
        with self.assertRaises(KeyError):
            wrapped()
        self.assertEqual(len(target.calls), 1)
        self.assertEqual(self.waits, [])

    def test_arguments_pass_through(self):
        """Positional and keyword arguments reach the function on every attempt"""
        target = Flaky(ValueError("x"), "ok")
        wrapped = retry(times=2, exceptions=(ValueError,), sleep=self.sleep)(target)
        self.assertEqual(wrapped("C02XG1234ABC", verbose=True), "ok")
        self.assertEqual(target.calls, [(("C02XG1234ABC",), {"verbose": True})] * 2)

    def test_decorator_syntax_and_wraps(self):
        """Works with @ syntax, times=1 means no retry, and __name__/__doc__ survive"""
        attempts = []

        @retry(times=1, sleep=self.sleep)
        def check_in(serial):
            """Check a device in."""
            attempts.append(serial)
            raise TimeoutError("slow")

        with self.assertRaises(TimeoutError):
            check_in("7GH2K3Q")
        self.assertEqual(attempts, ["7GH2K3Q"])
        self.assertEqual(self.waits, [])
        self.assertEqual(check_in.__name__, "check_in")
        self.assertEqual(check_in.__doc__, "Check a device in.")

    def test_times_below_one_rejected_early(self):
        """times < 1 raises ValueError when retry(...) is called"""
        with self.assertRaises(ValueError):
            retry(times=0, sleep=self.sleep)
        with self.assertRaises(ValueError):
            retry(times=-2, sleep=self.sleep)


if __name__ == "__main__":
    unittest.main()
