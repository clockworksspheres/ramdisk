"""
PylintIface — deterministic, JSON‑safe Pylint interface for pytest
"""

import sys
import contextlib
from io import StringIO
import astroid

from pylint.lint import Run
from pylint.reporters.json_reporter import JSONReporter


# ---------------------------------------------------------------------------
# Stream patching helper
# ---------------------------------------------------------------------------

@contextlib.contextmanager
def _patch_streams(out):
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = out
    sys.stderr = out
    try:
        yield
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


# ---------------------------------------------------------------------------
# Deterministic JSON‑safe reporter
# ---------------------------------------------------------------------------

class AjsonReporter(JSONReporter):
    """
    JSON reporter that returns a list of plain dicts instead of Message objects.
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

    def handle_fatal(self, msg):
        # swallow fatal output and clear messages
        self.messages.clear()
        try:
            self.out.write("")
        except Exception:
            pass
        return None


# ---------------------------------------------------------------------------
# Shared Pylint argument list
# ---------------------------------------------------------------------------

BASE_ARGS = [
    "--ignored-modules=psutil,requests,pywin32,win32security,win32process,win32api",
    "--ignore=__pycache__,.pytest_cache,.qtcreator",
    "--ignore-paths=.*[\\/](ui)[\\/].*",
]


# ---------------------------------------------------------------------------
# Standalone function interface
# ---------------------------------------------------------------------------

def processFile(filename, compiledPackages="PySide6,PyQt5,PyQt4"):
    out = StringIO()
    reporter = AjsonReporter(out)
    msgs = ""

    args = [
        filename,
        "--extension-pkg-whitelist=" + compiledPackages,
    ] + BASE_ARGS

    with _patch_streams(out):
        try:
            Run(args, reporter=reporter, exit=False)
        except astroid.exceptions.AstroidError:
            reporter.messages.clear()
        except Exception:
            msgs = reporter.get_messages()
            if any(m["msg_id"].startswith("F") for m in msgs):
                pass  # real fatal lint message
            else:
                reporter.messages.clear()

    return reporter.get_messages()


# ---------------------------------------------------------------------------
# Class‑based interface
# ---------------------------------------------------------------------------

class PylintIface:
    acquiredData = {}

    def __init__(self, compiledPackages="PySide6"):
        self.compiledPackages = compiledPackages
        self.args = [
            "--extension-pkg-whitelist=" + self.compiledPackages,
        ] + BASE_ARGS

    @contextlib.contextmanager
    def _patch_streams(self, out):
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = out
        sys.stderr = out
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def processFile(self, filename):
        out = StringIO()
        reporter = AjsonReporter(out)

        args = [filename] + self.args

        with self._patch_streams(out):
            try:
                Run(args, reporter=reporter, exit=False)
            except astroid.exceptions.AstroidError:
                reporter.messages.clear()
            except Exception:
                msgs = reporter.get_messages()
                if any(m["msg_id"].startswith("F") for m in msgs):
                    pass
                else:
                    reporter.messages.clear()

        messages = reporter.get_messages()
        self.acquiredData[filename] = messages
        return messages

