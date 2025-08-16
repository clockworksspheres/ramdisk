import sys
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QDialogButtonBox

class ExampleDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Default Button Example")

        layout = QVBoxLayout()

        # Button that becomes default when focused (autoDefault is True by default)
        self.button1 = QPushButton("Auto-Default Button 1")
        self.button1.setAutoDefault(True)  # This is the default behavior

        # Another auto-default button
        self.button2 = QPushButton("Auto-Default Button 2")
        self.button2.setAutoDefault(True)

        # Explicitly set a default button (will show with strong frame immediately)
        self.default_button = QPushButton("Explicit Default Button")
        self.default_button.setDefault(True)  # This button is always the default

        # Button that is not auto-default
        self.non_default_button = QPushButton("Non Auto-Default Button")
        self.non_default_button.setAutoDefault(False)

        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        layout.addWidget(self.default_button)
        layout.addWidget(self.non_default_button)

        # Using QDialogButtonBox (AcceptRole button becomes default automatically)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setDefault(True)  # Explicitly set OK as default
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = ExampleDialog()
    dialog.exec()   

