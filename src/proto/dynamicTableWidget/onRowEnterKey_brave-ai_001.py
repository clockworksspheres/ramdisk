import sys
from PySide6.QtWidgets import (QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

def on_cell_activated(row, column):
    print(f"Cell activated at row {row}, column {column}")

app = QApplication(sys.argv)

# Create and configure the table widget
table = QTableWidget()
table.setRowCount(3)
table.setColumnCount(2)
table.setHorizontalHeaderLabels(["Column 1", "Column 2"])

# Populate some sample data
for row in range(3):
    for col in range(2):
        item = QTableWidgetItem(f"Item {row},{col}")
        table.setItem(row, col, item)

# Connect the cellActivated signal to the handler function
table.cellActivated.connect(on_cell_activated)

# Set up the main window
window = QWidget()
layout = QVBoxLayout()
layout.addWidget(table)
window.setLayout(layout)
window.show()

sys.exit(app.exec())   

