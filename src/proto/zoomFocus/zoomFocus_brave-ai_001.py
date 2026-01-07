from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QTableWidget,
    QTableWidgetItem, QSlider, QVBoxLayout, QHBoxLayout, QWidget,
    QFileDialog, QPushButton
)
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt

class ScaledLabel(QLabel):
    """Custom QLabel that automatically scales its pixmap to fit while preserving aspect ratio."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pixmap = None
        self.setAlignment(Qt.AlignCenter)

    def resizeEvent(self, event):
        if self._pixmap:
            self.setPixmap(self._pixmap.scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        super().resizeEvent(event)

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        if not pixmap.isNull():
            super().setPixmap(pixmap.scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            super().setPixmap(pixmap)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Zoom Example")
        self.resize(900, 700)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Top: Image Label
        self.label = ScaledLabel("No image loaded")
        self.label.setStyleSheet("QLabel { background-color: #f0f0f0; border: 1px solid #ccc; }")
        main_layout.addWidget(self.label, 4)  # Stretch factor 4

        # Middle: QLineEdit
        self.line_edit = QLineEdit("Editable text - zoom affects font size")
        main_layout.addWidget(self.line_edit, 1)

        # Table
        self.table = QTableWidget(6, 4)
        self.table.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3", "Column 4"])
        for i in range(6):
            for j in range(4):
                item = QTableWidgetItem(f"Cell {i+1},{j+1}")
                self.table.setItem(i, j, item)
        main_layout.addWidget(self.table, 3)

        # Controls layout
        controls_layout = QHBoxLayout()
        main_layout.addLayout(controls_layout)

        # Load image button
        load_btn = QPushButton("Load Image")
        load_btn.clicked.connect(self.load_image)
        controls_layout.addWidget(load_btn)

        # Zoom slider
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(50)
        self.zoom_slider.setMaximum(200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setTickInterval(25)
        self.zoom_slider.setTickPosition(QSlider.TicksBelow)
        self.zoom_slider.valueChanged.connect(self.update_zoom)
        controls_layout.addWidget(QLabel("Zoom:"))
        controls_layout.addWidget(self.zoom_slider, 1)

        # Zoom level display
        self.zoom_label = QLabel("100%")
        controls_layout.addWidget(self.zoom_label)

        # Initialize zoom
        self.update_zoom(100)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp *.gif)")
        if file_name:
            pixmap = QPixmap(file_name)
            if not pixmap.isNull():
                self.label.setPixmap(pixmap)
            else:
                self.label.setText("Failed to load image")

    def update_zoom(self, value):
        # Update zoom display
        self.zoom_label.setText(f"{value}%")

        # Calculate font size based on base size and zoom
        base_font_size = 10
        font_size = base_font_size * value / 100
        font = QFont()
        font.setPointSize(max(6, int(font_size)))  # Minimum size 6

        # Apply to line edit
        self.line_edit.setFont(font)

        # Apply to table
        self.table.setFont(font)

        # Adjust table row/column sizes if desired
        # This keeps cells reasonably sized at different zoom levels
        if value >= 100:
            self.table.resizeRowsToContents()
            self.table.resizeColumnsToContents()
        else:
            # At lower zoom, avoid making cells too small
            pass


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()   

