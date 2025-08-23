from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLineEdit, QPushButton
)
from PySide6.QtCore import Qt
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multiple LineEdits and Buttons - Tab Order")
        self.resize(400, 300)

        # Central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Create line edits
        self.edit1 = QLineEdit("Field 1")
        self.edit2 = QLineEdit("Field 2")
        self.edit3 = QLineEdit("Field 3")

        # Create buttons
        self.btn1 = QPushButton("Button 1")
        self.btn2 = QPushButton("Button 2")
        self.btn3 = QPushButton("Button 3")

        # === Ensure focus policies ===
        for widget in [self.edit1, self.edit2, self.edit3]:
            widget.setFocusPolicy(Qt.StrongFocus)

        for widget in [self.btn1, self.btn2, self.btn3]:
            widget.setFocusPolicy(Qt.TabFocus)

        # Add widgets to layout
        layout.addWidget(self.edit1)
        layout.addWidget(self.edit2)
        layout.addWidget(self.edit3)
        layout.addWidget(self.btn1)
        layout.addWidget(self.btn2)
        layout.addWidget(self.btn3)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # === Set tab order: edit1 → edit2 → edit3 → btn1 → btn2 → btn3 ===
        QWidget.setTabOrder(self.edit1, self.edit2)
        QWidget.setTabOrder(self.edit2, self.edit3)
        QWidget.setTabOrder(self.edit3, self.btn1)
        QWidget.setTabOrder(self.btn1, self.btn2)
        QWidget.setTabOrder(self.btn2, self.btn3)

        # Optional: Start with focus on first field
        self.edit1.setFocus()

        # Debug: Print which widget has focus
        QApplication.instance().focusChanged.connect(self.on_focus_changed)

    def on_focus_changed(self, old, new):
        if new and hasattr(new, 'text'):
            print(f"Focused: {new.text()[:20]}")
        elif new:
            print(f"Focused: {type(new).__name__}")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())   


