import sys
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QVBoxLayout, QLabel

class CustomDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("HELLO!")

        self.button = QPushButton("Close")
        self.button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        message = QLabel("Something happened, is that OK?")
        layout.addWidget(message)
        layout.addWidget(self.button)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        button = QPushButton("Press me for a dialog!")
        button.clicked.connect(self.button_clicked)
        self.setCentralWidget(button)

    def button_clicked(self):
        dlg = CustomDialog()
        if dlg.exec():
            print("User clicked Close")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

