"""
PyLintIface — deterministic, JSON‑safe Pylint interface for use under pytest
"""

import sys
import json
import contextlib
from io import StringIO

from pylint.lint import Run
from pylint.reporters.json_reporter import JSONReporter

from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp


# ---------------------------------------------------------------------------
# Stream patching helper
# ---------------------------------------------------------------------------

@contextlib.contextmanager
def _patch_streams(out):
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stderr = sys.stdout = out
    try:
        yield
    finally:
        sys.stderr = old_stderr
        sys.stdout = old_stdout


# ---------------------------------------------------------------------------
# Deterministic JSON‑safe reporter
# ---------------------------------------------------------------------------

class AjsonReporter(JSONReporter):
    """
    JSON reporter that returns a list of plain dicts instead of Message objects.
    This makes the output stable and JSON‑serializable across Pylint versions.
    """

    def get_messages(self):
        out = []
        for m in self.messages:
            out.append({
                "msg_id": m.msg_id,
                "symbol": m.symbol,
                "message": m.msg,
                "path": m.path,
                "line": m.line,
                "column": m.column,
                "category": m.category,
                "confidence": m.confidence,
            })
        return out


# ---------------------------------------------------------------------------
# Standalone function interface
# ---------------------------------------------------------------------------
"""
def processFile(filename, compiledPackages="PyQt5,PyQt4"):
    ""
    Process a file using Pylint and return JSON text (pretty‑printed).
    ""
    out = StringIO()
    reporter = AjsonReporter(out)

    # exit=False is critical to avoid SystemExit under pytest
    with _patch_streams(out):
        Run(
            [filename, "--extension-pkg-whitelist=" + compiledPackages],
            reporter=reporter,
            exit=False,
        )

    messages = reporter.get_messages()
    return json.dumps(messages, indent=4)
"""

def processFile(filename, compiledPackages="PyQt5,PyQt4"):
    out = StringIO()
    reporter = AjsonReporter(out)

    with _patch_streams(out):
        Run([filename, "--extension-pkg-whitelist=" + compiledPackages],
            reporter=reporter,
            exit=False)

    messages = reporter.get_messages()
    return messages   # <-- FIXED


# ---------------------------------------------------------------------------
# Class‑based interface (for integration into larger systems)
# ---------------------------------------------------------------------------

class PylintIface:
    """
    Class wrapper for Pylint processing with deterministic JSON output.
    """

    acquiredData = {}

    def __init__(self, logger: CyLogger, compiledPackages: str = "PySide6"):
        self.logger = logger
        self.compiledPackages = compiledPackages
        self.args = ["--extension-pkg-whitelist=" + self.compiledPackages]

    @contextlib.contextmanager
    def _patch_streams(self, out):
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stderr = sys.stdout = out
        try:
            yield
        finally:
            sys.stderr = old_stderr
            sys.stdout = old_stdout

    class AjsonReporter(JSONReporter):
        def get_messages(self):
            out = []
            for m in self.messages:
                out.append({
                    "msg_id": m.msg_id,
                    "symbol": m.symbol,
                    "message": m.msg,
                    "path": m.path,
                    "line": m.line,
                    "column": m.column,
                    "category": m.category,
                    "confidence": m.confidence,
                })
            return out
    '''
    def processFile(self, filename: str) -> str:
        """
        Process a file and return deterministic JSON text (pretty‑printed).
        """
        out = StringIO()
        reporter = self.AjsonReporter(out)

        # exit=False prevents Pylint from calling sys.exit()
        with self._patch_streams(out):
            Run(
                [filename] + self.args,
                reporter=reporter,
                exit=False,
            )

        messages = reporter.get_messages()
        json_out = json.dumps(messages, indent=4)

        # Optionally store for later inspection
        self.acquiredData[filename] = messages

        return json_out
    '''
    def processFile(self, filename):
        out = StringIO()
        reporter = self.AjsonReporter(out)

        with self._patch_streams(out):
            Run([filename] + self.args, reporter=reporter, exit=False)

        messages = reporter.get_messages()
        self.acquiredData[filename] = messages
        return messages   # <-- FIXED


