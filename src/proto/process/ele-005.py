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
        sudo_cmd = r'echo  ' + str(password) + ' | sudo -S ' + command
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

