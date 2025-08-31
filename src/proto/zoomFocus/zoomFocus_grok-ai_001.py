import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QKeySequence,QAction
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 macOS Shortcut Example")
        self.setGeometry(100, 100, 400, 300)

        # Central widget with label to track zoom level
        central_widget = QWidget()
        self.label = QLabel("Zoom level: 100%")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Create menu bar
        menubar = self.menuBar()
        view_menu = menubar.addMenu('&View')

        # Zoom In action (Command + Plus)
        zoom_in_action = QAction('&Zoom In', self)
        zoom_in_action.setShortcut(QKeySequence("Ctrl++"))  # Maps to ⌘+= on macOS
        # Alternative: zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)

        # Zoom Out action (Command + Minus)
        zoom_out_action = QAction('Z&oom Out', self)
        zoom_out_action.setShortcut(QKeySequence("Ctrl+-"))  # Maps to ⌘+- on macOS
        # Alternative: zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)

        # Track zoom level
        self.zoom_level = 100

    def zoom_in(self):
        # Increase zoom level
        self.zoom_level += 50
        self.label.setText(f"Zoom level: {self.zoom_level}%")

    def zoom_out(self):
        # Decrease zoom level, with a minimum of 50%
        if self.zoom_level > 50:
            self.zoom_level -= 50
            self.label.setText(f"Zoom level: {self.zoom_level}%")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


