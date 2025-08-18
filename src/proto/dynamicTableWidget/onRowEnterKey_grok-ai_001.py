import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt

class CustomTableWidget(QTableWidget):
    def keyPressEvent(self, event):
        super().keyPressEvent(event)  # Call the parent class's keyPressEvent
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            current_row = self.currentRow()
            current_column = self.currentColumn()
            # Check if there is a next row
            if current_row + 1 < self.rowCount():
                self.setCurrentCell(current_row + 1, current_column)
            else:
                # Optionally, loop back to the first row or do nothing
                self.setCurrentCell(0, current_column)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QTableWidget Return Key Example")
        self.setGeometry(100, 100, 600, 400)

        # Create the custom table widget
        self.table = CustomTableWidget()
        self.table.setRowCount(5)  # 5 rows
        self.table.setColumnCount(3)  # 3 columns
        self.table.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])

        # Populate the table with sample data
        for row in range(5):
            for col in range(3):
                item = QTableWidgetItem(f"Item {row+1},{col+1}")
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


