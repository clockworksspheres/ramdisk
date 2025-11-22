import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableView, QPushButton,
                               QVBoxLayout, QHBoxLayout, QWidget, QLabel)
from PySide6.QtCore import QAbstractTableModel, Qt


# Table model without pandas
class TableModel(QAbstractTableModel):
    def __init__(self, data, headers):
        super().__init__()
        self._data = data
        self._headers = headers

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._headers[section]
            if orientation == Qt.Vertical:
                return str(section + 1)
        return None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Window Resize with Keyboard Zoom")
        self.resize(800, 600)

        # Data
        self.data = [
            ["Alice", "25", "New York"],
            ["Bob", "30", "London"],
            ["Charlie", "35", "Tokyo"],
            ["Diana", "28", "Paris"],
            ["Eve", "33", "Berlin"]
        ]
        self.headers = ["Name", "Age", "City"]

        # Model and view
        self.model = TableModel(self.data, self.headers)
        self.table = QTableView()
        self.table.setModel(self.model)

        # Zoom label
        self.zoom_label = QLabel("Zoom: 100%")
        self.zoom_factor = 1.0

        # Zoom buttons
        self.zoom_in_btn = QPushButton("+")
        self.zoom_out_btn = QPushButton("-")
        self.reset_btn = QPushButton("Reset")

        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.reset_btn.clicked.connect(self.reset_zoom)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.zoom_in_btn)
        button_layout.addWidget(self.zoom_out_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.zoom_label)
        button_layout.addStretch()

        # Main layout
        layout = QVBoxLayout()
        layout.addLayout(button_layout)
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Allow window to receive key events
        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        """Handle keyboard zoom with +, -, and 0 keys."""
        if event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
            self.zoom_in()
        elif event.key() == Qt.Key_Minus:
            self.zoom_out()
        elif event.key() == Qt.Key_0:
            self.reset_zoom()
        else:
            super().keyPressEvent(event)

    def zoom_in(self):
        self.zoom_factor *= 1.2
        self.apply_zoom()

    def zoom_out(self):
        self.zoom_factor /= 1.2
        self.apply_zoom()

    def reset_zoom(self):
        self.zoom_factor = 1.0
        self.apply_zoom()

    def apply_zoom(self):
        # Scale font size
        font = self.table.font()
        font.setPointSize(int(8 * self.zoom_factor))
        self.table.setFont(font)

        # Scale row and column sizes
        self.table.horizontalHeader().setMinimumSectionSize(int(20 * self.zoom_factor))
        self.table.verticalHeader().setMinimumSectionSize(int(20 * self.zoom_factor))

        # Update zoom label
        self.zoom_label.setText(f"Zoom: {int(self.zoom_factor * 100)}%")

        # Resize the main window proportionally
        base_width, base_height = 800, 600
        new_width = int(base_width * self.zoom_factor)
        new_height = int(base_height * self.zoom_factor)
        self.resize(new_width, new_height)


# Run application
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())   

