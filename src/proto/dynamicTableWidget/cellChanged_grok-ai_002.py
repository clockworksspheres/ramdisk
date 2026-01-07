from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QTableWidget Test")
        self.setGeometry(100, 100, 600, 400)

        # Create table
        self.table = QTableWidget(4, 3)
        self.table.setHorizontalHeaderLabels(["Name", "Age", "City"])
        self.table.setSortingEnabled(False)  # Disable sorting during population

        # Populate table
        data = [
            {"Name": "John", "Age": "25", "City": "New York"},
            {"Name": "Jane", "Age": "22", "City": "London"},
            {"Name": "Alice", "Age": "30", "City": "Paris"},
            {"Name": "Bob", "Age": "28", "City": "Tokyo"},
        ]

        for row, entry in enumerate(data):
            for col, key in enumerate(["Name", "Age", "City"]):
                item = QTableWidgetItem(entry[key])
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

        # Enable sorting after population
        self.table.setSortingEnabled(True)

        # Connect signal for debugging
        self.table.currentCellChanged.connect(self.on_cell_changed)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def on_cell_changed(self, current_row, current_col, prev_row, prev_col):
        print(f"Selected: ({current_row}, {current_col})")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


