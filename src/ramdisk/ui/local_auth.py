
import sys
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QVBoxLayout, QLabel, QDialogButtonBox

sys.path.append("../..")

from ramdisk.ui.ui_local_auth import Ui_LocalAuth
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority


class _LocalAuth(QMainWindow):
    def __init__(self):
        super().__init__()

        '''   
    def __init__(self, parent: QMainWindow) -> None:
        QMainWindow.__init__(self)
        
    def __init__(self):
        super().__init__()
        '''
        self.ui = Ui_LocalAuth()
        self.ui.setupUi(self)

        self.logger = CyLogger()
        self.logger.initializeLogs()

        #####
        # Connect Button click signals to slots 
        self.ui.buttonbox.accepted.connect(
               lambda: self.authenticateCommand())
        self.ui.buttonbox.rejected.connect(
               lambda: self.rejectCommand())

    def authenticateCommand(self):
        print("Command accepted...")

    def rejectCommand(self):
        print("Command rejected...")


if __name__=="__main__":
    app = QApplication(sys.argv)
    print("started app...")
    
    window = _LocalAuth()

    print("initiated window")
    window.show()
    print("showing window...")
    window.raise_()
    print("raising_ window")
    sys.exit(app.exec())

    
