from PySide6.QtWidgets import (
    QApplication, QMainWindow, QSpinBox, QTableWidget,
    QVBoxLayout, QWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QKeyEvent


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spinbox + Table: Handle Enter on Row")
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

        # Populate table
        for row in range(4):
            for col in range(3):
                item = QTableWidgetItem(f"Item {row},{col}")
                self.table.setItem(row, col, item)

        # Install event filter on table viewport to catch key events
        self.table.viewport().installEventFilter(self)

        # Add widgets to layout
        layout.addWidget(self.spin_box)
        layout.addWidget(self.table)
        container.setLayout(layout)
        self.setCentralWidget(container)

    def eventFilter(self, obj, event):
        # Only process events from table viewport
        if obj == self.table.viewport():
            if event.type() == QEvent.KeyPress:
                key_event = QKeyEvent(event)
                # Check if Enter or Return key was pressed
                if key_event.key() in (Qt.Key_Return, Qt.Key_Enter):
                    current_item = self.table.currentItem()
                    if current_item:
                        row = current_item.row()
                        self.handle_enter_on_row(row)
                        return True  # Event handled
        return super().eventFilter(obj, event)

    def handle_enter_on_row(self, row):
        """Called when Enter is pressed in any cell of a row."""
        spin_value = self.spin_box.value()
        print(f"Enter pressed on row {row}. Updating all cells with spinbox value: {spin_value}")

        # Update all cells in the row
        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item:
                item.setText(f"Row{row}={spin_value}")

    def on_spinbox_editing_finished(self):
        print(f"Spinbox value set to: {self.spin_box.value()}")


# Run the application
app = QApplication([])
window = MainWindow()
window.show()
app.exec()   


