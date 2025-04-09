import sys
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QLabel, QLineEdit, QMessageBox, QFormLayout
from PySide6.QtCore import QProcess

class RootCommandApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Execute Command with Root')
        self.setGeometry(100, 100, 400, 200)

        layout = QFormLayout()

        self.command_field = QLineEdit(self)
        layout.addRow("Command:", self.command_field)

        self.password_field = QLineEdit(self)
        self.password_field.setEchoMode(QLineEdit.Password)
        layout.addRow("Password:", self.password_field)

        self.button = QPushButton('Execute Command', self)
        self.button.clicked.connect(self.execute_root_command)
        layout.addRow(self.button)

        self.setLayout(layout)

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.command_finished)

    def execute_root_command(self):
        command = self.command_field.text().strip()
        password = self.password_field.text().strip()

        if not command:
            QMessageBox.critical(self, 'Error', 'Please enter a command.')
            return

        if not password:
            QMessageBox.critical(self, 'Error', 'Please enter your password.')
            return

        self.run_sudo_command(command, password)

    def run_sudo_command(self, command, password):
        #####
        # single quotes around password to account for special characters
        # in password..
        sudo_cmd = r'echo  ' + "'" + password + "'" + ' | sudo -S ' + command
        
        self.process.start('sh', ['-c', sudo_cmd])

    def command_finished(self, exitCode, exitStatus):
        if exitStatus == QProcess.NormalExit and exitCode == 0:
            QMessageBox.information(self, 'Success', 'Command executed successfully.')
        else:
            QMessageBox.critical(self, 'Error', 'Command failed to execute.')

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        #self.text.appendPlainText(stdout)
        print(stdout)

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        #self.text.appendPlainText(stderr)
        print(stderr)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RootCommandApp()
    ex.show()
    sys.exit(app.exec())

