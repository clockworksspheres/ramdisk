from PySide6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QLabel, 
                               QGraphicsView, QGraphicsScene, QGraphicsTextItem, 
                               QTableWidget, QTableWidgetItem, QPushButton, 
                               QVBoxLayout, QHBoxLayout, QWidget)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from PySide6.QtCore import Qt
import sys

class ZoomDemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Zoom Demo with Key Combinations")
        self.setGeometry(100, 100, 800, 600)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # QTextEdit
        self.text_edit = QTextEdit()
        self.text_edit.setText("Sample text in QTextEdit")
        layout.addWidget(QLabel("QTextEdit:"))
        layout.addWidget(self.text_edit)

        # QWebEngineView
        self.web_view = QWebEngineView()
        self.web_view.setHtml("<p>Sample text in QWebEngineView</p>")
        layout.addWidget(QLabel("QWebEngineView:"))
        layout.addWidget(self.web_view)

        # QLabel
        self.label = QLabel("Sample text in QLabel")
        layout.addWidget(QLabel("QLabel:"))
        layout.addWidget(self.label)

        # QGraphicsView
        self.graphics_view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.graphics_view.setScene(self.scene)
        text_item = QGraphicsTextItem("Sample text in QGraphicsView")
        self.scene.addItem(text_item)
        layout.addWidget(QLabel("QGraphicsView:"))
        layout.addWidget(self.graphics_view)

        # QTableWidget
        self.table = QTableWidget(3, 2)
        self.table.setHorizontalHeaderLabels(["Column 1", "Column 2"])
        for row in range(3):
            for col in range(2):
                self.table.setItem(row, col, QTableWidgetItem(f"Row {row+1}, Col {col+1}"))
        layout.addWidget(QLabel("QTableWidget:"))
        layout.addWidget(self.table)

        # Buttons for zooming
        button_layout = QHBoxLayout()
        zoom_in_button = QPushButton("Zoom In (Ctrl++)")
        zoom_out_button = QPushButton("Zoom Out (Ctrl+-)")
        reset_button = QPushButton("Reset Zoom (Ctrl+0)")
        button_layout.addWidget(zoom_in_button)
        button_layout.addWidget(zoom_out_button)
        button_layout.addWidget(reset_button)
        layout.addLayout(button_layout)

        # Connect buttons to zoom functions
        zoom_in_button.clicked.connect(self.zoom_in)
        zoom_out_button.clicked.connect(self.zoom_out)
        reset_button.clicked.connect(self.reset_zoom)

        # Keyboard shortcuts
        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_Plus), self, self.zoom_in)
        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_Equal), self, self.zoom_in)  # Handle Ctrl+=
        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_Minus), self, self.zoom_out)
        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_0), self, self.reset_zoom)

        # Track original font size for QLabel and QTableWidget
        self.label_base_font = self.label.font()
        self.table_base_font = self.table.font()
        self.current_label_size = self.label_base_font.pointSize()
        self.current_table_size = self.table_base_font.pointSize()
        self.graphics_scale = 1.0
        self.web_zoom_factor = 1.0

    def zoom_in(self):
        # QTextEdit: Increase font size
        self.text_edit.zoomIn(2)  # Increase by 2 points

        # QWebEngineView: Increase zoom factor
        self.web_zoom_factor *= 1.2
        self.web_view.setZoomFactor(self.web_zoom_factor)

        # QLabel: Increase font size
        self.current_label_size += 2
        new_font = QFont(self.label_base_font)
        new_font.setPointSize(self.current_label_size)
        self.label.setFont(new_font)

        # QGraphicsView: Scale up
        self.graphics_scale *= 1.2
        self.graphics_view.resetTransform()
        self.graphics_view.scale(self.graphics_scale, self.graphics_scale)

        # QTableWidget: Increase font size
        self.current_table_size += 2
        new_table_font = QFont(self.table_base_font)
        new_table_font.setPointSize(self.current_table_size)
        self.table.setFont(new_table_font)

    def zoom_out(self):
        # QTextEdit: Decrease font size
        self.text_edit.zoomOut(2)  # Decrease by 2 points

        # QWebEngineView: Decrease zoom factor
        self.web_zoom_factor /= 1.2
        self.web_view.setZoomFactor(self.web_zoom_factor)

        # QLabel: Decrease font size
        self.current_label_size = max(6, self.current_label_size - 2)  # Prevent too small
        new_font = QFont(self.label_base_font)
        new_font.setPointSize(self.current_label_size)
        self.label.setFont(new_font)

        # QGraphicsView: Scale down
        self.graphics_scale /= 1.2
        self.graphics_view.resetTransform()
        self.graphics_view.scale(self.graphics_scale, self.graphics_scale)

        # QTableWidget: Decrease font size
        self.current_table_size = max(6, self.current_table_size - 2)  # Prevent too small
        new_table_font = QFont(self.table_base_font)
        new_table_font.setPointSize(self.current_table_size)
        self.table.setFont(new_table_font)

    def reset_zoom(self):
        # QTextEdit: Reset to default font
        self.text_edit.setFont(self.label_base_font)  # Reset to app default

        # QWebEngineView: Reset zoom factor
        self.web_zoom_factor = 1.0
        self.web_view.setZoomFactor(self.web_zoom_factor)

        # QLabel: Reset font size
        self.current_label_size = self.label_base_font.pointSize()
        self.label.setFont(self.label_base_font)

        # QGraphicsView: Reset scale
        self.graphics_scale = 1.0
        self.graphics_view.resetTransform()

        # QTableWidget: Reset font size
        self.current_table_size = self.table_base_font.pointSize()
        self.table.setFont(self.table_base_font)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)  # Ensure proper scaling on high-DPI displays
    window = ZoomDemoWindow()
    window.show()
    sys.exit(app.exec())


