import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QDialog,
    QLabel,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt


# Dialog to display row data
class RowDataDialog(QDialog):
    def __init__(self, row_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Row Details")
        self.resize(300, 200)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("<b>Selected Row Data:</b>"))
        for col_index, value in enumerate(row_data):
            layout.addWidget(QLabel(f"<b>Column {col_index}:</b> {value}"))

        # OK button to close
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.setLayout(layout)


# Main Window with QTableWidget inside
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QTableWidget in QMainWindow - Press Enter to View Row")
        self.resize(600, 400)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create and configure the table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "Age", "City"])
        self.populate_table()

        layout.addWidget(self.table)

        # Optional: Set focus policy to ensure key events are received
        self.table.setFocusPolicy(Qt.StrongFocus)

    def populate_table(self):
        data = [
            ["Alice", "30", "New York"],
            ["Bob", "25", "Los Angeles"],
            ["Charlie", "35", "Chicago"],
            ["Diana", "28", "Seattle"]
        ]
        self.table.setRowCount(len(data))
        for row, items in enumerate(data):
            for col, text in enumerate(items):
                self.table.setItem(row, col, QTableWidgetItem(text))

    # Override keyPressEvent for the main window (or route through table)
    def keyPressEvent(self, event):
        # Forward Enter/Return key press to the table if it has focus
        if self.table is self.focusWidget():
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                current_item = self.table.currentItem()
                if current_item:
                    row = current_item.row()
                    row_data = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else "")
                    
                    # Show dialog with row data
                    dialog = RowDataDialog(row_data, self)
                    dialog.exec()
                    dialog.raise_()
                else:
                    print("No cell selected.")
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())   

