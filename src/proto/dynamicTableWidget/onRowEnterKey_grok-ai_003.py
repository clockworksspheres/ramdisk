import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt, Slot

class CustomTableWidget(QTableWidget):
    def __init__(self):
        super().__init__()

    def keyPressEvent(self, event):
        super().keyPressEvent(event)  # Call the parent class's keyPressEvent
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            current_row = self.currentRow()
            # Get data from all columns in the current row
            row_data = []
            for col in range(self.columnCount()):
                item = self.item(current_row, col)
                row_data.append(item.text() if item else "")
            # Call the slot with the row number and data from all columns
            self.on_enter_pressed(current_row, row_data)

    @Slot(int, list)
    def on_enter_pressed(self, row, row_data):
        # Slot to handle Enter key press for all columns in the row
        print(f"Enter pressed in row {row + 1}. Data: {row_data}")
        # Example action: Update all cells in the row
        for col, data in enumerate(row_data):
            new_item = QTableWidgetItem(f"Updated {data}")
            self.setItem(row, col, new_item)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QTableWidget Enter Key for All Columns in Row")
        self.setGeometry(100, 100, 600, 400)

        # Create the custom table widget
        self.table = CustomTableWidget()
        self.table.setRowCount(5)  # 5 rows
        self.table.setColumnCount(3)  # 3 columns
        self.table.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])

        # Populate the table with sample data
        for row in range(5):
            for col in range(3):
                item = QTableWidgetItem(f"Item {row + 1},{col + 1}")
                item.setFlags(item.flags() | Qt.ItemIsEditable)  # Make cells editable
                self.table.setItem(row, col, item)

        # Resize columns to content
        self.table.resizeColumnsToContents()

        # Set the table as the central widget
        self.setCentralWidget(self.table)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


