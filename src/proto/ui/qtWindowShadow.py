from PySide6.QtWidgets import QApplication, QGraphicsDropShadowEffect, QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

class ShadowWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the window
        self.setWindowTitle("PySide6 Drop Shadow Example")
        self.setGeometry(100, 100, 300, 200)

        # Create a label widget
        label = QLabel("This window has a drop shadow!", self)
        label.setAlignment(Qt.AlignCenter)

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)

        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 150))  # Semi-transparent black
        shadow.setOffset(5, 5)  # Horizontal and vertical offset

        self.setGraphicsEffect(shadow)

# Run the application
app = QApplication([])
window = ShadowWindow()
window.show()
app.exec()


