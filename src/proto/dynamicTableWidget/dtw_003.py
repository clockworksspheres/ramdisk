import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic Table with Row Selection")
        self.setGeometry(100, 100, 600, 400)

        # Create the table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "Age", "City"])
        self.table.setRowCount(0)  # Start with no rows

        # Enable row selection
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        # Create buttons
        self.add_button = QPushButton("Add Row")
        self.add_button.clicked.connect(self.add_row)
        self.remove_button = QPushButton("Remove Selected Row")
        self.remove_button.clicked.connect(self.remove_row)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.add_button)
        layout.addWidget(self.remove_button)
        layout.addWidget(self.table)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Sample data counter for new rows
        self.row_counter = 0

    def add_row(self):
        # Insert a new row at the end
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        # Populate the row with sample data
        self.table.setItem(row_position, 0, QTableWidgetItem(f"Person {self.row_counter + 1}"))
        self.table.setItem(row_position, 1, QTableWidgetItem(str(20 + self.row_counter)))
        self.table.setItem(row_position, 2, QTableWidgetItem(f"City {self.row_counter + 1}"))
        self.row_counter += 1

    def remove_row(self):
        # Get selected rows
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            print("No row selected")
            return []

        # Collect data from selected rows before removal
        removed_data = []
        for index in sorted([row.row() for row in selected_rows], reverse=True):
            # Extract data from each cell in the row
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(index, col)
                row_data.append(item.text() if item else "")
            removed_data.append(row_data)
            # Remove the row
            self.table.removeRow(index)

        # Print removed data (you can return or process it as needed)
        for data in removed_data:
            print(f"Removed row data: {data}")
        
        return removed_data

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


