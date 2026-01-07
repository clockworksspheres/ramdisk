import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tab Navigation Cycle Example")
        self.setGeometry(100, 100, 400, 300)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create widgets
        self.line_edit1 = QLineEdit()
        self.line_edit1.setPlaceholderText("Line Edit 1")
        self.line_edit2 = QLineEdit()
        self.line_edit2.setPlaceholderText("Line Edit 2")
        self.button = QPushButton("Click Me")
        self.table = QTableWidget(3, 2)  # 3 rows, 2 columns

        # Populate table with sample data
        for row in range(3):
            for col in range(2):
                self.table.setItem(row, col, QTableWidgetItem(f"Cell {row},{col}"))

        # Set focus policy for all widgets
        self.line_edit1.setFocusPolicy(Qt.StrongFocus)
        self.line_edit2.setFocusPolicy(Qt.StrongFocus)
        self.button.setFocusPolicy(Qt.StrongFocus)
        self.table.setFocusPolicy(Qt.StrongFocus)

        # Add widgets to layout
        layout.addWidget(self.line_edit1)
        layout.addWidget(self.line_edit2)
        layout.addWidget(self.button)
        layout.addWidget(self.table)

        # Set custom tab order
        self.setTabOrder(self.line_edit1, self.line_edit2)
        self.setTabOrder(self.line_edit2, self.button)
        self.setTabOrder(self.button, self.table)
        # Note: No need to set tab order from table to line_edit1, as we handle it manually

        # Connect table's key press event
        self.table.keyPressEvent = self.table_key_press_event

        # Set initial focus
        self.line_edit1.setFocus()

    def table_key_press_event(self, event):
        """Custom key press event for QTableWidget to cycle back to line_edit1."""
        if event.key() == Qt.Key_Tab:
            current_row = self.table.currentRow()
            current_col = self.table.currentColumn()
            # If in the last cell, move focus to line_edit1
            if current_row == self.table.rowCount() - 1 and current_col == self.table.columnCount() - 1:
                self.line_edit1.setFocus()
                return
        # Default table key handling (e.g., move to next cell)
        super(QTableWidget, self.table).keyPressEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


