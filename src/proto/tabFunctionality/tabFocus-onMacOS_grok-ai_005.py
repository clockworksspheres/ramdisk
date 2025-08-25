from PySide6.QtWidgets import (QApplication, QMainWindow, QLineEdit, 
                              QPushButton, QTableWidget, QTableWidgetItem, 
                              QVBoxLayout, QWidget)
from PySide6.QtCore import QTimer, Qt
import sys

# Simulated Ui_MainWindow class (mimics Qt Designer-generated code)
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        # Create central widget and layout
        self.centralwidget = QWidget(MainWindow)
        self.layout = QVBoxLayout(self.centralwidget)

        # Create QTableWidget
        self.tableWidget = QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setRowCount(3)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(["Name", "Value"])
        # Populate table with sample data
        for row in range(3):
            for col in range(2):
                item = QTableWidgetItem(f"Item {row},{col}")
                self.tableWidget.setItem(row, col, item)

        # Create QLineEdit
        self.lineEdit = QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setPlaceholderText("Select a table cell")

        # Create QPushButton
        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("Clear LineEdit")

        # Add widgets to layout
        self.layout.addWidget(self.tableWidget)
        self.layout.addWidget(self.lineEdit)
        self.layout.addWidget(self.pushButton)

        # Set central widget
        MainWindow.setCentralWidget(self.centralwidget)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Table to LineEdit Example")
        self.setMinimumSize(400, 300)

        # Initialize UI from Ui_MainWindow
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Reset QLineEdit palette to default
        self.ui.lineEdit.setPalette(QApplication.palette())

        # Set focus policy
        self.ui.lineEdit.setFocusPolicy(Qt.StrongFocus)
        self.ui.pushButton.setFocusPolicy(Qt.StrongFocus)
        self.ui.tableWidget.setFocusPolicy(Qt.StrongFocus)

        # Set tab order
        QWidget.setTabOrder(self.ui.tableWidget, self.ui.lineEdit)
        QWidget.setTabOrder(self.ui.lineEdit, self.ui.pushButton)

        # Connect signals
        self.ui.tableWidget.cellClicked.connect(self.table_cell_to_lineedit)
        self.ui.pushButton.clicked.connect(self.ui.lineEdit.clear)

        # Set default focus to lineEdit after window is shown
        QTimer.singleShot(0, self.ui.lineEdit.setFocus)

    def table_cell_to_lineedit(self, row, column):
        # Transfer table cell content to QLineEdit
        item = self.ui.tableWidget.item(row, column)
        if item:
            self.ui.lineEdit.setText(item.text())
        else:
            self.ui.lineEdit.clear()
        # Ensure focus returns to lineEdit
        QTimer.singleShot(0, self.ui.lineEdit.setFocus)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


