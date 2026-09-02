import unittest
from types import SimpleNamespace

from exercise import RetryError, backoff_delay, retry_with_backoff


def resp(status, headers=None):
    return SimpleNamespace(status=status, headers=headers or {})


def make_send(outcomes):
    """Fake request: returns each outcome in turn, raising the ones that are exceptions."""
    it = iter(outcomes)
    calls = []

    def send():
        outcome = next(it)
        calls.append(outcome)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    send.calls = calls
    return send


class Sleeper:
    def __init__(self):
        self.calls = []

    def __call__(self, seconds):
        self.calls.append(seconds)


class TestBackoffDelay(unittest.TestCase):
    def test_exponential_and_capped(self):
        """Doubles each attempt and never exceeds cap; jitter=0 is exact"""
        self.assertEqual([backoff_delay(k) for k in range(4)], [0.5, 1.0, 2.0, 4.0])
        self.assertEqual(backoff_delay(10, base=0.5, cap=30.0), 30.0)
        self.assertEqual(backoff_delay(2, base=1.0, cap=3.0), 3.0)

    def test_jitter_uses_injected_rand(self):
        """Jitter adds delay * jitter * rand() using the injected rand"""
        self.assertEqual(backoff_delay(1, base=1.0, jitter=1.0, rand=lambda: 0.5), 3.0)
        self.assertEqual(backoff_delay(1, base=1.0, jitter=0.5, rand=lambda: 0.5), 2.5)
        self.assertEqual(backoff_delay(1, base=1.0, jitter=1.0, rand=lambda: 0.0), 2.0)


class TestRetryWithBackoff(unittest.TestCase):
    def test_success_first_try(self):
        """A 200 on the first call is returned with no sleep"""
        send, sleep = make_send([resp(200)]), Sleeper()
        self.assertEqual(retry_with_backoff(send, sleep=sleep).status, 200)
        self.assertEqual(len(send.calls), 1)
        self.assertEqual(sleep.calls, [])

    def test_retries_then_succeeds(self):
        """429 and 5xx are retried with doubling delays until a success"""
        send, sleep = make_send([resp(503), resp(429), resp(502), resp(200)]), Sleeper()
        self.assertEqual(retry_with_backoff(send, sleep=sleep).status, 200)
        self.assertEqual(len(send.calls), 4)
        self.assertEqual(sleep.calls, [0.5, 1.0, 2.0])

    def test_non_retryable_returned_immediately(self):
        """404 and 401 are returned at once, never retried"""
        for status in (404, 401, 204):
            send, sleep = make_send([resp(status), resp(200)]), Sleeper()
            self.assertEqual(retry_with_backoff(send, sleep=sleep).status, status)
            self.assertEqual(len(send.calls), 1, status)
            self.assertEqual(sleep.calls, [], status)

    def test_retry_after_header_wins(self):
        """A numeric Retry-After replaces the computed delay for that retry"""
        send = make_send([resp(429, {"Retry-After": "7"}), resp(503), resp(200)])
        sleep = Sleeper()
        retry_with_backoff(send, sleep=sleep)
        self.assertEqual(sleep.calls, [7.0, 1.0])

    def test_exception_is_retried(self):
        """OSError from send counts as a retryable failure"""
        send, sleep = make_send([ConnectionError("reset"), resp(200)]), Sleeper()
        self.assertEqual(retry_with_backoff(send, sleep=sleep).status, 200)
        self.assertEqual(sleep.calls, [0.5])

    def test_gives_up_with_retry_error(self):
        """After max_attempts failures RetryError carries the last response and attempt count"""
        send, sleep = make_send([resp(503), resp(500), resp(503), resp(200)]), Sleeper()
        with self.assertRaises(RetryError) as ctx:
            retry_with_backoff(send, max_attempts=3, sleep=sleep)
        self.assertEqual(ctx.exception.attempts, 3)
        self.assertEqual(ctx.exception.response.status, 503)
        self.assertEqual(len(send.calls), 3)
        self.assertEqual(sleep.calls, [0.5, 1.0])

    def test_bad_max_attempts(self):
        """max_attempts below 1 raises ValueError without calling send"""
        send = make_send([resp(200)])
        with self.assertRaises(ValueError):
            retry_with_backoff(send, max_attempts=0, sleep=lambda s: None)
        self.assertEqual(send.calls, [])


if __name__ == "__main__":
    unittest.main()
