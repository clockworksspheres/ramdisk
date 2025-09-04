from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget
)
from PySide6.QtGui import QPixmap, QFont, QKeySequence, QShortcut
from PySide6.QtCore import Qt
import sys


class ScaledLabel(QLabel):
    """Custom QLabel that scales its pixmap to fit while preserving aspect ratio."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pixmap = None
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("QLabel { background-color: #f0f0f0; border: 1px solid #ccc; }")

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
        self.setWindowTitle("PySide6 Zoom with Keyboard Shortcuts")
        self.resize(900, 700)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Image Label
        self.label = ScaledLabel("No image loaded")
        main_layout.addWidget(self.label, 4)

        # QLineEdit
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

        # Zoom state
        self.zoom_level = 100
        self.base_font_size = 10

        # Keyboard shortcuts
        self.setup_shortcuts()

    def setup_shortcuts(self):
        # Zoom In: Ctrl++ or Ctrl+=
        QShortcut(QKeySequence("Ctrl++"), self, self.zoom_in)
        QShortcut(QKeySequence("Ctrl+="), self, self.zoom_in)

        # Zoom Out: Ctrl+-
        QShortcut(QKeySequence("Ctrl+-"), self, self.zoom_out)

        # Reset Zoom: Ctrl+0
        QShortcut(QKeySequence("Ctrl+0"), self, self.reset_zoom)

    def zoom_in(self):
        if self.zoom_level < 200:
            self.zoom_level += 10
            self.update_zoom()

    def zoom_out(self):
        if self.zoom_level > 50:
            self.zoom_level -= 10
            self.update_zoom()

    def reset_zoom(self):
        self.zoom_level = 100
        self.update_zoom()

    def update_zoom(self):
        font_size = max(6, int(self.base_font_size * self.zoom_level / 100))
        font = QFont()
        font.setPointSize(font_size)

        self.line_edit.setFont(font)
        self.table.setFont(font)

        # Optional: Resize table contents
        if self.zoom_level >= 100:
            self.table.resizeRowsToContents()
            self.table.resizeColumnsToContents()

        # Update window title to show zoom level
        self.setWindowTitle(f"PySide6 Zoom with Keyboard Shortcuts - {self.zoom_level}%")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())   

