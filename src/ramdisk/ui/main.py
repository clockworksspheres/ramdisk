#!/usr/bin/env -S python -u

import datetime
import logging
import traceback


from PySide6.QtCore import QCoreApplication, QEvent, QSize, Qt, Slot
from PySide6.QtGui import QCursor, QDragMoveEvent, QDropEvent, QFont, QColor
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea,
                               QApplication, QFrame, QLabel, QListWidget,
                               QListWidgetItem, QMainWindow, QPushButton,
                               QSizePolicy, QSpacerItem, QVBoxLayout, QWidget,
                               QMessageBox, QDialog, QDialogButtonBox,
                               QGraphicsDropShadowEffect, QTableWidget,
                               QTableWidgetItem, QHeaderView)


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
from ramdisk.ui.ui_main import Ui_MainWindow
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
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Oops")

        self.button = QPushButton("Close")
        self.button.clicked.connect(self.accept)
        layout = QVBoxLayout()
        message = QLabel("Not Yet Implemented")
        layout.addWidget(message)
        layout.addWidget(self.button)
        self.setLayout(layout)


class CustomMessageDialog(QDialog):
    def __init__(self, message):
        super().__init__()
        self.setWindowTitle("Oops")

        self.button = QPushButton("Ok")
        self.button.setDefault(True)
        self.button.clicked.connect(self.accept)
        layout = QVBoxLayout()
        messageText = QLabel(f"{message}")
        layout.addWidget(messageText)
        layout.addWidget(self.button)
        self.setLayout(layout)


class _CreateRamdisk(QMainWindow):
    def __init__(self):
        super().__init__()

        '''   
    def __init__(self, parent: QMainWindow) -> None:
        QMainWindow.__init__(self)
        
    def __init__(self):
        super().__init__()
        '''
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.logger = CyLogger()
        self.logger.initializeLogs()

        self.getMemStatus = GetMemStatus()

        #####
        # Set default button
        self.ui.createPushButton.setDefault(True)
        self.ui.ejectPushButton.setAutoDefault(True)
        self.ui.debugPushButton.setAutoDefault(False)
        self.ui.quitPushButton.setAutoDefault(True)

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
        self.ui.tableWidget.activated.connect(self.show_mount_data)

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

        print("exiting init...")

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
                current_item = self.ui.tableWidget.currentItem()
                if current_item:
                    row = current_item.row()
                    row_data = []
                    for col in range(self.ui.tableWidget.columnCount()):
                        item = self.ui.tableWidget.item(row, col)
                        row_data.append(item.text() if item else "")
                    
                    data = getMountedData(row_data[0])

                    # show message box with mounted data
                    dlg = CustomMessageDialog(data[0])
                    #dlg.show()
                    #dlg.raise_()
                    if dlg.exec():
                        print("User clicked OK")
                    return True
                else:
                    print("No cell selected.")
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
                    if col == 1:
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
        """
        #message = ""
        device = ""

        selected_rows = self.ui.tableWidget.selectionModel().selectedRows()

        if not selected_rows:
            print("no rows selected")
            return []

        if selected_rows:
            # Remove rows in reverse order to avoid index shifting
            for index in sorted([row.row() for row in selected_rows], reverse=True):

                for col in range(self.ui.tableWidget.columnCount()):
                    item = self.ui.tableWidget.item(index, col)
                    if col == 1:
                        device = item.text()
                        print(str(f"{device}"))
        data = getMountedData(device)

        # show message box with mounted data
        dlg = CustomMessageDialog(data[0])
        dlg.show()
        dlg.raise_()
        if dlg.exec():
            print("User clicked OK")

        """
        reply = QMessageBox.question(self, 'Message', f"{data[0]}",
                                     QMessageBox.Ok)
        reply.setMinimumWidth(400)


        if reply == QMessageBox.Yes:
            event.accept()  # Let the window close
        else:
            event.ignore()  # Prevent the window from closing
        """

    def update_slider(self, text):
        try:
            availableMem = self.getMemStatus.getAvailableMem()
            self.ui.sizeHorizontalSlider.setRange(0, availableMem)
            value = int(text)
            self.ui.sizeHorizontalSlider.setValue(value)
        except ValueError:
            pass   

    def update_line_edit(self, value):
        availableMem = self.getMemStatus.getAvailableMem()
        self.ui.sizeHorizontalSlider.setRange(0, availableMem)
        self.ui.sizeLineEdit.setText(str(value) + "M")

    def quit_application(self):
        self.close()

    def closeEvent(self, event):
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
        self.user = user
        self.passwd = passwd
        #  print(passwd)

    def populateMountedInTable(self):
        """
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
            pass
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
                else:
                    #####
                    # create ramdisk with specific mountpoint
                    ramdisk = RamDisk(str(memSize), str(mountPoint), self.logger)
                    ramdisk.getNlogData()
                    success, mntPnt, device = ramdisk.getNprintData()

                self.add_row(device, mntPnt)


'''
def init_event_logger(path: str, fmt: str, debug: bool = False,
                      stdout: bool = False) -> None:
    """Initializes the event logger.
    - Set the path of the event log file
    - Set the format of the event log file
    - Set the debug level of the event log file
    - Set up the event logger
    """
    logging.basicConfig(
        filename=path,
        filemode="w",
        format=fmt,
        datefmt="%d-%b-%y %H:%M:%S",
        level=logging.DEBUG if debug else logging.INFO,
    )
    if stdout:
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
'''



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


