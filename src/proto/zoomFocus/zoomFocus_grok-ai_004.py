import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QKeySequence, QAction
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Font Zoom Stylesheet Example")
        self.setGeometry(100, 100, 400, 300)

        # Central widget with label for text
        central_widget = QWidget()
        self.label = QLabel("Sample Text")
        self.label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Set initial stylesheet with enhanced properties
        self.font_size = 16  # Starting font size in pixels
        self.update_stylesheet()

        # Create menu bar
        menubar = self.menuBar()
        view_menu = menubar.addMenu('&View')

        # Zoom In action (Command + Plus)
        zoom_in_action = QAction('&Zoom In', self)
        zoom_in_action.setShortcut(QKeySequence("Ctrl++"))  # Maps to ⌘+= on macOS
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)

        # Zoom Out action (Command + Minus)
        zoom_out_action = QAction('Z&oom Out', self)
        zoom_out_action.setShortcut(QKeySequence("Ctrl+-"))  # Maps to ⌘+- on macOS
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)

    def update_stylesheet(self):
        # Apply stylesheet with multiple properties
        self.label.setStyleSheet(f"""
            font-size: {self.font_size}px;
            font-family: Arial;
            font-weight: bold;
            color: #2c3e50;
            background-color: #ecf0f1;
            padding: 10px;
            border: 2px solid #3498db;
            border-radius: 5px;
        """)

    def zoom_in(self):
        # Increase font size by 2 pixels
        self.font_size += 2
        self.update_stylesheet()

    def zoom_out(self):
        # Decrease font size by 2 pixels, with a minimum of 8px
        if self.font_size > 8:
            self.font_size -= 2
            self.update_stylesheet()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


