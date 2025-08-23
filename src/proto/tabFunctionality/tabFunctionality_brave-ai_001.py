from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem

app = QApplication([])
window = QWidget()
layout = QVBoxLayout()

# Create widgets
line_edit = QLineEdit("Edit me")
button1 = QPushButton("Button 1")
button2 = QPushButton("Button 2")
table = QTableWidget(3, 2)
table.setItem(0, 0, QTableWidgetItem("Cell 0,0"))
table.setItem(1, 0, QTableWidgetItem("Cell 1,0"))

# Add to layout in desired tab order
layout.addWidget(line_edit)
layout.addWidget(button1)
layout.addWidget(button2)
layout.addWidget(table)

window.setLayout(layout)
window.show()

app.exec()   


