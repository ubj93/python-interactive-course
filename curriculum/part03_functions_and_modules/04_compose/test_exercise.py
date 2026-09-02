import unittest

from exercise import compose


def strip(s):
    return s.strip()


def lower(s):
    return s.lower()


def drop_domain(s):
    return s.split(".")[0]


class TestCompose(unittest.TestCase):
    def test_single_function(self):
        """compose(f) behaves like f"""
        self.assertEqual(compose(lower)("ABC"), "abc")

    def test_two_functions_right_to_left(self):
        """compose(f, g)(x) is f(g(x))"""
        self.assertEqual(compose(lambda x: x + 1, lambda x: x * 10)(4), 41)
        self.assertEqual(compose(lambda x: x * 10, lambda x: x + 1)(4), 50)

    def test_three_functions(self):
        """Three functions apply last-to-first"""
        clean = compose(drop_domain, lower, strip)
        self.assertEqual(clean("  MBP-J-DOE.corp.example.com \n"), "mbp-j-doe")

    def test_identity(self):
        """compose() with no functions returns its argument unchanged"""
        self.assertEqual(compose()("unchanged"), "unchanged")
        self.assertEqual(compose()(42), 42)
        self.assertIsNone(compose()(None))

    def test_works_with_builtins_and_methods(self):
        """Built-ins and unbound str methods are ordinary callables"""
        self.assertEqual(compose(len, str.strip)("  abc  "), 3)
        self.assertEqual(compose(str, abs)(-7), "7")

    def test_result_is_reusable_and_independent(self):
        """The composed function can be called repeatedly and does not share state"""
        add_then_double = compose(lambda x: x * 2, lambda x: x + 1)
        double_then_add = compose(lambda x: x + 1, lambda x: x * 2)
        self.assertEqual([add_then_double(1), add_then_double(1)], [4, 4])
        self.assertEqual(double_then_add(1), 3)

    def test_non_callable_raises_at_compose_time(self):
        """A non-callable argument raises TypeError when compose is called"""
        with self.assertRaises(TypeError):
            compose(str.lower, "strip")
        with self.assertRaises(TypeError):
            compose(None)


if __name__ == "__main__":
    unittest.main()
