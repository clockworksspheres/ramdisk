import sys
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QLabel, QMessageBox, QDialog, QLineEdit, QFormLayout, QFileDialog
from PySide6.QtCore import QProcess

class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Enter Password')
        layout = QFormLayout()

        self.password_field = QLineEdit(self)
        self.password_field.setEchoMode(QLineEdit.Password)
        layout.addRow("Password:", self.password_field)

        self.setLayout(layout)
        self.accepted.connect(self.accept_password)

    def accept_password(self):
        self.password = self.password_field.text()

class RootCommandApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Execute Command with Root')
        self.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout()

        self.label = QLabel('Click the button to execute a command with root privileges.')
        layout.addWidget(self.label)

        self.button = QPushButton('Execute Command', self)
        self.button.clicked.connect(self.execute_root_command)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def execute_root_command(self):
        command = "ls /root"  # Example command that requires root privileges
        self.run_command_with_root(command)

    def run_command_with_root(self, command):
        dialog = PasswordDialog(self)
        if dialog.exec() == QDialog.Accepted:
            password = dialog.password
            self.run_sudo_command(command, password)

    def run_sudo_command(self, command, password):
        sudo_cmd = f"echo {password} | sudo -S {command}"
        process = QProcess(self)
        process.finished.connect(self.command_finished)
        process.start('sh', ['-c', sudo_cmd])

    def command_finished(self, exitCode, exitStatus):
        if exitStatus == QProcess.NormalExit and exitCode == 0:
            QMessageBox.information(self, 'Success', 'Command executed successfully.')
        else:
            QMessageBox.critical(self, 'Error', 'Command failed to execute.')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RootCommandApp()
    ex.show()
    sys.exit(app.exec())


