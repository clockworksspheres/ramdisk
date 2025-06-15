import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the window properties
        self.setWindowTitle("Window with Shadow")
        self.setGeometry(100, 100, 400, 300)

        # Create a drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)  # Adjust the blur radius for more or less shadow
        shadow.setColor(Qt.black)  # Set the color of the shadow
        shadow.setOffset(5, 5)     # Set the offset of the shadow (x, y)

        # Apply the shadow effect to the main window
        self.setGraphicsEffect(shadow)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    