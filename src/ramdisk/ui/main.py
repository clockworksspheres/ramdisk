#!/usr/bin/env -S python -u

import datetime
import logging

from PySide6.QtCore import QCoreApplication, QEvent, QSize, Qt, Slot
from PySide6.QtGui import QCursor, QDragMoveEvent, QDropEvent, QFont
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea,
                               QApplication, QFrame, QLabel, QListWidget,
                               QListWidgetItem, QMainWindow, QPushButton,
                               QSizePolicy, QSpacerItem, QVBoxLayout, QWidget,
                               QMessageBox, QDialog, QDialogButtonBox)


import sys 
# from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QVBoxLayout, QLabel, QDialogButtonBox
# from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QIntValidator


from ui_main import Ui_MainWindow
from ui_not_yet_implemented import Ui_Dialog

from validate import validateMntPntString
from getValues import getMaxMemSize

sys.path.append("../..")

#--- non-native python libraries in this source tree
from ramdisk.lib.dev.getMemStatus import GetMemStatus


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

        #####
        # Connect Button click signals to slots 
        self.ui.createPushButton.clicked.connect(
               lambda: self.notYetImplemented())
        self.ui.debugPushButton.clicked.connect(
               lambda: self.notYetImplemented())
        self.ui.quitPushButton.clicked.connect(
               lambda: self.quit_application())
        self.ui.rListPushButton.clicked.connect(
               lambda: self.notYetImplemented())
    
        #####
        # Connect Button click signals to slots 
        self.ui.createPushButton.keyPressEvent = lambda event: keyPressEvent(event, parent, self.notYetImplemented()) 
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


