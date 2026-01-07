from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout

def show_window(window):
    window.show()
    window.raise_()
    window.activateWindow()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 300, 200)
        
        # Create secondary window
        self.secondary_window = QWidget()
        self.secondary_window.setWindowTitle("Secondary Window")
        self.secondary_window.setGeometry(150, 150, 250, 150)
        
        # Button to show secondary window
        button = QPushButton("Show Window", self)
        button.clicked.connect(lambda: show_window(self.secondary_window))
        
        layout = QVBoxLayout()
        layout.addWidget(button)
        self.setLayout(layout)

app = QApplication([])
main_window = MainWindow()
main_window.show()
app.exec()   
