import sys
import traceback
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QVBoxLayout, QLabel, QDialogButtonBox

sys.path.append("../..")

from ramdisk.ui.ui_local_auth_widget import Ui_LocalAuth
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority
from ramdisk.lib.run_commands_linux import RunWith


class InvalidInitParameterError(BaseException):
    """
    Custom Exception
    """
    def __init__(self, *args, **kwargs):
        BaseException.__init__(self, *args, **kwargs)


class _LocalAuth(QDialog):
    def __init__(self):
        super().__init__()

        self.rw = RunWith()

        self.ui = Ui_LocalAuth()
        self.ui.setupUi(self)

        self.logger = CyLogger()
        self.logger.initializeLogs()

        #####
        # Connect Button click signals to slots
        self.ui.buttonBox.accepted.connect(
               lambda: self.acceptSignal())
        self.ui.buttonBox.rejected.connect(
               lambda: self.reject())

    def acceptSignal(self):
        print("Command accepted...")

        #####
        # sudo -k
        try:
            self.rw.setCommand(["/usr/bin/sudo", "-k"])
            retout, reterr, retval = self.rw.communicate()
        except Exception as err:
            print("DamnItJim!!!")
            traceback.format_exc(err)

        print("sudo -k worked...")
        retval = 1
        #####
        # sudo ls -l
        try:
            self.rw.setCommand('/usr/bin/ls /tmp')

            user = self.ui.userLineEdit.text()
            passwd = self.ui.passLineEdit.text()
            retout, reterr, retval = self.rw.runWithSudo(passwd.strip())
        except Exception as err:
            print("DamnItJim!!!")
            traceback.format_exc(err)
        print("recode: " + str(retval))
        if not int(retval):
            # if recode == 0 - ie: command succeeded
            self.accept()
            print("Command run....")
        else:
            self.reject()

        self.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    print("started app...")

    rw = RunWith()

    window = _LocalAuth()

    result = window.exec()

    # Check the result of the dialog
    if result == QDialog.Accepted:
        print("Dialog accepted")
    else:
        print("Dialog rejected")
    sys.exit()
    """
    print("initiated window")
    window.show()
    print("showing window...")
    window.raise_()
    print("raising_ window")
    """
    sys.exit(app.exec())


