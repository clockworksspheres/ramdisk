import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PySide6.QtWidgets import QDialog, QDialogButtonBox

class InnerDialog(QDialog):
    """A simple dialog shown when a button is clicked."""
    def __init__(self, button_name):
        super().__init__()
        self.setWindowTitle(f"From {button_name}")
        
        layout = QVBoxLayout()
        layout.addWidget(QPushButton(f"This dialog opened from '{button_name}'"))
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)


class ExampleDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Default Button Example")

        layout = QVBoxLayout()

        # Buttons that open another dialog when clicked
        self.button1 = QPushButton("Open from Button 1")
        self.button1.setAutoDefault(True)
        self.button1.clicked.connect(lambda: self.open_inner_dialog("Button 1"))

        self.button2 = QPushButton("Open from Button 2")
        self.button2.setAutoDefault(True)
        self.button2.clicked.connect(lambda: self.open_inner_dialog("Button 2"))

        # Default button (activated by Enter)
        self.default_button = QPushButton("Open from Default Button (Press Enter)")
        self.default_button.setDefault(True)
        self.default_button.clicked.connect(lambda: self.open_inner_dialog("Default Button"))

        # Non-auto-default button
        self.normal_button = QPushButton("Open from Normal Button")
        self.normal_button.setAutoDefault(False)
        self.normal_button.clicked.connect(lambda: self.open_inner_dialog("Normal Button"))

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText("Submit")
        button_box.button(QDialogButtonBox.Cancel).setText("Cancel")

        button_box.button(QDialogButtonBox.Ok).setDefault(True)
        button_box.button(QDialogButtonBox.Ok).clicked.connect(lambda: self.open_inner_dialog("Submit"))
        button_box.button(QDialogButtonBox.Cancel).clicked.connect(lambda: self.open_inner_dialog("Cancel"))

        # Add widgets to layout
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        layout.addWidget(self.default_button)
        layout.addWidget(self.normal_button)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def open_inner_dialog(self, button_name):
        inner_dialog = InnerDialog(button_name)
        inner_dialog.exec()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")

        open_dialog_btn = QPushButton("Open Main Dialog")
        open_dialog_btn.clicked.connect(self.open_main_dialog)

        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(open_dialog_btn)
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_main_dialog(self):
        dialog = ExampleDialog()
        dialog.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())   


