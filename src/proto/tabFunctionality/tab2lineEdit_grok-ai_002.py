from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QLineEdit, QVBoxLayout, QWidget, QTableWidgetItem
from PySide6.QtCore import Qt, QEvent

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Table to LineEdit on Key Event")

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create table
        self.table = QTableWidget(3, 2)  # 3 rows, 2 columns
        self.table.setFocusPolicy(Qt.StrongFocus)
        self.table.setEditTriggers(QTableWidget.DoubleClicked)  # Edit cells on double-click

        # Populate table with sample data
        for row in range(3):
            for col in range(2):
                self.table.setItem(row, col, QTableWidgetItem(f"Cell {row},{col}"))

        # Create QLineEdit
        self.line_edit = QLineEdit()
        self.line_edit.setFocusPolicy(Qt.StrongFocus)
        self.line_edit.setPlaceholderText("Type here...")

        # Apply stylesheet for focus highlight
        self.line_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid gray;
                padding: 2px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d7;  /* macOS-like blue highlight */
                background-color: #e6f3ff;  /* Light blue background */
            }
        """)

        # Add widgets to layout
        layout.addWidget(self.table)
        layout.addWidget(self.line_edit)

        # Set tab order (optional, for default Tab behavior)
        self.setTabOrder(self.table, self.line_edit)

        # Install event filter on table
        self.table.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Handle key press events for the QTableWidget."""
        if obj == self.table and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Tab, Qt.Key_Enter, Qt.Key_Return):
                self.line_edit.setFocus()  # Move focus to QLineEdit
                self.line_edit.selectAll()  # Optional: Select all text
                return True  # Event handled
        return super().eventFilter(obj, event)  # Pass other events to default handler

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


