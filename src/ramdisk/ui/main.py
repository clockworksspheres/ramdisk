#!/usr/bin/env -S python -u

import datetime
import logging

from PySide6.QtCore import QCoreApplication, QEvent, QSize, Qt, Slot
from PySide6.QtGui import QCursor, QDragMoveEvent, QDropEvent, QFont
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea,
                               QApplication, QFrame, QLabel, QListWidget,
                               QListWidgetItem, QMainWindow, QPushButton,
                               QSizePolicy, QSpacerItem, QVBoxLayout, QWidget,
                               QMessageBox, QDialog, QDialogButtonBox,
                               QGraphicsDropShadowEffect)


import sys 

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
from ramdisk.lib.loggers import LogPriority
from ramdisk.ramdisk import RamDisk

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
        '''
        doesn't work for a ui_mainwindow...
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(5)
        shadow.setYOffset(5)
        shadow.setColor(Qt.gray)
        self.ui.setGraphicsEffect(shadow)
        '''
        # Create a drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)  # Adjust the blur radius for more or less shadow
        shadow.setColor(Qt.black)  # Set the color of the shadow
        shadow.setOffset(5, 5)     # Set the offset of the shadow (x, y)

        # Apply the shadow effect to the main window
        self.setGraphicsEffect(shadow)

        self.setStyleSheet("""
            MainWindow {
                border: 5px solid red;
                background-color: rgb(0,255,255);
                border-radius: 10px;
                box-shadow: 4px 4px 8px rgba(224, 224, 224, 0.5);
            }
        """)

        #####
        # Connect Button click signals to slots 
        self.ui.createPushButton.clicked.connect(self.createRamdisk)
        self.ui.debugPushButton.clicked.connect(self.notYetImplemented)
        self.ui.quitPushButton.clicked.connect(self.quit_application)
        self.ui.rListPushButton.clicked.connect(self.notYetImplemented)
    
        #####
        # Connect Button click signals to slots 
        self.ui.createPushButton.keyPressEvent = lambda event: keyPressEvent(event, parent, self.createRamdisk()) 
        self.ui.debugPushButton.keyPressEvent = lambda event: keyPressEvent(event, parent, self.notYetImplemented())
        self.ui.quitPushButton.keyPressEvent = lambda event: keyPressEvent(event, parent, self.quit_application())
        self.ui.rListPushButton.keyPressEvent = lambda event: keyPressEvent(event, parent, self.notYetImplemented())

        #####
        # connect slider to line edit
        self.ui.sizeHorizontalSlider.valueChanged.connect(self.update_line_edit)

        #####
        # connect line edit to slider

        #####
        # getMacosMemStatus.getAvailableMem
        self.getMemStatus = GetMemStatus()
        availableMem = self.getMemStatus.getAvailableMem()
        self.ui.sizeHorizontalSlider.setRange(0, availableMem)

        # CEnsure the inputs within the slider's range
        self.ui.sizeLineEdit.setValidator(QIntValidator(0, availableMem))
        self.ui.sizeLineEdit.textChanged.connect(self.update_slider)

        print("exiting init...")

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
        # Perform any necessary cleanup or confirmation actions here
        reply = QMessageBox.question(self, 'Message', 'Are you sure you want to quit?', 
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

    def createRamdisk(self):
        """
        Grab the values from the interface to create the ramdisk.
        """
        
        creds = False
        if sys.platform.startswith('darwin'):
            creds = True
        if sys.platform.startswith('linux'):
            window = _LocalAuth()
            '''
            makes all widgets inside the window shadowed - 
            what a MESS!!
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(10)
            shadow.setXOffset(5)
            shadow.setYOffset(5)
            shadow.setColor(Qt.gray)
            window.setGraphicsEffect(shadow)
            '''
            window.setStyleSheet("background-color: white; border-radius: 10px;")
        
            # Add drop shadow effect
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setColor(Qt.black)
            shadow.setOffset(0, 0)
            window.setGraphicsEffect(shadow)

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
            pass

        #####
        # Grab the mount point
        try:
            mountPoint = self.ui.mountLineEdit.text()
        except Exception as err:
            traceback.format_exc()
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
                if sys.platform.startswith('linux'):
                    #####
                    # create ramdisk with specific mountpoint
                    ramdisk = RamDisk(str(memSize), str(mountPoint), self.logger, passwd=self.passwd)
                    ramdisk.getNlogData()
                    ramdisk.getNprintData()
                else:
                    #####
                    # create ramdisk with specific mountpoint
                    ramdisk = RamDisk(str(memSize), str(mountPoint), self.logger)
                    ramdisk.getNlogData()
                    ramdisk.getNprintData()

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


