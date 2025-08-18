import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt, Slot

class CustomTableWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        # Initialize any additional setup if needed

    def keyPressEvent(self, event):
        super().keyPressEvent(event)  # Call the parent class's keyPressEvent
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            current_row = self.currentRow()
            current_column = self.currentColumn()
            # Emit a signal or call a slot with row and column information
            self.on_enter_pressed(current_row, current_column)

    @Slot(int, int)
    def on_enter_pressed(self, row, col):
        # This is the slot that gets called when Enter is pressed
        print(f"Enter pressed in row {row + 1}, column {col + 1}")
        # Example action: Update the cell content
        item = self.item(row, col)
        if item:
            item.setText(f"Updated {row + 1},{col + 1}")
        else:
            item = QTableWidgetItem(f"Updated {row + 1},{col + 1}")
            self.setItem(row, col, item)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QTableWidget Enter Key to Slot Example")
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

