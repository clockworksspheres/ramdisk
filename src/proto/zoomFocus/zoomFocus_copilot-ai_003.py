from PySide6.QtWidgets import QApplication, QMainWindow, QLineEdit
from PySide6.QtGui import QFont, QKeySequence, QShortcut

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.line_edit = QLineEdit("Use ⌘ + '+' or ⌘ + '-' to zoom")
        self.setCentralWidget(self.line_edit)

        self.font_size = 12
        self.line_edit.setFont(QFont("Arial", self.font_size))

        # macOS uses Command (MetaModifier) instead of Ctrl
        zoom_in_shortcut = QShortcut(QKeySequence("Meta++"), self)
        zoom_out_shortcut = QShortcut(QKeySequence("Meta+-"), self)

        zoom_in_shortcut.activated.connect(self.zoom_in)
        zoom_out_shortcut.activated.connect(self.zoom_out)

    def zoom_in(self):
        self.font_size += 1
        self.line_edit.setFont(QFont("Arial", self.font_size))

    def zoom_out(self):
        if self.font_size > 1:
            self.font_size -= 1
            self.line_edit.setFont(QFont("Arial", self.font_size))

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.resize(400, 100)
    window.show()
    app.exec()


