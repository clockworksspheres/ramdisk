from PySide6.QtWidgets import (QApplication, QMainWindow, QLineEdit, 
                              QPushButton, QVBoxLayout, QWidget)
from PySide6.QtCore import QTimer, Qt
import sys

# Simulated Ui_MainWindow class (mimics Qt Designer-generated code)
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        # Create central widget and layout
        self.centralwidget = QWidget(MainWindow)
        self.layout = QVBoxLayout(self.centralwidget)

        # Create widgets
        self.lineEdit_1 = QLineEdit(self.centralwidget)
        self.lineEdit_1.setObjectName("lineEdit_1")
        self.lineEdit_1.setPlaceholderText("LineEdit 1")
        
        self.pushButton_1 = QPushButton(self.centralwidget)
        self.pushButton_1.setObjectName("pushButton_1")
        self.pushButton_1.setText("Focus LineEdit 2")
        
        self.lineEdit_2 = QLineEdit(self.centralwidget)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_2.setPlaceholderText("LineEdit 2")
        
        self.pushButton_2 = QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setText("Focus LineEdit 1")

        # Add widgets to layout
        self.layout.addWidget(self.lineEdit_1)
        self.layout.addWidget(self.pushButton_1)
        self.layout.addWidget(self.lineEdit_2)
        self.layout.addWidget(self.pushButton_2)

        # Set central widget
        MainWindow.setCentralWidget(self.centralwidget)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LineEdit Default Focus Example")
        self.setMinimumSize(400, 200)

        # Initialize UI from Ui_MainWindow
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Reset QLineEdit palette to default
        self.ui.lineEdit_1.setPalette(QApplication.palette())
        self.ui.lineEdit_2.setPalette(QApplication.palette())

        # Set focus policy
        self.ui.lineEdit_1.setFocusPolicy(Qt.StrongFocus)
        self.ui.pushButton_1.setFocusPolicy(Qt.StrongFocus)
        self.ui.lineEdit_2.setFocusPolicy(Qt.StrongFocus)
        self.ui.pushButton_2.setFocusPolicy(Qt.StrongFocus)

        # Set tab order
        QWidget.setTabOrder(self.ui.lineEdit_1, self.ui.pushButton_1)
        QWidget.setTabOrder(self.ui.pushButton_1, self.ui.lineEdit_2)
        QWidget.setTabOrder(self.ui.lineEdit_2, self.ui.pushButton_2)

        # Connect button clicks
        self.ui.pushButton_1.clicked.connect(self.focus_line_edit_2)
        self.ui.pushButton_2.clicked.connect(self.focus_line_edit_1)

        # Set default focus to lineEdit_1 after window is shown
        QTimer.singleShot(0, self.ui.lineEdit_1.setFocus)

    def focus_line_edit_2(self):
        QTimer.singleShot(0, self.ui.lineEdit_2.setFocus)

    def focus_line_edit_1(self):
        QTimer.singleShot(0, self.ui.lineEdit_1.setFocus)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


