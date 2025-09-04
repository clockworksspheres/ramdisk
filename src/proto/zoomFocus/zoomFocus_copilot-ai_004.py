from PySide6.QtWidgets import QApplication, QMainWindow, QLineEdit
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from PySide6.QtCore import QSize

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.line_edit = QLineEdit("Use ⌘ + '+' or ⌘ + '-' to zoom")
        self.setCentralWidget(self.line_edit)

        self.font_size = 12
        self.line_edit.setFont(QFont("Arial", self.font_size))

        # Shortcuts for macOS (Command key)
        zoom_in_shortcut = QShortcut(QKeySequence("Meta++"), self)
        zoom_out_shortcut = QShortcut(QKeySequence("Meta+-"), self)

        zoom_in_shortcut.activated.connect(self.zoom_in)
        zoom_out_shortcut.activated.connect(self.zoom_out)

        self.adjust_window_size()

    def zoom_in(self):
        self.font_size += 1
        self.line_edit.setFont(QFont("Arial", self.font_size))
        self.adjust_window_size()

    def zoom_out(self):
        if self.font_size > 1:
            self.font_size -= 1
            self.line_edit.setFont(QFont("Arial", self.font_size))
            self.adjust_window_size()

    def adjust_window_size(self):
        # Resize based on font size (simple scaling logic)
        width = 20 * self.font_size + 100
        height = 4 * self.font_size + 60
        self.resize(QSize(width, height))

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()



