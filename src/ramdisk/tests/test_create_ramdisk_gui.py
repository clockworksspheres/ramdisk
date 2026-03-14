import re
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

if sys.platform.lower().startswith("linux"):
    #####
    # This must be set before Pyside6 gets loaded...
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PySide6.QtCore import Qt

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

parent_dir = Path(__file__).parent
sys.path.append(str(parent_dir))

from qt_ci_test_harness import QtTestCase, SignalSpy
from ramdisk.ui.main import _CreateRamdisk
from ramdisk.lib.environment import Environment


class TestCreateRamdisk(QtTestCase):

    def setUp(self):

        self.window = _CreateRamdisk()
        self.window.show()

        self.process_events()
        self.environment = Environment()

    def tearDown(self):

        self.window.close()
        self.process_events()


# ---------------------------------------------------
# Button click test
# ---------------------------------------------------

    @patch("ramdisk.ui.main.RamDisk")
    def test_create_button(self, mock_ramdisk):

        instance = MagicMock()
        instance.getNprintData.return_value = (True, "/mnt/test", "disk1")

        mock_ramdisk.return_value = instance

        self.window.ui.mountLineEdit.setText("/mnt/test")
        self.window.ui.sizeHorizontalSlider.setValue(512)

        self.click(self.window.ui.createPushButton)

        mock_ramdisk.assert_called()


# ---------------------------------------------------
# Enter key triggers create
# ---------------------------------------------------

    @patch("ramdisk.ui.main.RamDisk")
    def test_return_key_create(self, mock_ramdisk):

        instance = MagicMock()
        instance.getNprintData.return_value = (True, "/mnt/test", "disk1")

        mock_ramdisk.return_value = instance

        self.window.ui.mountLineEdit.setText("/mnt/test")

        self.key(self.window.ui.mountLineEdit, Qt.Key_Return)

        mock_ramdisk.assert_called()


# ---------------------------------------------------
# Table row add
# ---------------------------------------------------

    def test_add_row(self):

        rows = self.window.ui.tableWidget.rowCount()

        self.window.add_row("disk1", "/mnt/test")

        self.assertEqual(
            self.window.ui.tableWidget.rowCount(),
            rows + 1
        )


# ---------------------------------------------------
# Table keyboard navigation
# ---------------------------------------------------
    @unittest.skipIf(sys.platform.lower().startswith("linux"), "Skip test on Linux")
    def test_table_tab_navigation(self):

        self.window.add_row("disk1", "/mnt/test")

        table = self.window.ui.tableWidget

        table.setFocus()
        table.selectRow(0)

        ####
        # Appears not to work in a Jenkins environment on macOS and Linux
        self.key(table, Qt.Key_Tab)

        osType = self.environment.getostype().strip()
        # linBased = 'Red Hat Enterprise Linux|AlmaLinux|Rocky Linux|CentOS|Fedora|Debian|macOS'
        linBased = 'Red Hat Enterprise Linux|Fedora'
        print("==========================")
        print(str(osType))
        print("==========================")
        if re.search(linBased, osType):
            print("==========================")
            print("RH Based")
            print("==========================")
            self.assertTrue(
                self.window.ui.mountLineEdit.hasFocus()
                # self.window.ui.tableWidget.hasFocus()
            )
        else:
            self.assertTrue(
                # self.window.ui.mountLineEdit.hasFocus()
                self.window.ui.tableWidget.hasFocus()
            )

# ---------------------------------------------------
# Signal spy example
# ---------------------------------------------------

    def test_slider_signal(self):

        spy = SignalSpy(
            self.window.ui.sizeHorizontalSlider.valueChanged
        )

        self.window.ui.sizeHorizontalSlider.setValue(100)

        self.process_events()

        self.assertGreater(spy.count(), 0)


# ---------------------------------------------------
# Screenshot on failure example
# ---------------------------------------------------

    def test_screenshot_example(self):

        try:

            self.assertTrue(self.window.isVisible())

        except AssertionError:

            self.fail_with_screenshot(self.window, "visibility_failure")


