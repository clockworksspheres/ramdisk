from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QLabel
)
from PySide6.QtCore import Qt

import sys

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Tab Order Example with setTabOrder")

# Create layout
layout = QVBoxLayout()

# Create widgets
label = QLabel("Focus starts here. Press Tab to cycle through controls.")

line_edit = QLineEdit("Start typing here")
button1 = QPushButton("Button 1")
button2 = QPushButton("Button 2")

table = QTableWidget(2, 2)
table.setItem(0, 0, QTableWidgetItem("Cell 0,0"))
table.setItem(0, 1, QTableWidgetItem("Cell 0,1"))
table.setItem(1, 0, QTableWidgetItem("Cell 1,0"))
table.setItem(1, 1, QTableWidgetItem("Cell 1,1"))

# Add widgets to layout
layout.addWidget(label)
layout.addWidget(line_edit)
layout.addWidget(button1)
layout.addWidget(button2)
layout.addWidget(table)

window.setLayout(layout)

# === Set custom tab order using setTabOrder ===
QWidget.setTabOrder(line_edit, button1)   # After line_edit → button1
QWidget.setTabOrder(button1, button2)     # After button1 → button2
QWidget.setTabOrder(button2, table)       # After button2 → table

# Optional: Start focus on line_edit
line_edit.setFocus()

window.show()

app.exec()   

