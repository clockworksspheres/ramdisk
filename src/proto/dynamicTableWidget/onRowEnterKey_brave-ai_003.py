import sys
from PySide6.QtWidgets import (
    QApplication, QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout,
    QLabel, QWidget
)

class RowDialog(QDialog):
    """Dialog to display all contents of a selected row."""
    def __init__(self, row_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Row Details")
        self.resize(300, 100)

        layout = QVBoxLayout()

        for col_idx, value in enumerate(row_data):
            label = QLabel(f"Column {col_idx}: {value}")
            layout.addWidget(label)

        self.setLayout(layout)


class CustomTableWidget(QTableWidget):
    """Custom QTableWidget that shows a dialog when a row is clicked."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["Name", "Age"])
        self.populate_sample_data()

        # Connect click signal to handler
        self.itemClicked.connect(self.on_row_clicked)

    def populate_sample_data(self):
        data = [
            ["Alice", "30"],
            ["Bob", "25"],
            ["Charlie", "35"]
        ]
        self.setRowCount(len(data))
        for row, (name, age) in enumerate(data):
            self.setItem(row, 0, QTableWidgetItem(name))
            self.setItem(row, 1, QTableWidgetItem(age))

    def on_row_clicked(self, item):
        row = item.row()
        row_data = []

        # Collect all items in the row
        for col in range(self.columnCount()):
            cell_item = self.item(row, col)
            row_data.append(cell_item.text() if cell_item else "")

        # Show dialog with row contents
        dialog = RowDialog(row_data, self)
        dialog.exec()


# Main Application
app = QApplication(sys.argv)

# Create main window
window = QWidget()
window.setWindowTitle("Custom QTableWidget - Click Row to Show Dialog")
window.resize(400, 300)

# Create custom table
table = CustomTableWidget()

# Layout
layout = QVBoxLayout()
layout.addWidget(table)
window.setLayout(layout)

window.show()

sys.exit(app.exec())   


