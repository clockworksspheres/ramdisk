from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QApplication
from PySide6.QtCore import Qt
import sys

app = QApplication(sys.argv)

window = QWidget()
layout = QVBoxLayout()

line_edit = QLineEdit("Focus here first")
button = QPushButton("Next Button")

# Ensure focus policy allows tab
line_edit.setFocusPolicy(Qt.StrongFocus)
button.setFocusPolicy(Qt.TabFocus)
button.setFocusPolicy(Qt.StrongFocus)

layout.addWidget(line_edit)
layout.addWidget(button)
window.setLayout(layout)

# Set tab order: line_edit → button
QWidget.setTabOrder(line_edit, button)

window.show()

# Optional: set initial focus
line_edit.setFocus()

app.exec()   


