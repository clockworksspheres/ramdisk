from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                              QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout)
from PySide6.QtCore import QTimer, Qt
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tabs, Buttons, and LineEdit Example")
        self.setMinimumSize(400, 300)

        # Create QTabWidget
        self.tab_widget = QTabWidget()

        # Tab 1
        self.tab1 = QWidget()
        self.tab1_layout = QVBoxLayout()
        self.tab1_line_edit = QLineEdit("Tab 1 LineEdit")
        self.tab1_button = QPushButton("Tab 1 Button")
        self.tab1_layout.addWidget(self.tab1_line_edit)
        self.tab1_layout.addWidget(self.tab1_button)
        self.tab1.setLayout(self.tab1_layout)
        self.tab_widget.addTab(self.tab1, "Tab 1")

        # Tab 2
        self.tab2 = QWidget()
        self.tab2_layout = QVBoxLayout()
        self.tab2_line_edit = QLineEdit("Tab 2 LineEdit")
        self.tab2_button = QPushButton("Tab 2 Button")
        self.tab2_layout.addWidget(self.tab2_line_edit)
        self.tab2_layout.addWidget(self.tab2_button)
        self.tab2.setLayout(self.tab2_layout)
        self.tab_widget.addTab(self.tab2, "Tab 2")

        # Set tab order within each tab
        QWidget.setTabOrder(self.tab1_line_edit, self.tab1_button)
        QWidget.setTabOrder(self.tab2_line_edit, self.tab2_button)

        # Reset QLineEdit palette to default
        self.tab1_line_edit.setPalette(QApplication.palette())
        self.tab2_line_edit.setPalette(QApplication.palette())

        # Ensure widgets can accept focus
        self.tab1_line_edit.setFocusPolicy(Qt.StrongFocus)
        self.tab1_button.setFocusPolicy(Qt.StrongFocus)
        self.tab2_line_edit.setFocusPolicy(Qt.StrongFocus)
        self.tab2_button.setFocusPolicy(Qt.StrongFocus)

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.tab_widget)
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Connect button clicks to demonstrate focus
        self.tab1_button.clicked.connect(self.on_tab1_button_clicked)
        self.tab2_button.clicked.connect(self.on_tab2_button_clicked)

        # Set initial focus after window is shown
        self.show()
        QTimer.singleShot(0, self.set_initial_focus)

    def set_initial_focus(self):
        # Set focus to tab1_line_edit initially
        self.tab1_line_edit.setFocus()
        print(f"Initial focus set to: {QApplication.focusWidget().objectName()}")

    def on_tab1_button_clicked(self):
        # Move to Tab 2 and set focus to its QLineEdit
        self.tab_widget.setCurrentIndex(1)
        QTimer.singleShot(0, self.tab2_line_edit.setFocus)
        print(f"Focus moved to: {QApplication.focusWidget().objectName()}")

    def on_tab2_button_clicked(self):
        # Move to Tab 1 and set focus to its QLineEdit
        self.tab_widget.setCurrentIndex(0)
        QTimer.singleShot(0, self.tab1_line_edit.setFocus)
        print(f"Focus moved to: {QApplication.focusWidget().objectName()}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())


