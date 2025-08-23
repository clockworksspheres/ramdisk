from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LineEdits & Buttons - Tab Example")
        self.resize(400, 400)

        # Central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout()

        # === Create LineEdits ===
        layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit("John Doe")

        layout.addWidget(QLabel("Email:"))
        self.email_edit = QLineEdit("john@example.com")

        layout.addWidget(QLabel("Phone:"))
        self.phone_edit = QLineEdit("+1 234 567 890")

        # Set focus policy for LineEdits
        for edit in [self.name_edit, self.email_edit, self.phone_edit]:
            edit.setFocusPolicy(Qt.StrongFocus)

        # Add line edits to layout
        layout.addWidget(self.name_edit)
        layout.addWidget(self.email_edit)
        layout.addWidget(self.phone_edit)

        # === Create Buttons ===
        self.btn_apply = QPushButton("Apply")
        self.btn_ok = QPushButton("OK")
        self.btn_cancel = QPushButton("Cancel")
        self.btn_clear = QPushButton("Clear")

        # Set focus policy for buttons
        for btn in [self.btn_apply, self.btn_ok, self.btn_cancel, self.btn_clear]:
            btn.setFocusPolicy(Qt.TabFocus)

        # Connect button actions
        self.btn_apply.clicked.connect(self.on_apply)
        self.btn_ok.clicked.connect(self.on_ok)
        self.btn_cancel.clicked.connect(self.on_cancel)
        self.btn_clear.clicked.connect(self.on_clear)

        # Add buttons to layout
        layout.addWidget(self.btn_apply)
        layout.addWidget(self.btn_ok)
        layout.addWidget(self.btn_cancel)
        layout.addWidget(self.btn_clear)

        # Set layout
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # === Set Tab Order ===
        QWidget.setTabOrder(self.name_edit, self.email_edit)
        QWidget.setTabOrder(self.email_edit, self.phone_edit)
        QWidget.setTabOrder(self.phone_edit, self.btn_apply)
        QWidget.setTabOrder(self.btn_apply, self.btn_ok)
        QWidget.setTabOrder(self.btn_ok, self.btn_cancel)
        QWidget.setTabOrder(self.btn_cancel, self.btn_clear)

        # Start focus on first field
        self.name_edit.setFocus()

        # Optional: Debug focus changes
        QApplication.instance().focusChanged.connect(self.on_focus_changed)

    def on_apply(self):
        QMessageBox.information(self, "Apply", "Settings applied!")

    def on_ok(self):
        QMessageBox.information(self, "OK", "Saved and closing...")
        self.close()

    def on_cancel(self):
        self.close()

    def on_clear(self):
        self.name_edit.clear()
        self.email_edit.clear()
        self.phone_edit.clear()

    def on_focus_changed(self, old, new):
        if new:
            name = getattr(new, 'text', lambda: type(new).__name__)()
            print(f"Focus → {name}")

# Run the app
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())   


