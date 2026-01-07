from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
)
from PySide6.QtCore import Qt
import sys

# Create the application
app = QApplication(sys.argv)

# Create the main window
window = QWidget()
window.setWindowTitle("Tab from QLineEdit to QPushButton")

# Create layout
layout = QVBoxLayout()

# Create widgets
label = QLabel("Click in the text field, then press Tab to move to the button.")
line_edit = QLineEdit("Start here")
button1 = QPushButton("Button 1 - Press Tab to get here")
button2 = QPushButton("Button 2")

# === Critical: Ensure widgets can receive tab focus ===
line_edit.setFocusPolicy(Qt.StrongFocus)
button1.setFocusPolicy(Qt.TabFocus)
button2.setFocusPolicy(Qt.TabFocus)

# Add widgets to layout
layout.addWidget(label)
layout.addWidget(line_edit)
layout.addWidget(button1)
layout.addWidget(button2)
window.setLayout(layout)

# === Set tab order: line_edit → button1 → button2 ===
QWidget.setTabOrder(line_edit, button1)
QWidget.setTabOrder(button1, button2)

# Optional: Start with focus on line_edit
line_edit.setFocus()

# Show window
window.show()

# Optional: Debug focus changes
def on_focus_changed(old, new):
    if new:
        print(f"Focus: {new.text() if hasattr(new, 'text') else new}")

app.focusChanged.connect(on_focus_changed)

# Run the app
sys.exit(app.exec())   


