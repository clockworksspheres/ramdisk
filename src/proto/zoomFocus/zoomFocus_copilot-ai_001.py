from PySide6.QtWidgets import QApplication, QMainWindow, QLineEdit
from PySide6.QtGui import QFont, QWheelEvent, QKeySequence
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.line_edit = QLineEdit("Zoom me in or out!")
        self.setCentralWidget(self.line_edit)

        self.default_font_size = 12
        self.line_edit.setFont(QFont("Arial", self.default_font_size))

    def wheelEvent(self, event: QWheelEvent):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()

    def zoom_in(self):
        font = self.line_edit.font()
        size = font.pointSize()
        font.setPointSize(size + 1)
        self.line_edit.setFont(font)

    def zoom_out(self):
        font = self.line_edit.font()
        size = font.pointSize()
        if size > 1:
            font.setPointSize(size - 1)
            self.line_edit.setFont(font)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.resize(400, 100)
    window.show()
    app.exec()



