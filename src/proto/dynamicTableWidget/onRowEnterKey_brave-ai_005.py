import sys
from PySide6.QtWidgets import (
    QApplication, QTableWidget, QTableWidgetItem, QWidget,
    QVBoxLayout, QDialog, QLabel, QDialogButtonBox
)
from PySide6.QtCore import Qt


# Dialog to show row data
class RowDialog(QDialog):
    def __init__(self, row_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Row Data")
        self.resize(300, 200)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("<b>Selected Row:</b>"))
        for col, value in enumerate(row_data):
            layout.addWidget(QLabel(f"<b>Column {col}:</b> {value}"))
        
        # Add OK button
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.setLayout(layout)


# Custom Table Widget with keypress override
class CustomTableWidget(QTableWidget):
    def keyPressEvent(self, event):
        # On macOS, both Qt.Key_Return and Qt.Key_Enter are handled the same
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            current_item = self.currentItem()
            if current_item:
                row = current_item.row()
                row_data = []
                for col in range(self.columnCount()):
                    item = self.item(row, col)
                    row_data.append(item.text() if item else "")
                
                # Show dialog
                dialog = RowDialog(row_data, self)
                dialog.exec()
            else:
                print("No item selected.")
        else:
            # Let the parent handle other keys (e.g., arrow keys)
            super().keyPressEvent(event)


# Main Window
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Press Enter to Open Dialog (macOS Safe)")
        self.resize(500, 300)

        self.table = CustomTableWidget(3, 3)
        self.table.setHorizontalHeaderLabels(["Name", "Age", "City"])

        # Populate data
        data = [
            ["Alice", "30", "New York"],
            ["Bob", "25", "San Francisco"],
            ["Charlie", "35", "Chicago"]
        ]
        for row, items in enumerate(data):
            for col, text in enumerate(items):
                self.table.setItem(row, col, QTableWidgetItem(text))

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())   


