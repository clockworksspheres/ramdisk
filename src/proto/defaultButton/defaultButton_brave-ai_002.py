import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PySide6.QtWidgets import QDialog, QDialogButtonBox

class ExampleDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Default Button Example")

        layout = QVBoxLayout()

        # Buttons with autoDefault enabled (default behavior)
        self.button1 = QPushButton("Auto-Default Button 1")
        self.button1.setAutoDefault(True)

        self.button2 = QPushButton("Auto-Default Button 2")
        self.button2.setAutoDefault(True)

        # Explicit default button (always shown as default, activated by Enter)
        self.default_button = QPushButton("Submit (Default)")
        self.default_button.setDefault(True)

        # Non-auto-default button
        self.non_default_button = QPushButton("Normal Button")
        self.non_default_button.setAutoDefault(False)

        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        layout.addWidget(self.default_button)
        layout.addWidget(self.non_default_button)

        # Dialog button box with OK as default
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText("Submit")
        button_box.button(QDialogButtonBox.Cancel).setText("Close")

        # Ensure OK is the default button
        button_box.button(QDialogButtonBox.Ok).setDefault(True)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window - Open Dialog Example")

        # Button to open the dialog
        open_dialog_btn = QPushButton("Open Dialog")
        open_dialog_btn.clicked.connect(self.open_dialog)

        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(open_dialog_btn)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def open_dialog(self):
        dialog = ExampleDialog()
        result = dialog.exec()
        if result == QDialog.Accepted:
            print("Dialog accepted (Submit clicked)")
        else:
            print("Dialog canceled (Close clicked)")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())   

