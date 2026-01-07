from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QTableWidget,
    QVBoxLayout, QWidget, QLabel
)
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtCore import Qt

class ZoomWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.zoom_level = 100  # Starting at 100% (normal size)
        self.init_ui()
        self.update_zoom()

    def init_ui(self):
        self.setWindowTitle("Zoom In/Out Example")

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Add QLineEdit
        self.line_edit = QLineEdit("This is a QLineEdit")
        layout.addWidget(self.line_edit)

        # Add QTableWidget
        self.table = QTableWidget(3, 3)
        self.table.setHorizontalHeaderLabels(["A", "B", "C"])
        self.table.setVerticalHeaderLabels(["1", "2", "3"])
        layout.addWidget(self.table)

        # Status label to show zoom level
        self.status_label = QLabel(f"Zoom: {self.zoom_level}%", alignment=Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Zoom In: Ctrl++ or Ctrl+=
        self.zoom_in_shortcut = QShortcut(QKeySequence("Ctrl++"), self)
        self.zoom_in_shortcut2 = QShortcut(QKeySequence("Ctrl+="), self)
        self.zoom_in_shortcut.activated.connect(self.zoom_in)
        self.zoom_in_shortcut2.activated.connect(self.zoom_in)

        # Zoom Out: Ctrl+-
        self.zoom_out_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        self.zoom_out_shortcut.activated.connect(self.zoom_out)

    def zoom_in(self):
        self.zoom_level += 20
        self.update_zoom()

    def zoom_out(self):
        if self.zoom_level > 20:  # Prevent going too small
            self.zoom_level -= 20
        self.update_zoom()

    def update_zoom(self):
        # Convert zoom level to pt (base ~10pt at 100%)
        font_size = max(6, int(10 * self.zoom_level / 100))
        self.setStyleSheet(f"QWidget {{ font-size: {font_size}pt; }}")

        # Update status label
        self.status_label.setText(f"Zoom: {self.zoom_level}%")

# Run the app
app = QApplication()
app.setAttribute(app.AA_EnableHighDpiScaling)

window = ZoomWindow()
window.show()

app.exec()   



