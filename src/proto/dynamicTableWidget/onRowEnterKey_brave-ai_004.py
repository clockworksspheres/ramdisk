import sys
from PySide6.QtWidgets import (
    QApplication, QTableWidget, QTableWidgetItem, QWidget,
    QVBoxLayout, QDialog, QLabel, QDialogButtonBox, QVBoxLayout
)
from PySide6.QtCore import Qt


# Dialog to show row contents
class RowDataDialog(QDialog):
    def __init__(self, row_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Row Details")
        self.resize(300, 150)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("<b>Row Contents:</b>"))
        for i, value in enumerate(value):
            layout.addWidget(QLabel(f"<b>Column {i}:</b> {value}"))

        # Add OK button to close
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

        self.setLayout(layout)


# Custom Table Widget that responds to Enter/Return key
class CustomTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["Name", "Age", "City"])
        self.populate_data()

    def populate_data(self):
        data = [
            ["Alice", "30", "New York"],
            ["Bob", "25", "Los Angeles"],
            ["Charlie", "35", "Chicago"]
        ]
        self.setRowCount(len(data))
        for row, items in enumerate(data):
            for col, text in enumerate(items):
                self.setItem(row, col, QTableWidgetItem(text))

    def keyPressEvent(self, event):
        # Check if Enter or Return key was pressed
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            current_item = self.currentItem()
            if current_item is not None:
                row = current_item.row()

                # Collect all data in the row
                row_data = []
                for col in range(self.columnCount()):
                    item = self.item(row, col)
                    row_data.append(item.text() if item else "")

                # Show dialog with row data
                dialog = RowDataDialog(row_data, self)
                dialog.exec()
            else:
                # No item selected
                print("No cell selected.")
        else:
            # Pass other keys to the parent method
            super().keyPressEvent(event)


# Main Window
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QTableWidget - Press Enter to Show Row")
        self.resize(500, 300)

        self.table = CustomTableWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())   


