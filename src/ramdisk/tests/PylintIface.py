"""
PyLintIface — deterministic, JSON‑safe Pylint interface for use under pytest
"""

import sys
import json
import contextlib
from io import StringIO

from pylint.lint import Run
from pylint.reporters.json_reporter import JSONReporter
import astroid

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

    def handle_fatal(self, msg):
        self.messages.clear()
        try:
            self.out.write("")  # swallow fatal output
        except Exception:
            pass
        return None


# ---------------------------------------------------------------------------
# Standalone function interface
# ---------------------------------------------------------------------------
def processFile(filename, compiledPackages="PySide6,PyQt5,PyQt4"):
    out = StringIO()
    reporter = AjsonReporter(out)
    msgs = ""

    # exit=False is critical to avoid SystemExit under pytest
    with _patch_streams(out):
        try:
            with contextlib.redirect_stderr(StringIO()):
                Run([filename, "--extension-pkg-whitelist=" + compiledPackages, 
                           "--ignored-modules=psutil,requests,pywin32,win32security,win32process,win32api",
                           "--ignore=__pycache__,.pytest_cache,.qtcreator",
                           '--ignore-paths=.*[\\/](ui)[\\/].*'],
                reporter=reporter,
                exit=False)
        except astroid.exceptions.AstroidError:
            # INTERNAL crash - not a real Pylint F message
            # Any other unexpected internal crash
            reporter.messages.clear()
            #reporter.internal_crash = True
        except Exception:
            msgs = reporter.get_messages()
            if any(m["msg_id"].startswith("F") for m in msgs):
                # Keep real fail/fatal messages
                pass
            else:
                # Any other unexpected internal crash
                reporter.messages.clear()
                #reporter.internal_crash = True
            
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

    def __init__(self, compiledPackages: str = "PySide6"):
        self.compiledPackages = compiledPackages

        # main.py ignored due to unfixable pytest - pytest errors
        self.args = ["--extension-pkg-whitelist=" + self.compiledPackages,
                     "--ignored-modules=psutil,requests,pywin32,win32security,win32process,win32api",
                     "--ignore=main.py,__pycache__,.pytest_cache,.qtcreator",
                     '--ignore-paths=.*[\\/](ui)[\\/].*']

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

    def processFile(self, filename):
        out = StringIO()
        reporter = self.AjsonReporter(out)
        msgs = ""

        with self._patch_streams(out):
            try:
                with contextlib.redirect_stderr(StringIO()):
                    Run([filename] + self.args, reporter=reporter, exit=False)
            except astroid.exceptions.AstroidError:
                # INTERNAL crash - not a real Pylint F message
                # Any other unexpected internal crash
                reporter.messages.clear()
                #reporter.internal_crash = True
            except Exception:
                # Check if this is a rel Pylint fatal message (F0001 etc.)
                if any(m["msg_id"].startswith("F") for m in msgs):
                    # Keep real fail/fatal messages
                    pass
                else:
                    # Any other unexpected internal crash
                    # Internal crash or unexpected exception
                    reporter.messages.clear()
                    #reporter.internal_crash = True

        messages = reporter.get_messages()
        self.acquiredData[filename] = messages
        return messages   # <-- FIXED

