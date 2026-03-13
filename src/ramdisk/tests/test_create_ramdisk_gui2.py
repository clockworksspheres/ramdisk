#!/usr/bin/env python3

import re
import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

parent_dir = Path(__file__).parent
sys.path.append(str(parent_dir))

from qt_ci_test_harness import QtTestCase, SignalSpy

from ramdisk.ui.main import _CreateRamdisk
from ramdisk.lib.environment import Environment

class TestCreateRamdiskGUI(QtTestCase):

    def setUp(self):

        self.window = _CreateRamdisk()

        self.window.show()
        self.window.activateWindow()
        self.window.raise_()

        self.environment = Environment()

        self.process_events(100)

    def tearDown(self):

        self.window.close()
        self.process_events()


# ------------------------------------------------------
# Test create button
# ------------------------------------------------------

    @patch("ramdisk.ui.main.RamDisk")
    def test_create_button(self, mock_ramdisk):

        instance = MagicMock()

        instance.getNprintData.return_value = (
            True,
            "/mnt/test",
            "disk1"
        )

        mock_ramdisk.return_value = instance

        self.window.ui.mountLineEdit.setText("/mnt/test")
        self.window.ui.sizeHorizontalSlider.setValue(512)

        self.click(self.window.ui.createPushButton)

        mock_ramdisk.assert_called()


# ------------------------------------------------------
# Test pressing RETURN in mount field
# ------------------------------------------------------

    @patch("ramdisk.ui.main.RamDisk")
    def test_return_key_create(self, mock_ramdisk):

        instance = MagicMock()

        instance.getNprintData.return_value = (
            True,
            "/mnt/test",
            "disk1"
        )

        mock_ramdisk.return_value = instance

        self.window.ui.mountLineEdit.setText("/mnt/test")
        self.window.ui.sizeHorizontalSlider.setValue(256)

        self.key(self.window.ui.mountLineEdit, Qt.Key_Return)

        mock_ramdisk.assert_called()


# ------------------------------------------------------
# Test table add row
# ------------------------------------------------------

    def test_add_row(self):

        rows_before = self.window.ui.tableWidget.rowCount()

        self.window.add_row("disk1", "/mnt/test")

        rows_after = self.window.ui.tableWidget.rowCount()

        self.assertEqual(rows_after, rows_before + 1)


# ------------------------------------------------------
# Test TAB navigation from table back to mount field
# ------------------------------------------------------

    def test_table_tab_navigation(self):

        self.window.add_row("disk1", "/mnt/test")

        table = self.window.ui.tableWidget

        table.setFocus()
        table.setCurrentCell(0, 0)

        event = QKeyEvent(
            QEvent.KeyPress,
            Qt.Key_Tab,
            Qt.NoModifier
        )

        QApplication.sendEvent(table, event)

        self.process_events()

        osType = self.environment.getostype().strip()
        rhBased = 'Red Hat Enterprise Linux|AlmaLinux|Rocky Linux|CentOS|Fedora|'
        print("==========================")
        print(str(osType))
        print("==========================")
        if re.search(rhBased, osType):
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


# ------------------------------------------------------
# Test ENTER on table row opens dialog
# ------------------------------------------------------

    @patch("ramdisk.ui.main.getMountedData")
    @patch("ramdisk.ui.main.RamdiskCustomMessageDialog.exec")
    def test_table_enter_opens_dialog(self, mock_exec, mock_data):

        mock_exec.return_value = True
        mock_data.return_value = ["disk info"]

        self.window.add_row("disk1", "/mnt/test")

        table = self.window.ui.tableWidget

        table.setFocus()
        table.setCurrentCell(0, 0)

        self.key(table, Qt.Key_Return)

        mock_exec.assert_called()


# ------------------------------------------------------
# Test slider emits signal
# ------------------------------------------------------

    def test_slider_signal(self):

        spy = SignalSpy(
            self.window.ui.sizeHorizontalSlider.valueChanged
        )

        self.window.ui.sizeHorizontalSlider.setValue(128)

        self.process_events()

        self.assertGreater(spy.count(), 0)


# ------------------------------------------------------
# Test remove selected row
# ------------------------------------------------------

    @patch("ramdisk.ui.main.eject")
    def test_remove_row(self, mock_eject):

        self.window.add_row("disk1", "/mnt/test")

        table = self.window.ui.tableWidget
        table.selectRow(0)

        removed = self.window.remove()

        self.assertEqual(len(removed), 1)


# ------------------------------------------------------
# Test quit button closes window
# ------------------------------------------------------

    @patch("PySide6.QtWidgets.QMessageBox.question")
    def test_quit_button(self, mock_question):

        from PySide6.QtWidgets import QMessageBox

        mock_question.return_value = QMessageBox.Yes

        self.click(self.window.ui.quitPushButton)

        self.process_events()

        self.assertFalse(self.window.isVisible())


# ------------------------------------------------------
# Screenshot example if failure occurs
# ------------------------------------------------------

    def test_window_visible(self):

        if not self.window.isVisible():

            self.fail_with_screenshot(
                self.window,
                "window_visibility_failure"
            )


if __name__ == "__main__":

    app = QApplication.instance()

    if not app:
        app = QApplication(sys.argv)

    unittest.main(verbosity=2)

