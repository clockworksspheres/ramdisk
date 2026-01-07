from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QLineEdit, QVBoxLayout, QWidget, QTableWidgetItem
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Table to LineEdit Tab Focus")

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create table
        self.table = QTableWidget(3, 2)  # 3 rows, 2 columns
        self.table.setFocusPolicy(Qt.StrongFocus)  # Ensure table can receive focus
        self.table.setEditTriggers(QTableWidget.DoubleClicked)  # Optional: Edit cells on double-click

        # Populate table with sample data
        for row in range(3):
            for col in range(2):
                self.table.setItem(row, col, QTableWidgetItem(f"Cell {row},{col}"))

        # Create QLineEdit
        self.line_edit = QLineEdit()
        self.line_edit.setFocusPolicy(Qt.StrongFocus)  # Ensure line edit can receive focus
        self.line_edit.setPlaceholderText("Type here...")

        # Apply stylesheet for focus highlight
        self.line_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid gray;
                padding: 2px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d7;  /* macOS-like blue highlight */
                background-color: #e6f3ff;  /* Light blue background on focus */
            }
        """)

        # Add widgets to layout
        layout.addWidget(self.table)
        layout.addWidget(self.line_edit)

        # Set tab order from table to line edit
        self.setTabOrder(self.table, self.line_edit)

        # Optional: Handle focus-in event for additional behavior
        self.line_edit.focusInEvent = self.on_line_edit_focus_in

    def on_line_edit_focus_in(self, event):
        """Custom focus-in event handler for QLineEdit."""
        # Select all text when the QLineEdit gains focus (optional)
        self.line_edit.selectAll()
        super(QLineEdit, self.line_edit).focusInEvent(event)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

