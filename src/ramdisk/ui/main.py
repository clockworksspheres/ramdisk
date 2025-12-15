#!/usr/bin/env -S python -u

import datetime
import logging
import traceback


from PySide6.QtCore import QCoreApplication, QEvent, QSize, Qt, Slot, QTimer
from PySide6.QtGui import QCursor, QDragMoveEvent, QDropEvent, QFont, QColor
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea,
                               QApplication, QFrame, QLabel, QListWidget,
                               QListWidgetItem, QMainWindow, QPushButton,
                               QSizePolicy, QSpacerItem, QVBoxLayout, QWidget,
                               QMessageBox, QDialog, QDialogButtonBox,
                               QGraphicsDropShadowEffect, QTableWidget,
                               QTableWidgetItem, QHeaderView, QLineEdit)


import sys 
'''
from PySide6.QtCore import Slot, Qt, QEvent
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QPushButton,
                               QVBoxLayout, QMessageBox, QDialog, QTableWidget,
                               QTableWidgetItem, QHeaderView, QAbstractItemView)
'''
sys.path.append("../..")

# from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QVBoxLayout, QLabel, QDialogButtonBox
# from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QIntValidator


#--- non-native python libraries in this source tree
from ramdisk.ui.ui_main_n import Ui_MainWindow
from ramdisk.ui.ui_not_yet_implemented import Ui_Dialog

from ramdisk.ui.validate import validateMntPntString
from ramdisk.ui.getValues import getMaxMemSize

from ramdisk.lib.dev.getMemStatus import GetMemStatus
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.RamDisk import RamDisk, eject, getMountedData, getMountedDisks
from ramdisk.config import DEFAULT_RAMDISK_SIZE

if sys.platform.startswith('linux'):
    from ramdisk.ui.local_auth_widget import _LocalAuth


class CustomDialog(QDialog):
    def __init__(self, parent=None):
        """
        Not yet implemented error dialog
        """
        super().__init__(parent)
        self.setWindowTitle("Oops")

        self.button = QPushButton("Close")
        self.button.clicked.connect(self.accept)
        layout = QVBoxLayout()
        message = QLabel("Not Yet Implemented")
        layout.addWidget(message)
        layout.addWidget(self.button)
        self.setLayout(layout)


class RamdiskCustomMessageDialog(QDialog):
    def __init__(self, parent=None, message=""):
        """
        Generic message dialog that shows the passed in message.
        """
        super().__init__(parent)

        # Set window title
        self.setWindowTitle("message")

        # Create layout
        layout = QVBoxLayout()

        # Add centered message label
        messageText = QLabel(f"{message}")
        messageText.setAlignment(Qt.AlignLeft)
        layout.addWidget(messageText)

        # Add single OK button
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        layout.addWidget(button_box)

        # Connect the OK button to the accept slot
        button_box.accepted.connect(self.accept)
        '''
        self.button = QPushButton("Ok")
        self.button.setDefault(True)
        self.button.accepted.connect(self.accept)
        layout.addWidget(self.button)
        '''
        # Set the layout
        self.setLayout(layout)


class _CreateRamdisk(QMainWindow):
    """
    The Main Window dialog for the ramdisk.
    """
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.logger = CyLogger()
        self.logger.initializeLogs()

        self.getMemStatus = GetMemStatus()

        #####
        # Set the default palette of items in the ui to default.
        self.ui.sizeLineEdit.setPalette(QApplication.palette())
        self.ui.mountLineEdit.setPalette(QApplication.palette())
        #self.ui.setPalette(QApplication.palette())

        #####
        # Set default button
        self.ui.createPushButton.setDefault(True)
        #self.ui.mountLineEdit.setDefault(True)
        #self.ui.ejectPushButton.setAutoDefault(True)
        #self.ui.debugPushButton.setAutoDefault(False)
        self.ui.quitPushButton.setAutoDefault(True)

        #####
        # Apply stylesheet for focus highlight
        self.ui.mountLineEdit.setStyleSheet("""
            QLineEdit {
                border: 1px solid gray;
                padding: 2px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d7;  /* macOS-like blue highlight */
                background-color: #e6f3ff;  /* Light blue background */
            }
        """)
        
        #####
        # Set Tab Order
        QWidget.setTabOrder(self.ui.mountLineEdit, self.ui.createPushButton)
        QWidget.setTabOrder(self.ui.createPushButton, self.ui.ejectPushButton)
        QWidget.setTabOrder(self.ui.ejectPushButton, self.ui.quitPushButton)
        QWidget.setTabOrder(self.ui.quitPushButton, self.ui.tableWidget)
        QWidget.setTabOrder(self.ui.tableWidget, self.ui.mountLineEdit)
        #self.setTabOrder

        #####
        # Set Focus Policy
        self.ui.mountLineEdit.setFocusPolicy(Qt.StrongFocus)
        self.ui.createPushButton.setFocusPolicy(Qt.StrongFocus)
        #self.ui.ejectPushButton.setFocusPolicy(Qt.TabFocus)
        self.ui.ejectPushButton.setFocusPolicy(Qt.StrongFocus)
        #self.ui.debugPushButton.setFocusPolicy(Qt.TabFocus)
        self.ui.debugPushButton.setFocusPolicy(Qt.StrongFocus)
        #self.ui.quitPushButton.setFocusPolicy(Qt.TabFocus)
        self.ui.quitPushButton.setFocusPolicy(Qt.StrongFocus)
        self.ui.tableWidget.setFocusPolicy(Qt.StrongFocus)
        self.ui.sizeHorizontalSlider.setFocusPolicy(Qt.NoFocus) # skip this in the tab order
        self.ui.sizeLineEdit.setFocusPolicy(Qt.NoFocus) # skip this in the tab order
        self.ui.debugPushButton.setFocusPolicy(Qt.NoFocus) # skip this in the tab order

        #self.ui.createPushButton.setDefault(True)

        #####
        # table keypress event signal
        self.ui.tableWidget.keyPressEvent = self.table_key_press_event

        #####
        # on enter in the line edit box, create the ramdisk
        self.ui.mountLineEdit.returnPressed.connect(self.createRamdisk)

        #####
        # Connect Button click signals to slots 
        self.ui.createPushButton.clicked.connect(self.createRamdisk)
        self.ui.debugPushButton.clicked.connect(self.notYetImplemented)
        self.ui.quitPushButton.clicked.connect(self.quit_application)
        self.ui.ejectPushButton.clicked.connect(self.remove)
        #self.ui.tableWidget.itemDoubleClicked.connect(self.show_mount_data)
        #self.ui.tableWidget.itemPressed.connect(self.show_mount_data)
        # Connect signal for debugging
        # self.ui.tableWidget.currentCellChanged.connect(self.on_cell_changed)

        #####
        # Connect Button click signals to slots 
        '''
        self.ui.createPushButton.keyPressEvent = lambda event: keyPressEvent(event, parent, self.createRamdisk()) 
        self.ui.debugPushButton.keyPressEvent = lambda event: keyPressEvent(event, parent, self.notYetImplemented())
        self.ui.quitPushButton.keyPressEvent = lambda event: keyPressEvent(event, parent, self.quit_application())
        self.ui.ejectPushButton.keyPressEvent = lambda event: keyPressEvent(event, parent, self.remove())
        # self.ui.tableWidget.keyPressedEvent = lambda event: keyPressEvent(event, parent, self.????())
        '''
        #####
        # connect slider to line edit
        self.ui.sizeHorizontalSlider.valueChanged.connect(self.update_line_edit)

        #####
        # connect line edit to slider

        # Set the default slider value
        self.ui.sizeHorizontalSlider.setValue(DEFAULT_RAMDISK_SIZE)

        #####
        # Set up the table to list ramdisks
        # self.ui.tableWidget.setColumnCount(4)
        # self.ui.tableWidget.setHorizontalHeaderLabels(["device", "mount point", "file system", "owner"])
        self.ui.tableWidget.setColumnCount(2)
        self.ui.tableWidget.setHorizontalHeaderLabels(["device", "mount point"])
        self.ui.tableWidget.setRowCount(0)

        # stretch columns to fit tableWidget size
        header = self.ui.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # enable row selection
        self.ui.tableWidget.setSelectionMode(QTableWidget.SingleSelection)
        self.ui.tableWidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.ui.tableWidget.doubleClicked.connect(self.show_mount_data)

        # set table items as non-editable
        self.ui.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # row counter
        self.row_counter = 0

        #####
        # getMacosMemStatus.getAvailableMem
        self.getMemStatus = GetMemStatus()
        availableMem = self.getMemStatus.getAvailableMem()
        self.ui.sizeHorizontalSlider.setRange(0, availableMem)
        # Set the default slider value
        self.ui.sizeHorizontalSlider.setValue(DEFAULT_RAMDISK_SIZE)

        # CEnsure the inputs within the slider's range
        self.ui.sizeLineEdit.setValidator(QIntValidator(0, availableMem))
        self.ui.sizeLineEdit.textChanged.connect(self.update_slider)

        #####
        # Populate the table with already created ramdisks
        self.populateMountedInTable()

        # Optional: Handle focus-in event for additional behavior
        self.ui.mountLineEdit.focusInEvent = self.on_line_edit_focus_in

        #####
        # from Grok - for macOS specific focus bugs
        QTimer.singleShot(0, self.ui.mountLineEdit.setFocus)

        # Apply stylesheets with heavy blue focus highlight and light blue tint (day mode)
        self.set_day_mode_styles()

        print("exiting init...")

    def on_line_edit_focus_in(self, event):
        """Custom focus-in event handler for QLineEdit."""
        # from Grok - for macOS specific focus bugs
        QTimer.singleShot(0, self.ui.mountLineEdit.setFocus)

        # Select all text when the QLineEdit gains focus (optional)
        self.ui.mountLineEdit.selectAll()
        super(QLineEdit, self.ui.mountLineEdit).focusInEvent(event)

    def table_key_press_event(self, event):
        """
        Custom key press event for QTableWidget to cycle back to mountLineEdit.
        
        When hitting a tab, if one is in the table, where to go from there.
        """
        if event.key() == Qt.Key_Tab:
            current_row = self.ui.tableWidget.currentRow()
            if current_row == self.ui.tableWidget.rowCount() - 1:
                self.ui.mountLineEdit.setFocus()
                return
        # Default table key handling (e.g., move to next cell)
        super(QTableWidget, self.ui.tableWidget).keyPressEvent(event)

    def on_cell_changed(current_row, current_col, prev_row, prev_col):
        print(f"Current: ({current_row}, {current_col}), Previous: ({prev_row}, {prev_col})")

    def add_row(self, device="", mntPnt="", filesystem="", username=""):
        """
        Add a row to the ramdisk list (created by this app)
        """
        # Insert a new row at the end of the list
        row_position = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(row_position)

        # populate the row with the mount data
        self.ui.tableWidget.setItem(row_position, 0, QTableWidgetItem(f"{device}"))
        self.ui.tableWidget.setItem(row_position, 1, QTableWidgetItem(f"{mntPnt}"))
        # self.ui.tableWidget.setItem(row_position, 2, QTableWidgetItem(f"{filesystem}"))
        # self.ui.tableWidget.setItem(row_position, 3, QTableWidgetItem(f"{username}"))

        # Set alternating row color
        color = QColor("#f0f0f0") if row_position % 2 == 0 else QColor("#ffffff")  # Light gray for even, white for odd
        for col in range(self.ui.tableWidget.columnCount()):
            item = self.ui.tableWidget.item(row_position, col)
            if item:
                item.setBackground(color)

        self.row_counter = self.row_counter + 1

    def keyPressEvent(self, event):
        '''
        On keypress -
            process enter/return
        '''

        if self.ui.tableWidget is self.focusWidget():
            # if event.key() == Qt.Key_Return:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                data = ""
                #current_item = self.ui.tableWidget.currentItem()
                current_row_index = self.ui.tableWidget.currentRow()
                print(f"current row {current_row_index}...........")
                if current_row_index >= 0:
                    if sys.platform.lower().startswith("darwin"):
                        column = 0
                    elif sys.platform.lower().startswith("linux"):
                        column = 1
                    elif sys.platform.lower().startswith("win32"):
                        column = 0
                    item = self.ui.tableWidget.item(current_row_index, column)  # Get first column item
                    device = item.text() if item else ""
                    data = getMountedData(device)
                else:
                    print("No Row Selected...")

                # show message box with mounted data
                dlg = RamdiskCustomMessageDialog(self, data[column])
                retval = dlg.exec()
                if retval:
                    print("User clicked OK, dialog accepted")
                else:
                    print("Dialog Rejected")
                # return True
            else:
                return super().keyPressEvent(event)
        else:
            return super().keyPressEvent(event)

    def remove(self):
        """
        remove ramdisk from list when unmounted
        """
        # remove the selected row (if any)
        selected_rows = self.ui.tableWidget.selectionModel().selectedRows()

        if not selected_rows:
            print("no rows selected")
            return []

        removed_data = []

        if selected_rows:
            # extract data from each cell in the row
            row_data = []
            # Remove rows in reverse order to avoid index shifting
            for index in sorted([row.row() for row in selected_rows], reverse=True):

                for col in range(self.ui.tableWidget.columnCount()):
                    item = self.ui.tableWidget.item(index, col)
                    row_data.append(item.text() if item else "")
                    #####
                    # Make sure to use the device column, not the mount point column.
                    if col == 1 and sys.platform.startswith('linux'):
                        window = _LocalAuth()

                        window.credsSig.connect(self.getCreds)
                        result = window.exec()
                        # Check the result of the dialog
                        if result == window.accepted:
                            print("Dialog accepted")
                            eject(item.text(), self.logger, self.passwd)
                            
                        else:
                            print("Dialog rejected")
                    else col == 0:
                        # windows and mac branch...
                       eject(item.text(), self.logger)
                removed_data.append(row_data)

                # remove the row
                self.ui.tableWidget.removeRow(index)
            else:
                print("No row selected")

        for data in removed_data:
            print(f"Removed row data: {data}")

        return removed_data

    def show_mount_data(self, device=""):
        """
        Make a call to the generic window dialog with a message containing the
        mount and device information of the passed in disk
        """
        #message = ""
        device = ""
        data = ""
        '''
        #current_item = self.ui.tableWidget.currentItem()
        current_row_index = self.ui.tableWidget.currentRow()
        if current_row_index >= 0:
            item = self.ui.tableWidget.item(current_row_index, 0)  # Get first column item
            device = item.text() if item else ""
        '''
        #current_item = self.ui.tableWidget.currentItem()
        current_row_index = self.ui.tableWidget.currentRow()
        print(f"current row {current_row_index}...........")
        if current_row_index >= 0:
            if sys.platform.lower().startswith("darwin"):
                column = 0
            elif sys.platform.lower().startswith("linux"):
                column = 1
            elif sys.platform.lower().startswith("win32"):
                column = 0
            item = self.ui.tableWidget.item(current_row_index, column)  # Get first column item
            device = item.text() if item else ""
            data = getMountedData(device)
        else:
            print("No Row Selected...")

        # show message box with mounted data
        dlg = RamdiskCustomMessageDialog(self, data[0])
        dlg.show()
        dlg.raise_()
        if dlg.exec():
            print("User clicked OK")

    def update_slider(self, text):
        """
        Update the slider, based on the passed in text
        """
        try:
            availableMem = self.getMemStatus.getAvailableMem()
            self.ui.sizeHorizontalSlider.setRange(0, availableMem)
            value = int(text)
            self.ui.sizeHorizontalSlider.setValue(value)
        except ValueError:
            pass   

    def update_line_edit(self, value):
        """
        Update the line edit information based on slider change
        """
        availableMem = self.getMemStatus.getAvailableMem()
        self.ui.sizeHorizontalSlider.setRange(0, availableMem)
        self.ui.sizeLineEdit.setText(str(value) + "M")

    def quit_application(self):
        """
        Quit the application
        """
        self.close()

    def closeEvent(self, event):
        """
        Once the close event is detected, pop up a dialog asking if you are sure
        you want to exit the app.
        """
        print("Entered the twilight zone....")
        # Perform any necessary cleanup or confirmation actions hered
        reply = QMessageBox.question(self, 'Message', 'Are you sure you want to quit?\n\nYour ramdisk list will be re-populated with current ramdisks.',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            event.accept()  # Let the window close
        else:
            event.ignore()  # Prevent the window from closing
        #event.accept()  # Let the window close
        print("Exiting the twilight zone!!!")        

    def notYetImplemented(self):
        """
        pop up a window indicating that this functionality is not yet 
        implemented...
        """
        # print("click", s)

        dlg = CustomDialog()
        dlg.show()
        dlg.raise_()
        if dlg.exec():
            print("User clicked OK")

    @Slot(str, str)
    def getCreds(self, user, passwd):
        """
        Slot for getting the enered user and password information
        """
        self.user = user
        self.passwd = passwd
        #  print(passwd)

    def populateMountedInTable(self):
        """
        Populate the table based on created ramdisks
        """
        print("Entering populateMountedInTable...")
        mountedDisks = {}
        try:
            mountedDisks = getMountedDisks()
            print(f"{mountedDisks}")
        except Exception as err:
            print(traceback.format_exc())
            print(str(err))

        #####
        # populate table
        for name, dev in mountedDisks.items():
            self.add_row(dev, name)
        
        print(f"attempted to populate previous ramdisks in table: {mountedDisks}")

    def createRamdisk(self):
        """
        Grab the values from the interface to create the ramdisk.
        """
        if sys.platform.startswith('darwin'):
            self.logger.log(lp.DEBUG, "Darwin doesn't need elevation to create a ramdisk")
        if sys.platform.startswith('linux'):
            window = _LocalAuth()

            window.credsSig.connect(self.getCreds)
            result = window.exec()
            # Check the result of the dialog
            if result == window.accepted:
                print("Dialog accepted")
            else:
                print("Dialog rejected")
        if sys.platform.startswith('win32'):
            self.logger.log(lp.DEBUG, "Darwin needs to be run elevated to create a ramdisk")
        #####
        # Grab the size
        try:
            memSize = self.ui.sizeHorizontalSlider.value()
        except ValueError as err:
            print("Ignored error: " + str(err))

        #####
        # Grab the mount point
        try:
            mountPoint = self.ui.mountLineEdit.text()
        except Exception as err:
            print(traceback.format_exc())
            print(str(err))

        if not memSize:
            #####
            # pop up a dialog saying can't create a ramdisk that small....
            print("No dice... no size parameter, not creating a ramdisk!")
        else:
            print("we have a size for memory..")
            if not mountPoint:
                #####
                # create ramdisk with randomized mountpoint
                if sys.platform.startswith('linux'):
                    print("Found Linux, creating linux ramdisk..." + self.passwd)
                    ramdisk = RamDisk(str(memSize), "", self.logger, mode=700, uid=None, gid=None, fstype="tmpfs", nr_inodes=None, nr_blocks=None, creds=False, passwd=self.passwd)
                else:
                    ramdisk = RamDisk(str(memSize), "", self.logger)
                ramdisk.getNlogData()
                ramdisk.getNprintData()
            else:
                success = False
                mntPnt = ""
                device = ""
                if sys.platform.startswith('linux'):
                    #####
                    # create ramdisk with specific mountpoint
                    ramdisk = RamDisk(str(memSize), str(mountPoint), self.logger, passwd=self.passwd)
                    ramdisk.getNlogData()
                    success, mntPnt, device = ramdisk.getNprintData()
                elif sys.platform.startswith('win32'):
                    #####
                    # create ramdisk with specific mountpoint
                    ramdisk = RamDisk(str(memSize), str(mountPoint), self.logger)
                    ramdisk.getNlogData()
                    success, mntPnt, device = ramdisk.getNprintData()
                else:
                    #####
                    # create ramdisk with specific mountpoint
                    ramdisk = RamDisk(str(memSize), str(mountPoint), self.logger)
                    ramdisk.getNlogData()
                    success, mntPnt, device = ramdisk.getNprintData()

                self.add_row(device, mntPnt)

    def set_day_mode_styles(self):
        """Apply stylesheets for day mode with heavy blue focus highlight and light blue tint."""
        self.ui.mountLineEdit.setStyleSheet("""
            QLineEdit {
                background: #ffffff;
                color: #000000;
                border: 1px solid #888888;
                border-radius: 4px;
                padding: 4px;
            }
            QLineEdit:focus {
                border: 3px solid #0078d7; /* Heavy blue border */
                background: #e6f3ff; /* Light blue tint */
            }
        """)

        self.ui.sizeLineEdit.setStyleSheet("""
            QLineEdit {
                background: #ffffff;
                color: #000000;
                border: 1px solid #888888;
                border-radius: 4px;
                padding: 4px;
            }
            QLineEdit:focus {
                border: 3px solid #0078d7; /* Heavy blue border */
                background: #e6f3ff; /* Light blue tint */
            }
        """)

        self.ui.ejectPushButton.setStyleSheet("""
            QPushButton {
                background: #e0e0e0;
                color: #000000;
                border: 1px solid #888888;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:focus {
                border: 3px solid #0078d7; /* Heavy blue border */
                background: #e6f3ff; /* Light blue tint */
            }
            QPushButton:hover {
                background: #d0d0d0;
            }
        """)

        self.ui.quitPushButton.setStyleSheet("""
            QPushButton {
                background: #e0e0e0;
                color: #000000;
                border: 1px solid #888888;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:focus {
                border: 3px solid #0078d7; /* Heavy blue border */
                background: #e6f3ff; /* Light blue tint */
            }
            QPushButton:hover {
                background: #d0d0d0;
            }
        """)

        self.ui.tableWidget.setStyleSheet("""
            QTableWidget {
                background: #ffffff;
                color: #000000;
                border: 1px solid #888888;
                border-radius: 4px;
                gridline-color: #888888;
            }
            QTableWidget::item {
                border: none;
            }
            QTableWidget::item:selected {
                background: #0078d7; /* Blue selection */
                color: #ffffff;
            }
            QTableWidget:focus {
                border: 3px solid #0078d7; /* Heavy blue border */
            }
        """)
        self.setStyleSheet("QMainWindow { background: #f0f0f0; }")  # Light background

    def set_night_mode_styles(self):
        """Apply stylesheets for night mode with heavy blue focus highlight and light blue tint."""
        self.ui.mountLineEdit.setStyleSheet("""
            QLineEdit {
                background: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }
            QLineEdit:focus {
                border: 3px solid #0078d7; /* Heavy blue border */
                background: #2f4a6d; /* Darker light blue tint */
            }
        """)
        self.ui.sizeLineEdit.setStyleSheet("""
            QLineEdit {
                background: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }
            QLineEdit:focus {
                border: 3px solid #0078d7; /* Heavy blue border */
                background: #2f4a6d; /* Darker light blue tint */
            }
        """)
        self.ui.createPushButton.setStyleSheet("""
            QPushButton {
                background: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }
            QLineEdit:focus {
                border: 3px solid #0078d7; /* Heavy blue border */
                background: #2f4a6d; /* Darker light blue tint */
            }
            QPushButton:hover {
                background: #4a4a4a;
            }
        """)
        self.ui.ejectPushButton.setStyleSheet("""
            QPushButton {
                background: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }
            QLineEdit:focus {
                border: 3px solid #0078d7; /* Heavy blue border */
                background: #2f4a6d; /* Darker light blue tint */
            }
            QPushButton:hover {
                background: #4a4a4a;
            }
        """)
        self.ui.quitPushButton.setStyleSheet("""
            QPushButton {
                background: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }
            QLineEdit:focus {
                border: 3px solid #0078d7; /* Heavy blue border */
                background: #2f4a6d; /* Darker light blue tint */
            }
            QPushButton:hover {
                background: #4a4a4a;
            }
        """)
        self.ui.tableWidget.setStyleSheet("""
            QTableWidget {
                background: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                gridline-color: #555555;
            }
            QTableWidget::item {
                border: none;
            }
            QTableWidget::item:selected {
                background: #0078d7; /* Blue selection */
                color: #ffffff;
            }
            QTableWidget:focus {
                border: 3px solid #0078d7; /* Heavy blue border */
            }
        """)
        self.setStyleSheet("QMainWindow { background: #1e1e1e; }")  # Dark background


if __name__=="__main__":
    app = QApplication(sys.argv)
    """
    # Set up event logger
    init_event_logger(
        os.path.join(get_current_directory(), "event.log"),
        "%(asctime)s - %(levelname)s - %(message)s",
        stdout=True,
        debug=True if "--debug" in sys.argv else False,
    )
    """
    print("started app...")
    window = _CreateRamdisk()
    print("initiated window")
    window.show()
    print("showing window...")
    window.raise_()
    print("raising_ window")
    sys.exit(app.exec())

