import sys

from PySide6.QtCore import QCoreApplication, QEvent, QSize, Qt, Slot, QTimer
from PySide6.QtGui import QCursor, QDragMoveEvent, QDropEvent, QFont, QColor
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea,
                               QApplication, QFrame, QLabel, QListWidget,
                               QListWidgetItem, QMainWindow, QPushButton,
                               QSizePolicy, QSpacerItem, QVBoxLayout, QWidget,
                               QMessageBox, QDialog, QDialogButtonBox,
                               QGraphicsDropShadowEffect, QTableWidget,
                               QTableWidgetItem, QHeaderView, QLineEdit)

sys.path.append(r'../..')

from ramdisk.lib.run_commands import RunWith
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.commonRamdiskTemplate import RamDiskTemplate, NotValidForThisOS, BadRamdiskArguments
from ramdisk.ui.local_auth_widget import _LocalAuth

class testUi2UmountDisk(QDialog):
    


    def __init__(self, disk):
        self.passwd = ""
        window = _LocalAuth()

        window.credsSig.connect(self.getCreds)

        result = window.exec()
        # Check the result of the dialog
        print("\tDISK: " + disk)
        if result == window.accepted:
            print("Dialog accepted")
            eject(disk, self.logger, self.passwd)
                                
        else:
            print("Dialog rejected, will not unmount disk")

    @Slot(str, str)
    def getCreds(self, user, passwd):
        """
        Slot for getting the enered user and password information
        """
        self.user = user
        self.passwd = passwd
        #  print(passwd)



def  eject(mnt_point="", logger=False, password=""):
    '''
    mirror function for umount
    '''
    success = False
    if mnt_point:

        paths = ["/bin", "/usr/bin", "/sbin", "/usr/sbin", "/usr/local/bin", "/user/local/sbin"]

        #####
        # Look for the umount command
        umountFound = False
        umountPath = ""
        for path in paths:
            possibleFullPath = os.path.join(path, "umount")
            if os.path.exists(possibleFullPath):
                umountPath = possibleFullPath
                umountFound = True

        if not umountFound:
            raise SystemToolNotAvailable("Cannot find umount command...")

        #####
        # Run the umount command...
        runWith = RunWith(logger)
        command = [umountPath, mnt_point]
        runWith.setCommand(command)
        #runWith.communicate()
        retval, reterr, retcode = self.runWith.runWithSudo(password.strip())
        #retval, reterr, retcode = runWith.getNlogReturns()
        self.logger.log(lp.INFO, "RETURNS: " + retval)
        #if not reterr:
        if retval:
            success = True

    return success


if __name__=='__main__':

    app = QApplication(sys.argv)

    window = testUi2UmountDisk("/tmp/ram0")

    window.show()
    print("showing window...")
    window.raise_()
    print("raising_ window")
    sys.exit(app.exec())


