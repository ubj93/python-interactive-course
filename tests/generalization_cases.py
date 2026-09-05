"""Shared public pilot checks for CPython and the real browser worker.

Run this file to emit the same grading payloads used by the browser smoke test.
Incorrect implementations live here for regression testing, not in learner files.
"""
import json
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parent.parent
PILOT = [
    ("01_two_sum", "two_sum", "two_sum_brute", [
        ("self pairing", """
            def two_sum(sizes, target):
                seen = {}
                for j, value in enumerate(sizes):
                    seen[value] = j
                    if target - value in seen:
                        return seen[target - value], j
        """),
        ("sorted indexes", """
            def two_sum(sizes, target):
                sizes = sorted(sizes)
                lo, hi = 0, len(sizes) - 1
                while lo < hi:
                    total = sizes[lo] + sizes[hi]
                    if total == target:
                        return lo, hi
                    if total < target:
                        lo += 1
                    else:
                        hi -= 1
        """),
        ("float arithmetic", """
            def two_sum(sizes, target):
                seen = {}
                for j, value in enumerate(sizes):
                    need = float(target) - float(value)
                    if need in seen:
                        return seen[need], j
                    seen[float(value)] = j
        """),
    ]),
    ("02_balanced_brackets", "balanced_brackets", "balanced_brackets_expected", [
        ("counts without nesting", """
            def balanced_brackets(text):
                return all(text.count(left) == text.count(right) for left, right in ['()', '[]', '{}'])
        """),
        ("ignores quoted brackets", """
            import re
            def balanced_brackets(text):
                text = re.sub(r"'[^']*'", '', text)
                text = re.sub(r'"[^"]*"', '', text)
                stack = []
                for ch in text:
                    if ch in '([{':
                        stack.append(ch)
                    elif ch in ')]}':
                        if not stack or stack.pop() != {')': '(', ']': '[', '}': '{'}[ch]:
                            return False
                return not stack
        """),
        ("stops after the first pair", """
            def balanced_brackets(text):
                stack = []
                for ch in text:
                    if ch in '([{':
                        stack.append(ch)
                    elif ch in ')]}':
                        if not stack or stack.pop() != {')': '(', ']': '[', '}': '{'}[ch]:
                            return False
                        if not stack:
                            return True
                return not stack
        """),
    ]),
    ("07_bisect_first_bad", "bisect_first_bad", "bisect_first_bad_half_open", [
        ("linear scan", """
            def bisect_first_bad(n_builds, is_bad):
                for build in range(1, n_builds + 1):
                    if is_bad(build):
                        return build
        """),
        ("unchecked final build", """
            def bisect_first_bad(n_builds, is_bad):
                if not n_builds:
                    return None
                lo, hi = 1, n_builds
                while lo < hi:
                    mid = (lo + hi) // 2
                    if is_bad(mid):
                        hi = mid
                    else:
                        lo = mid + 1
                return lo
        """),
        ("float midpoint", """
            def bisect_first_bad(n_builds, is_bad):
                if not n_builds:
                    return None
                lo, hi = 1, n_builds
                while lo < hi:
                    mid = int((lo + hi) / 2)
                    if is_bad(mid):
                        hi = mid
                    else:
                        lo = mid + 1
                return lo if is_bad(lo) else None
        """),
    ]),
]

GENERALIZATION_ONLY = '''

def load_tests(loader, tests, pattern):
    # Use the actual shipped test method; skip unrelated stress tests for mutants.
    return unittest.TestSuite(case for group in tests for case in group
                              if case._testMethodName == "test_generalization_seeded")
'''


def grading_cases():
    cases = []
    for folder, name, alternative, mutants in PILOT:
        directory = ROOT / "curriculum/part12_interview_patterns" / folder
        reference = (directory / "solution.py").read_text(encoding="utf-8")
        tests = (directory / "test_exercise.py").read_text(encoding="utf-8")
        variants = [("reference (full suite)", reference, tests, True),
                    ("alternative (generalization)", reference + f"\n{name} = {alternative}\n", tests + GENERALIZATION_ONLY, True)]
        variants += [(label, textwrap.dedent(code), tests + GENERALIZATION_ONLY, False) for label, code in mutants]
        for label, code, test_source, passes in variants:
            cases.append({"name": name + ": " + label, "slug": folder,
                          "passes": passes, "files": {"exercise.py": code, "test_exercise.py": test_source}})
    return cases


if __name__ == "__main__":
    print(json.dumps(grading_cases()))
