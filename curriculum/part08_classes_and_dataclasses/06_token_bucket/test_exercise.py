import unittest

from exercise import TokenBucket


class FakeClock:
    """A clock the test moves by hand. Calling it returns the current time."""

    def __init__(self, t: float = 0.0) -> None:
        self.t = t

    def __call__(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        self.t += seconds


class TestTokenBucket(unittest.TestCase):
    def test_starts_full_and_allows_a_burst(self):
        """A fresh bucket allows exactly `capacity` calls, then denies"""
        clock = FakeClock()
        bucket = TokenBucket(capacity=3, refill_per_second=1.0, now=clock)
        self.assertEqual(bucket.available, 3.0)
        self.assertEqual([bucket.allow() for _ in range(4)], [True, True, True, False])

    def test_denied_call_spends_nothing(self):
        """A denied allow() leaves the token count unchanged"""
        clock = FakeClock()
        bucket = TokenBucket(capacity=2, refill_per_second=1.0, now=clock)
        bucket.allow()
        self.assertFalse(bucket.allow(cost=2))
        self.assertEqual(bucket.available, 1.0)
        self.assertTrue(bucket.allow())

    def test_refills_over_time(self):
        """Tokens come back at refill_per_second"""
        clock = FakeClock()
        bucket = TokenBucket(capacity=3, refill_per_second=1.0, now=clock)
        for _ in range(3):
            bucket.allow()
        self.assertFalse(bucket.allow())
        clock.advance(2.0)
        self.assertEqual(bucket.available, 2.0)
        self.assertTrue(bucket.allow())
        self.assertTrue(bucket.allow())
        self.assertFalse(bucket.allow())

    def test_never_exceeds_capacity(self):
        """Waiting a long time fills the bucket to capacity and no further"""
        clock = FakeClock()
        bucket = TokenBucket(capacity=5, refill_per_second=10.0, now=clock)
        bucket.allow()
        clock.advance(1000.0)
        self.assertEqual(bucket.available, 5.0)
        self.assertEqual([bucket.allow() for _ in range(6)], [True] * 5 + [False])

    def test_fractional_refill(self):
        """Half a second at 1 token/s gives half a token, which is not enough for a call"""
        clock = FakeClock()
        bucket = TokenBucket(capacity=1, refill_per_second=1.0, now=clock)
        self.assertTrue(bucket.allow())
        clock.advance(0.5)
        self.assertAlmostEqual(bucket.available, 0.5)
        self.assertFalse(bucket.allow())
        clock.advance(0.5)
        self.assertTrue(bucket.allow())

    def test_cost(self):
        """cost spends several tokens at once; cost above capacity raises"""
        clock = FakeClock()
        bucket = TokenBucket(capacity=4, refill_per_second=2.0, now=clock)
        self.assertTrue(bucket.allow(cost=3))
        self.assertEqual(bucket.available, 1.0)
        self.assertFalse(bucket.allow(cost=2))
        with self.assertRaises(ValueError):
            bucket.allow(cost=5)
        with self.assertRaises(ValueError):
            bucket.seconds_until(cost=5)

    def test_seconds_until(self):
        """seconds_until reports 0.0 when allowed, else the wait at the refill rate"""
        clock = FakeClock(t=100.0)
        bucket = TokenBucket(capacity=2, refill_per_second=0.5, now=clock)
        self.assertEqual(bucket.seconds_until(), 0.0)
        bucket.allow(cost=2)
        self.assertAlmostEqual(bucket.seconds_until(), 2.0)
        self.assertAlmostEqual(bucket.seconds_until(cost=2), 4.0)
        clock.advance(1.0)
        self.assertAlmostEqual(bucket.seconds_until(), 1.0)

    def test_validation_and_backwards_clock(self):
        """Bad constructor arguments raise; a clock that goes backwards does not drain tokens"""
        clock = FakeClock()
        for capacity, rate in [(0, 1.0), (-1, 1.0), (1, 0.0), (1, -2.0)]:
            with self.assertRaises(ValueError, msg=(capacity, rate)):
                TokenBucket(capacity, rate, clock)
        bucket = TokenBucket(capacity=2, refill_per_second=1.0, now=clock)
        bucket.allow()
        clock.t = -5.0
        self.assertEqual(bucket.available, 1.0)
        clock.t = 1.0
        self.assertEqual(bucket.available, 2.0)


if __name__ == "__main__":
    unittest.main()
