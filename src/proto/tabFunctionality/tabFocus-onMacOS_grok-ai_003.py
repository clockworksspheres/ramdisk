from PySide6.QtWidgets import (QApplication, QMainWindow, QLineEdit, 
                              QPushButton, QVBoxLayout, QWidget)
from PySide6.QtCore import QTimer, Qt
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LineEdit and Button Example")
        self.setMinimumSize(400, 200)

        # Create widgets
        self.line_edit1 = QLineEdit("LineEdit 1")
        self.button1 = QPushButton("Focus LineEdit 2")
        self.line_edit2 = QLineEdit("LineEdit 2")
        self.button2 = QPushButton("Focus LineEdit 1")

        # Reset QLineEdit palette to default
        self.line_edit1.setPalette(QApplication.palette())
        self.line_edit2.setPalette(QApplication.palette())

        # Set focus policy
        self.line_edit1.setFocusPolicy(Qt.StrongFocus)
        self.button1.setFocusPolicy(Qt.StrongFocus)
        self.line_edit2.setFocusPolicy(Qt.StrongFocus)
        self.button2.setFocusPolicy(Qt.StrongFocus)

        # Set tab order
        QWidget.setTabOrder(self.line_edit1, self.button1)
        QWidget.setTabOrder(self.button1, self.line_edit2)
        QWidget.setTabOrder(self.line_edit2, self.button2)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.line_edit1)
        layout.addWidget(self.button1)
        layout.addWidget(self.line_edit2)
        layout.addWidget(self.button2)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Connect button clicks
        self.button1.clicked.connect(self.focus_line_edit2)
        self.button2.clicked.connect(self.focus_line_edit1)

        # Set initial focus after window is shown
        QTimer.singleShot(0, self.line_edit1.setFocus)

    def focus_line_edit2(self):
        QTimer.singleShot(0, self.line_edit2.setFocus)

    def focus_line_edit1(self):
        QTimer.singleShot(0, self.line_edit1.setFocus)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


