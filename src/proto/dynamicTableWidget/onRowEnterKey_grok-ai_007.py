from PySide6.QtWidgets import (
    QApplication, QMainWindow, QSpinBox, QTableWidget,
    QVBoxLayout, QWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt, QEvent


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editable Table with Enter Key Handling")
        self.setGeometry(100, 100, 500, 300)

        # Central widget and layout
        container = QWidget()
        layout = QVBoxLayout()

        # QSpinBox
        self.spin_box = QSpinBox()
        self.spin_box.setRange(0, 100)
        self.spin_box.setValue(10)
        self.spin_box.setPrefix("Value: ")
        self.spin_box.editingFinished.connect(self.on_spinbox_editing_finished)

        # QTableWidget
        self.table = QTableWidget()
        self.table.setRowCount(4)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Col 1", "Col 2", "Col 3"])

        # Populate table with editable items
        for row in range(4):
            for col in range(3):
                item = QTableWidgetItem(f"Item {row},{col}")
                item.setFlags(item.flags() | Qt.ItemIsEditable)  # Ensure item is editable
                self.table.setItem(row, col, item)

        # Install event filter on viewport to catch key events
        self.table.viewport().installEventFilter(self)

        # Add widgets to layout
        layout.addWidget(self.spin_box)
        layout.addWidget(self.table)
        container.setLayout(layout)
        self.setCentralWidget(container)

    def eventFilter(self, obj, event):
        if obj == self.table.viewport() and event.type() == QEvent.KeyPress:
            key_event = event
            if key_event.key() in (Qt.Key_Return, Qt.Key_Enter):
                current_item = self.table.currentItem()
                if current_item:
                    row = current_item.row()
                    self.handle_enter_on_row(row)
                    return True  # Prevent further handling
        return super().eventFilter(obj, event)

    def handle_enter_on_row(self, row):
        """Called when Enter is pressed in any cell of the row."""
        spin_value = self.spin_box.value()
        print(f"Enter pressed on row {row}. Updating all cells with: {spin_value}")

        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item:
                item.setText(f"Updated {spin_value}")

    def on_spinbox_editing_finished(self):
        print(f"Spinbox value confirmed: {self.spin_box.value()}")


# Run the application
app = QApplication([])
window = MainWindow()
window.show()
app.exec()   


