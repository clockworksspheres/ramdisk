#!/usr/bin/env -S python -u
"""
"""
import os
import sys
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QVBoxLayout, QLabel, QDialogButtonBox

sys.path.append("../")

from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp

class CustomDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("HELLO!")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        message = QLabel("Something happened, is that OK?")
        layout.addWidget(message)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        self.logger = CyLogger(level=10)
        self.logger.initializeLogs()

        button = QPushButton("Press me for a dialog!")
        button.clicked.connect(self.button_clicked)
        self.setCentralWidget(button)

    def button_clicked(self, s):
        print("click", s)
        
        mytest = os.isatty(sys.stdin.fileno())
        #mytest = os.isatty(sys.stdout.fileno)
        #mytest = os.isatty()

        if mytest:
            self.logger.log(10, "We're running in the terminal people...")
        else:
            self.logger.log(10, "we're running in GUI mode...")

        dlg = CustomDialog()
        if dlg.exec():
            print("User clicked OK")
        else:
            print("User clicked Cancel")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()


