import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget
from PySide6.QtGui import QKeySequence, QAction
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Zoom All Widgets and Window")
        self.base_width = 400
        self.base_height = 300
        self.setGeometry(100, 100, self.base_width, self.base_height)

        # Central widget with multiple widgets
        central_widget = QWidget()
        layout = QVBoxLayout()
        self.label = QLabel("Sample Text")
        self.label.setAlignment(Qt.AlignCenter)
        self.button = QPushButton("Click Me")
        self.text_edit = QTextEdit("Editable text area")
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        layout.addWidget(self.text_edit)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Initialize zoom factor and font size
        self.zoom_factor = 1.0  # Starting scale (1.0 = 100%)
        self.base_font_size = 14  # Base font size in pixels
        self.update_stylesheet_and_window()

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

    def update_stylesheet_and_window(self):
        # Calculate scaled font size
        scaled_font_size = int(self.base_font_size * self.zoom_factor)
        if scaled_font_size < 8:  # Minimum font size
            scaled_font_size = 8

        # Apply global stylesheet to all widgets
        self.centralWidget().setStyleSheet(f"""
            QLabel {{
                font-size: {scaled_font_size}px;
                font-family: Arial;
                font-weight: bold;
                color: #2c3e50;
                background-color: #ecf0f1;
                padding: 10px;
                border: 2px solid #3498db;
                border-radius: 5px;
            }}
            QPushButton {{
                font-size: {scaled_font_size}px;
                font-family: Arial;
                color: #ffffff;
                background-color: #3498db;
                padding: 8px;
                border: 1px solid #2980b9;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
            QTextEdit {{
                font-size: {scaled_font_size}px;
                font-family: Arial;
                color: #2c3e50;
                background-color: #ffffff;
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 5px;
            }}
        """)

        # Scale window size
        new_width = int(self.base_width * self.zoom_factor)
        new_height = int(self.base_height * self.zoom_factor)
        if new_width < 200 or new_height < 150:  # Minimum window size
            new_width = max(200, new_width)
            new_height = max(150, new_height)
        self.resize(new_width, new_height)

    def zoom_in(self):
        # Increase zoom factor by 0.2
        self.zoom_factor += 0.2
        self.update_stylesheet_and_window()

    def zoom_out(self):
        # Decrease zoom factor by 0.2, with a minimum of 0.5
        if self.zoom_factor > 0.5:
            self.zoom_factor -= 0.2
            self.update_stylesheet_and_window()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

