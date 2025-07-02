

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QPlainTextEdit, QVBoxLayout, QWidget
from PySide6.QtCore import QProcess

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Run Command with Root Privileges")
        self.setGeometry(100, 100, 600, 400)

        # Create a button to execute the command
        self.btn = QPushButton("Execute Command")
        self.btn.clicked.connect(self.start_process)

        # Create a text area to display the output
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.btn)
        layout.addWidget(self.text)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Initialize the QProcess
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)

    def start_process(self):
        self.text.appendPlainText("Executing command...")
        self.process.start("sudo", ["your_command", "arg1", "arg2"])  # Replace "your_command" and arguments as needed

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.text.appendPlainText(stdout)

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.text.appendPlainText(stderr)

    def process_finished(self):
        self.text.appendPlainText("Process finished.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

