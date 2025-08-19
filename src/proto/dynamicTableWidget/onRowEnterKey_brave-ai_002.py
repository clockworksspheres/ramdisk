import sys
from PySide6.QtWidgets import (
    QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QMessageBox
)

def on_cell_activated(row, column):
    # Get the item at the activated cell
    item = table.item(row, column)
    if item:
        content = item.text()
    else:
        content = "Empty Cell"

    # Show a pop-up message box with the cell content
    QMessageBox.information(table, f"Cell Content (Row {row}, Col {column})", content)

app = QApplication(sys.argv)

# Create the main window and table
window = QWidget()
window.setWindowTitle("QTableWidget Enter Key Example")
table = QTableWidget()
table.setRowCount(3)
table.setColumnCount(2)
table.setHorizontalHeaderLabels(["Name", "Age"])

# Populate the table with sample data
data = [
    ["Alice", "30"],
    ["Bob", "25"],
    ["Charlie", "35"]
]

for row, (name, age) in enumerate(data):
    table.setItem(row, 0, QTableWidgetItem(name))
    table.setItem(row, 1, QTableWidgetItem(age))

# Connect the signal: triggered when Enter is pressed or cell is double-clicked
table.cellActivated.connect(on_cell_activated)

# Layout
layout = QVBoxLayout()
layout.addWidget(table)
window.setLayout(layout)
window.resize(300, 200)
window.show()

sys.exit(app.exec())   

