from PySide6.QtWidgets import QApplication, QMainWindow, QLineEdit, QWidget, QHBoxLayout
from PySide6.QtCore import QTimer
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Focus and Tab Order Example")
        self.setMinimumSize(400, 100)

        # Create widgets
        self.txt_edit1 = QLineEdit("Text Edit 1")
        self.txt_edit2 = QLineEdit("Text Edit 2")

        # Set tab order
        QWidget.setTabOrder(self.txt_edit1, self.txt_edit2)

        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.txt_edit1)
        layout.addWidget(self.txt_edit2)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Ensure widget is visible before setting focus
        self.show()  # Ensure the window is shown
        QTimer.singleShot(0, self.set_focus_on_txt_edit2)

    def set_focus_on_txt_edit2(self):
        # Set focus to txt_edit2
        self.txt_edit2.setFocus()
        # Ensure the widget accepts focus
        self.txt_edit2.setFocusPolicy(Qt.StrongFocus)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


