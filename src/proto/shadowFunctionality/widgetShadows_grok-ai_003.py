import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QWidget, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from ui_mainwindow_003 import Ui_MainWindow  # Import the generated UI class

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set up the UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Widget Shadows with Dark Tab Highlight")

        # Populate table with sample data
        self.ui.tableWidget.setRowCount(3)
        self.ui.tableWidget.setColumnCount(2)
        for row in range(3):
            for col in range(2):
                self.ui.tableWidget.setItem(row, col, QTableWidgetItem(f"Cell {row},{col}"))

        # Set focus policy for all widgets
        self.ui.lineEdit.setFocusPolicy(Qt.StrongFocus)
        self.ui.lineEdit_2.setFocusPolicy(Qt.StrongFocus)
        self.ui.pushButton.setFocusPolicy(Qt.StrongFocus)
        self.ui.tableWidget.setFocusPolicy(Qt.StrongFocus)

        # Apply default shadow effects
        self.apply_default_shadow(self.ui.lineEdit)
        self.apply_default_shadow(self.ui.lineEdit_2)
        self.apply_default_shadow(self.ui.pushButton)
        self.apply_default_shadow(self.ui.tableWidget)

        # Apply dark-themed stylesheets with focus highlights
        self.ui.lineEdit.setStyleSheet("""
            QLineEdit {
                background: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }
            QLineEdit:focus {
                border: 2px solid #1e90ff;
                background: #333333;
            }
        """)
        self.ui.lineEdit_2.setStyleSheet("""
            QLineEdit {
                background: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }
            QLineEdit:focus {
                border: 2px solid #1e90ff;
                background: #333333;
            }
        """)
        self.ui.pushButton.setStyleSheet("""
            QPushButton {
                background: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:focus {
                border: 2px solid #1e90ff;
                background: #4a4a4a;
            }
            QPushButton:hover {
                background: #4a4a4a;
            }
        """)
        self.ui.tableWidget.setStyleSheet("""
            QTableWidget {
                background: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                gridline-color: #555555;
            }
            QTableWidget::item {
                border: none;
            }
            QTableWidget::item:selected {
                background: #1e90ff;
                color: #ffffff;
            }
            QTableWidget:focus {
                border: 2px solid #1e90ff;
            }
        """)

        # Set custom tab order
        QWidget.setTabOrder(self.ui.lineEdit, self.ui.lineEdit_2)
        QWidget.setTabOrder(self.ui.lineEdit_2, self.ui.pushButton)
        QWidget.setTabOrder(self.ui.pushButton, self.ui.tableWidget)

        # Connect table's key press event
        self.ui.tableWidget.keyPressEvent = self.table_key_press_event

        # Set initial focus
        self.ui.lineEdit.setFocus()

    def apply_default_shadow(self, widget):
        """Apply a default drop shadow effect to the given widget."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)  # Subtle blur for default shadow
        shadow.setXOffset(2)      # Small horizontal offset
        shadow.setYOffset(2)      # Small vertical offset
        shadow.setColor(QColor(0, 0, 0, 80))  # Semi-transparent black
        widget.setGraphicsEffect(shadow)

    def table_key_press_event(self, event):
        """Custom key press event for QTableWidget to cycle back to lineEdit."""
        if event.key() == Qt.Key_Tab:
            current_row = self.ui.tableWidget.currentRow()
            current_col = self.ui.tableWidget.currentColumn()
            # If in the last cell, move focus to lineEdit
            if current_row == self.ui.tableWidget.rowCount() - 1 and current_col == self.ui.tableWidget.columnCount() - 1:
                self.ui.lineEdit.setFocus()
                return
        # Default table key handling
        super(QTableWidget, self.ui.tableWidget).keyPressEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


