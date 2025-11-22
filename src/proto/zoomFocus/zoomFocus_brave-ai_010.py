import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton,
    QTableWidget, QVBoxLayout, QHBoxLayout, QWidget,
    QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFontMetrics

class ScaledLabel(QLabel):
    """QLabel that scales pixmap to fit, preserving aspect ratio."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setScaledContents(False)  # Disable automatic scaling
        self.setMinimumSize(100, 100)  # Prevent from collapsing

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        self.update_pixmap()

    def update_pixmap(self):
        if not hasattr(self, '_pixmap') or self._pixmap.isNull():
            return
        scaled = self._pixmap.scaled(
            self.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        super().setPixmap(scaled)

    def resizeEvent(self, event):
        self.update_pixmap()
        super().resizeEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Resizable QMainWindow Example")
        self.resize(600, 400)

        # Central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Scaled Image Label
        self.image_label = ScaledLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid #ccc;")

        # Load sample pixmap (replace with your image path)
        pixmap = QPixmap(300, 200)  # Placeholder
        pixmap.fill(Qt.GlobalColor.lightGray)
        self.image_label.setPixmap(pixmap)

        # Button to simulate zoom/resizing
        self.zoom_button = QPushButton("Resize Window")
        self.zoom_button.clicked.connect(self.resize_window)

        # Table widget
        self.table = QTableWidget(4, 3)
        self.table.setHorizontalHeaderLabels(["Col 1", "Col 2", "Col 3"])
        self.table.setAlternatingRowColors(True)
        
        # Set specific column width (e.g., 100px for column 1)
        self.table.setColumnWidth(1, 100)
        # Allow columns to resize to contents if needed
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        # Populate table with sample data
        for row in range(4):
            for col in range(3):
                item = QPushButton(f"Btn {row},{col}")
                self.table.setCellWidget(row, col, item)

        # Add widgets to layout
        main_layout.addWidget(self.image_label)
        main_layout.addWidget(self.table)
        main_layout.addWidget(self.zoom_button)

        self.setCentralWidget(central_widget)

    def resize_window(self):
        """Toggle window size to simulate zoom/resizing."""
        current_size = self.size()
        if current_size.width() < 800:
            self.resize(800, 600)
        else:
            self.resize(400, 300)
        # Force relayout and repaint
        self.layout().activate()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())   

