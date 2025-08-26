import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QWidget, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from ui_mainwindow_004 import Ui_MainWindow  # Import the generated UI class

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set up the UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Widget Shadows with Heavy Highlight")

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

        # Apply stylesheets with heavy focus highlight (day/night compatible)
        self.ui.lineEdit.setStyleSheet("""
            QLineEdit {
                background: #ffffff;
                color: #000000;
                border: 1px solid #888888;
                border-radius: 4px;
                padding: 4px;
            }
            QLineEdit:focus {
                border: 3px solid #ff6200; /* Heavy orange border */
                background: #fff5e6; /* Subtle orange tint */
            }
        """)
        self.ui.lineEdit_2.setStyleSheet("""
            QLineEdit {
                background: #ffffff;
                color: #000000;
                border: 1px solid #888888;
                border-radius: 4px;
                padding: 4px;
            }
            QLineEdit:focus {
                border: 3px solid #ff6200; /* Heavy orange border */
                background: #fff5e6; /* Subtle orange tint */
            }
        """)
        self.ui.pushButton.setStyleSheet("""
            QPushButton {
                background: #e0e0e0;
                color: #000000;
                border: 1px solid #888888;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:focus {
                border: 3px solid #ff6200; /* Heavy orange border */
                background: #f0e6d6; /* Subtle orange tint */
            }
            QPushButton:hover {
                background: #d0d0d0;
            }
        """)
        self.ui.tableWidget.setStyleSheet("""
            QTableWidget {
                background: #ffffff;
                color: #000000;
                border: 1px solid #888888;
                border-radius: 4px;
                gridline-color: #888888;
            }
            QTableWidget::item {
                border: none;
            }
            QTableWidget::item:selected {
                background: #ff6200; /* Orange selection */
                color: #ffffff;
            }
            QTableWidget:focus {
                border: 3px solid #ff6200; /* Heavy orange border */
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


