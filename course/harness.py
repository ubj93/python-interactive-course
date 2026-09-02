"""Test harness executed in a subprocess (or inside Pyodide) for one exercise.

Usage: python harness.py <exercise_dir>

Prints the learner's own stdout first, then a sentinel line followed by a JSON
document describing each test case. Keeping this file dependency-free and
self-contained lets the same harness run in the browser.
"""
import io
import json
import os
import sys
import traceback
import unittest

SENTINEL = "@@COURSE_RESULT@@"


class _FileOrderLoader(unittest.TestLoader):
    """Collect test methods in the order they appear in the file (easy tests first)."""

    def getTestCaseNames(self, testCaseClass):
        names = super().getTestCaseNames(testCaseClass)

        def line(name):
            fn = getattr(testCaseClass, name, None)
            code = getattr(fn, "__code__", None)
            return getattr(code, "co_firstlineno", 0)

        return sorted(names, key=line)


class _Recorder(unittest.TestResult):
    def __init__(self):
        super().__init__()
        self.records = []

    @staticmethod
    def _name(test):
        return getattr(test, "_testMethodName", str(test))

    @staticmethod
    def _doc(test):
        doc = test.shortDescription() if hasattr(test, "shortDescription") else None
        return doc or ""

    def _add(self, test, status, err=None):
        rec = {"name": self._name(test), "doc": self._doc(test), "status": status}
        if err is not None:
            etype, evalue, tb = err
            # Trim the unittest frames so the learner sees their code, not the runner.
            rec["message"] = "".join(traceback.format_exception_only(etype, evalue)).strip()
            rec["traceback"] = "".join(traceback.format_exception(etype, evalue, tb))
        self.records.append(rec)

    def addSuccess(self, test):
        super().addSuccess(test)
        self._add(test, "pass")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._add(test, "fail", err)

    def addError(self, test, err):
        super().addError(test, err)
        self._add(test, "error", err)

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._add(test, "skip")
        self.records[-1]["message"] = reason

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            status = "fail" if issubclass(err[0], AssertionError) else "error"
            self._add(subtest, status, err)
            self.records[-1]["name"] = str(subtest)


def run(exercise_dir):
    exercise_dir = os.path.abspath(exercise_dir)
    os.chdir(exercise_dir)
    sys.path.insert(0, exercise_dir)
    for mod in ("exercise", "test_exercise"):
        sys.modules.pop(mod, None)

    out = {"import_error": None, "tests": []}
    real_stdout = sys.stdout
    captured = io.StringIO()
    sys.stdout = captured
    try:
        try:
            __import__("exercise")
        except BaseException:  # noqa: BLE001 - report anything, including SystemExit
            out["import_error"] = traceback.format_exc()
        else:
            loader = _FileOrderLoader()
            try:
                suite = loader.loadTestsFromName("test_exercise")
            except BaseException:  # noqa: BLE001
                out["import_error"] = traceback.format_exc()
            else:
                rec = _Recorder()
                suite.run(rec)
                out["tests"] = rec.records
    finally:
        sys.stdout = real_stdout
    out["stdout"] = captured.getvalue()
    real_stdout.write(SENTINEL + "\n" + json.dumps(out) + "\n")
    real_stdout.flush()
    return out


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else ".")
