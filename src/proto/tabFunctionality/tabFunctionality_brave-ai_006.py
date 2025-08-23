from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLineEdit, QPushButton, QTextEdit, QLabel
)
from PySide6.QtCore import Qt
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QMainWindow Tab Order Example")
        self.resize(400, 300)

        # Central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Create widgets
        self.label = QLabel("Tab Order: LineEdit → Button → TextEdit")
        self.line_edit = QLineEdit("Start typing here")
        self.button = QPushButton("Click me with Tab!")
        self.text_edit = QTextEdit("Multi-line text (Tab will leave if set correctly)")

        # === Ensure focus policies are correct ===
        self.line_edit.setFocusPolicy(Qt.StrongFocus)
        self.button.setFocusPolicy(Qt.TabFocus)
        self.text_edit.setFocusPolicy(Qt.StrongFocus)

        # Add to layout
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.button)
        layout.addWidget(self.text_edit)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # === Set tab order: line_edit → button → text_edit ===
        QWidget.setTabOrder(self.line_edit, self.button)
        QWidget.setTabOrder(self.button, self.text_edit)

        # Optional: Set initial focus
        self.line_edit.setFocus()

        # Debug focus changes
        QApplication.instance().focusChanged.connect(self.on_focus_changed)

    def on_focus_changed(self, old, new):
        if new:
            print(f"Focus: {new}")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())   


