"""Structured unittest oracle: per-test identity, phase, outcome.

Runs unittest discovery and reports each error/failure with the phase
it died in, so a gate can tell an executed-test failure (bug proof)
from import/discovery/setup/teardown noise (not proof).

Usage: python structured_unittest.py START_DIR [TOP_DIR]
Prints one JSON object to stdout:
  {"tests_run": N, "events": [{"test": id, "outcome": "error"|"failure",
   "phase": "import"|"setup"|"call"|"teardown", "exc": "ExcName: msg"}]}
Exit 0 unless this runner itself crashes (exit 2 with {"runner_error"}).
Environment (PYTHONPATH, PATH, cwd) is inherited: the caller must set
the same sandbox the plain `unittest discover` gate uses.
"""
import json
import sys
import traceback
import unittest


def classify(test, err):
    """Phase of a (test, err) pair from unittest.

    import: loader could not import the module (_FailedTest).
    setup: setUp (or its helpers) raised before the test body ran.
    teardown: tearDown raised after the body ran.
    call: anything else - the test body executed and misbehaved.
    """
    if test.id().startswith("unittest.loader._FailedTest"):
        return "import"
    if err is None:
        return "call"
    frames = traceback.extract_tb(err[2])
    names = [f.name for f in frames]
    method = getattr(test, "_testMethodName", "")
    if "setUp" in names and method not in names:
        return "setup"
    if "tearDown" in names:
        return "teardown"
    return "call"


class Probe(unittest.TestResult):
    def __init__(self):
        super().__init__()
        self.events = []

    def _record(self, test, outcome, err):
        exc = "%s: %s" % (err[0].__name__, err[1]) if err else ""
        self.events.append({"test": test.id(), "outcome": outcome,
                            "phase": classify(test, err), "exc": exc[:300]})

    def addError(self, test, err):
        super().addError(test, err)
        self._record(test, "error", err)

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._record(test, "failure", err)

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            outcome = ("failure"
                       if issubclass(err[0], test.failureException)
                       else "error")
            self._record(test, outcome, err)


def main(argv):
    start = argv[1]
    top = argv[2] if len(argv) > 2 else start
    try:
        suite = unittest.TestLoader().discover(start, top_level_dir=top)
        result = Probe()
        suite(result)
    except Exception as exc:  # noqa: BLE001 - runner crash is data
        print(json.dumps({"runner_error": "%s: %s"
                          % (type(exc).__name__, exc)}))
        return 2
    print(json.dumps({"tests_run": result.testsRun,
                      "events": result.events}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
