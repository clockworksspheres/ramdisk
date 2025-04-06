
import sys
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QVBoxLayout, QLabel, QDialogButtonBox

sys.path.append("../..")

from ramdisk.ui.ui_local_auth import Ui_LocalAuth
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority
from ramdisk.lib.run_commands_linux import RunWith

class InvalidInitParameterError(BaseException):
    """
    Custom Exception
    """
    def __init__(self, *args, **kwargs):
        BaseException.__init__(self, *args, **kwargs)


class _LocalAuth(QMainWindow):
    def __init__(self, runWith):
        super().__init__()

        self.rw = runWith
        if isinstance(self.rw, RunWith):
            print("We are good to go Huston...")
        else:
            raise InvalidInitParameterError("Please pass in valid parameters...")

        self.ui = Ui_LocalAuth()
        self.ui.setupUi(self)

        self.logger = CyLogger()
        self.logger.initializeLogs()

        #####
        # Connect Button click signals to slots 
        self.ui.buttonBox.accepted.connect(
               lambda: self.accept())
        self.ui.buttonBox.rejected.connect(
               lambda: self.reject())

    def accept(self):
        print("Command accepted...")

    '''def reject(self):
        print("Command rejected...")
        self
    '''

if __name__=="__main__":
    app = QApplication(sys.argv)
    print("started app...")

    rw = RunWith()

    window = _LocalAuth(rw)

    print("initiated window")
    window.show()
    print("showing window...")
    window.raise_()
    print("raising_ window")
    sys.exit(app.exec())

    
