from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton
from PySide6.QtCore import Qt
import sys

app = QApplication(sys.argv)
window = QWidget()
layout = QVBoxLayout()

# Create widgets
line_edit = QLineEdit("Click here, then press Tab")
button1 = QPushButton("Button 1")
button2 = QPushButton("Button 2")

# === Fix focus policy ===
line_edit.setFocusPolicy(Qt.StrongFocus)
button1.setFocusPolicy(Qt.TabFocus)
button2.setFocusPolicy(Qt.TabFocus)

# === Set tab order ===
QWidget.setTabOrder(line_edit, button1)
QWidget.setTabOrder(button1, button2)

# Add to layout
layout.addWidget(line_edit)
layout.addWidget(button1)
layout.addWidget(button2)
window.setLayout(layout)

window.show()

# Optional: set initial focus
line_edit.setFocus()

app.exec()   


