import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QWidget, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from ui_mainwindow_007 import Ui_MainWindow  # Import the generated UI class

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set up the UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Bigger Blue Shadows with Blue Focus and Light Blue Tint")

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

        # Prevent Tab key insertion in QLineEdit
        self.ui.lineEdit.setInputMethodHints(Qt.ImhNoAutoUppercase)
        self.ui.lineEdit_2.setInputMethodHints(Qt.ImhNoAutoUppercase)
        self.ui.lineEdit.setAcceptDrops(False)
        self.ui.lineEdit_2.setAcceptDrops(False)

        # Apply bigger blue shadow effects
        self.apply_bigger_blue_shadow(self.ui.lineEdit)
        self.apply_bigger_blue_shadow(self.ui.lineEdit_2)
        self.apply_bigger_blue_shadow(self.ui.pushButton)
        self.apply_bigger_blue_shadow(self.ui.tableWidget)

        # Apply stylesheets with heavy blue focus highlight and light blue tint (day mode)
        self.set_day_mode_styles()

        # Set custom tab order
        QWidget.setTabOrder(self.ui.lineEdit, self.ui.lineEdit_2)
        QWidget.setTabOrder(self.ui.lineEdit_2, self.ui.pushButton)
        QWidget.setTabOrder(self.ui.pushButton, self.ui.tableWidget)

        # Connect table's key press event
        self.ui.tableWidget.keyPressEvent = self.table_key_press_event

        # Set initial focus
        self.ui.lineEdit.setFocus()

    def apply_bigger_blue_shadow(self, widget):
        """Apply a bigger blue drop shadow effect to the given widget."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)  # Larger blur for bigger shadow
        shadow.setXOffset(5)      # Larger horizontal offset
        shadow.setYOffset(5)      # Larger vertical offset
        shadow.setColor(QColor(0, 120, 215, 100))  # Semi-transparent blue (#0078d7)
        widget.setGraphicsEffect(shadow)

    def set_day_mode_styles(self):
        """Apply stylesheets for day mode with heavy blue focus highlight and light blue tint."""
        self.ui.lineEdit.setStyleSheet("""
            QLineEdit {
                background: #ffffff;
                color: #000000;
                border: 1px solid #888888;
                border-radius: 4px;
                padding: 4px;
            }
            QLineEdit:focus {
                border: 3px solid #0078d7; /* Heavy blue border */
                background: #e6f3ff; /* Light blue tint */
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
                border: 3px solid #0078d7; /* Heavy blue border */
                background: #e6f3ff; /* Light blue tint */
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
                border: 3px solid #0078d7; /* Heavy blue border */
                background: #e6f3ff; /* Light blue tint */
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
                background: #0078d7; /* Blue selection */
                color: #ffffff;
            }
            QTableWidget:focus {
                border: 3px solid #0078d7; /* Heavy blue border */
            }
        """)
        self.setStyleSheet("QMainWindow { background: #f0f0f0; }")  # Light background

    def set_night_mode_styles(self):
        """Apply stylesheets for night mode with heavy blue focus highlight and light blue tint."""
        self.ui.lineEdit.setStyleSheet("""
            QLineEdit {
                background: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }
            QLineEdit:focus {
                border: 3px solid #0078d7; /* Heavy blue border */
                background: #2f4a6d; /* Darker light blue tint */
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
                border: 3px solid #0078d7; /* Heavy blue border */
                background: #2f4a6d; /* Darker light blue tint */
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
            QLineEdit:focus {
                border: 3px solid #0078d7; /* Heavy blue border */
                background: #2f4a6d; /* Darker light blue tint */
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
                background: #0078d7; /* Blue selection */
                color: #ffffff;
            }
            QTableWidget:focus {
                border: 3px solid #0078d7; /* Heavy blue border */
            }
        """)
        self.setStyleSheet("QMainWindow { background: #1e1e1e; }")  # Dark background

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
    # Optionally switch to night mode for testing
    # window.set_night_mode_styles()
    sys.exit(app.exec())
