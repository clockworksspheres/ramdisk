from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Window with Shadow")
        self.resize(400, 300)

        # Remove default window frame
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Main container
        container = QWidget(self)
        container.setStyleSheet("background-color: white; border-radius: 10px;")
        
        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(Qt.black)
        shadow.setOffset(0, 0)
        container.setGraphicsEffect(shadow)

        # Layout with content
        layout = QVBoxLayout(container)
        layout.addWidget(QLabel("Window Content", alignment=Qt.AlignCenter))

        self.setCentralWidget(container)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()