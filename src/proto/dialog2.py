import sys
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QVBoxLayout, QLabel, QDialogButtonBox

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
        button = QPushButton("Press me for a dialog!")
        button.clicked.connect(self.button_clicked)
        self.setCentralWidget(button)

    def button_clicked(self, s):
        print("click", s)
        dlg = CustomDialog()
        if dlg.exec():
            print("User clicked OK")
        else:
            print("User clicked Cancel")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

