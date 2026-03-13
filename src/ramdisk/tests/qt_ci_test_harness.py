#!/usr/bin/env python3

"""
Advanced PySide6 CI Test Harness
--------------------------------

Features
• Creates QApplication automatically
• Forces offscreen mode
• Disables modal dialogs
• Logs Qt signals
• Processes timers safely
• Screenshot on failure
• Widget tree dump
• Qt signal spying
• CI-safe for Jenkins
"""

import os
import sys
import unittest
import logging
from unittest.mock import patch

#####
# This must be set before Pyside6 gets loaded...
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
    QDialog,
    QWidget
)

from PySide6.QtCore import (
    QCoreApplication,
    QObject,
    Signal
)

from PySide6.QtTest import QTest


# ---------------------------------------------------
# Force headless Qt
# ---------------------------------------------------

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_LOGGING_RULES", "*.debug=false")


# ---------------------------------------------------
# Logging
# ---------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)

logger = logging.getLogger("qt-tests")


# ---------------------------------------------------
# QApplication factory
# ---------------------------------------------------

def get_qapp():

    app = QApplication.instance()

    if app is None:
        logger.info("Creating QApplication")
        app = QApplication(sys.argv)

    return app


# ---------------------------------------------------
# Qt Signal Logger
# ---------------------------------------------------

class QtSignalLogger(QObject):

    def __init__(self):
        super().__init__()
        self.events = []

    def log(self, *args):
        logger.info(f"QtSignal: {args}")
        self.events.append(args)


def connect_signal_logger(signal):

    logger_obj = QtSignalLogger()
    signal.connect(logger_obj.log)

    return logger_obj


# ---------------------------------------------------
# Signal Spy (similar to QSignalSpy)
# ---------------------------------------------------

class SignalSpy(QObject):

    def __init__(self, signal):

        super().__init__()
        self.events = []

        signal.connect(self._capture)

    def _capture(self, *args):

        self.events.append(args)

    def count(self):

        return len(self.events)

    def last(self):

        if self.events:
            return self.events[-1]
        return None


# ---------------------------------------------------
# Prevent modal dialogs
# ---------------------------------------------------

class DialogPatcher:

    def __init__(self):
        self.patches = []

    def start(self):

        self.patches = [

            patch.object(QDialog, "exec", return_value=True),

            patch.object(
                QMessageBox,
                "question",
                return_value=QMessageBox.Yes
            ),

            patch.object(
                QMessageBox,
                "information",
                return_value=QMessageBox.Ok
            ),

            patch.object(
                QMessageBox,
                "warning",
                return_value=QMessageBox.Ok
            ),

            patch.object(
                QMessageBox,
                "critical",
                return_value=QMessageBox.Ok
            )
        ]

        for p in self.patches:
            p.start()

    def stop(self):

        for p in self.patches:
            p.stop()


# ---------------------------------------------------
# Widget Tree Dump
# ---------------------------------------------------

def dump_widget_tree(widget, indent=0):

    print(" " * indent + f"{widget.__class__.__name__}")

    for child in widget.findChildren(QWidget):
        dump_widget_tree(child, indent + 2)


# ---------------------------------------------------
# Screenshot on failure
# ---------------------------------------------------

def save_screenshot(widget, name):

    try:

        os.makedirs("test_screenshots", exist_ok=True)

        pixmap = widget.grab()

        filename = f"test_screenshots/{name}.png"

        pixmap.save(filename)

        logger.info(f"Saved screenshot: {filename}")

    except Exception as e:

        logger.warning(f"Screenshot failed: {e}")


# ---------------------------------------------------
# Base Qt Test Case
# ---------------------------------------------------

class QtTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.app = get_qapp()

        cls.dialogs = DialogPatcher()
        cls.dialogs.start()

        logger.info("QtTestCase setup complete")

    @classmethod
    def tearDownClass(cls):

        cls.dialogs.stop()

        logger.info("QtTestCase teardown")

    def process_events(self, delay=50):

        QTest.qWait(delay)
        QCoreApplication.processEvents()

    def click(self, widget):

        from PySide6.QtCore import Qt

        QTest.mouseClick(widget, Qt.LeftButton)
        self.process_events()

    def key(self, widget, key):

        QTest.keyClick(widget, key)
        self.process_events()

    def wait(self, ms=50):

        QTest.qWait(ms)

    def assertWidgetTree(self, widget):

        dump_widget_tree(widget)

    def fail_with_screenshot(self, widget, name="failure"):

        save_screenshot(widget, name)
        self.fail("GUI test failed")


