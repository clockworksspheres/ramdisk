from PySide6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QLabel, 
                               QGraphicsView, QGraphicsScene, QGraphicsTextItem, 
                               QTableWidget, QTableWidgetItem, QPushButton, 
                               QVBoxLayout, QHBoxLayout, QWidget, QSizePolicy, QHeaderView)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from PySide6.QtCore import Qt
import sys

class ZoomResizeDemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()  # Correctly initialize QMainWindow
        self.setWindowTitle("PySide6 Window, Widgets, and Font Resize Demo (macOS)")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(400, 300)  # Allow resizing with minimum size

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # QTextEdit
        self.text_edit = QTextEdit()
        self.text_edit.setText("QTextEdit (default font, resizable)")
        self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(QLabel("QTextEdit:"))
        layout.addWidget(self.text_edit)

        # QWebEngineView
        self.web_view = QWebEngineView()
        self.web_view.setHtml("<p>QWebEngineView (default font, resizable)</p>")
        self.web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(QLabel("QWebEngineView:"))
        layout.addWidget(self.web_view)

        # QLabel
        self.label = QLabel("QLabel (default font, resizable)")
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(QLabel("QLabel:"))
        layout.addWidget(self.label)

        # QGraphicsView
        self.graphics_view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.graphics_view.setScene(self.scene)
        text_item = QGraphicsTextItem("QGraphicsView (default font, resizable)")
        self.scene.addItem(text_item)
        self.graphics_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(QLabel("QGraphicsView:"))
        layout.addWidget(self.graphics_view)

        # QTableWidget
        self.table = QTableWidget(3, 2)
        self.table.setHorizontalHeaderLabels(["Column 1", "Column 2"])
        for row in range(3):
            for col in range(2):
                self.table.setItem(row, col, QTableWidgetItem(f"Row {row+1}, Col {col+1}"))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Stretch columns
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(QLabel("QTableWidget:"))
        layout.addWidget(self.table)

        # Buttons for font resizing (zooming)
        button_layout = QHBoxLayout()
        zoom_in_button = QPushButton("Zoom In (Cmd++)")
        zoom_out_button = QPushButton("Zoom Out (Cmd+-)")
        reset_button = QPushButton("Reset Zoom (Cmd+0)")
        button_layout.addWidget(zoom_in_button)
        button_layout.addWidget(zoom_out_button)
        button_layout.addWidget(reset_button)
        layout.addLayout(button_layout)

        # Connect buttons to zoom functions
        zoom_in_button.clicked.connect(self.zoom_in)
        zoom_out_button.clicked.connect(self.zoom_out)
        reset_button.clicked.connect(self.reset_zoom)

        # Keyboard shortcuts (Command for macOS, Ctrl as fallback)
        QShortcut(QKeySequence(Qt.META | Qt.Key_Plus), self, self.zoom_in)  # Cmd++
        QShortcut(QKeySequence(Qt.META | Qt.Key_Equal), self, self.zoom_in)  # Cmd+=
        QShortcut(QKeySequence(Qt.META | Qt.Key_Minus), self, self.zoom_out)  # Cmd+-
        QShortcut(QKeySequence(Qt.META | Qt.Key_0), self, self.reset_zoom)  # Cmd+0
        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_Plus), self, self.zoom_in)  # Ctrl++ fallback
        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_Equal), self, self.zoom_in)  # Ctrl+=
        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_Minus), self, self.zoom_out)  # Ctrl+-
        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_0), self, self.reset_zoom)  # Ctrl+0

        # Track original font sizes and table dimensions
        self.label_base_font = self.label.font()
        self.table_base_font = self.table.font()
        self.current_label_size = self.label_base_font.pointSize()
        self.current_table_size = self.table_base_font.pointSize()
        self.graphics_scale = 1.0
        self.web_zoom_factor = 1.0
        self.base_row_height = self.table.rowHeight(0) or 30  # Default if 0
        self.base_column_width = self.table.columnWidth(0) or 100  # Default if 0
        self.current_row_height = self.base_row_height
        self.current_column_width = self.base_column_width

    def zoom_in(self):
        # QTextEdit: Increase font size
        self.text_edit.zoomIn(2)

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

        # QTableWidget: Increase font size and cell dimensions
        self.current_table_size += 2
        self.current_row_height = int(self.current_row_height * 1.2)
        self.current_column_width = int(self.current_column_width * 1.2)
        new_table_font = QFont(self.table_base_font)
        new_table_font.setPointSize(self.current_table_size)
        self.table.setFont(new_table_font)
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, self.current_row_height)
        for col in range(self.table.columnCount()):
            self.table.setColumnWidth(col, self.current_column_width)

    def zoom_out(self):
        # QTextEdit: Decrease font size
        self.text_edit.zoomOut(2)

        # QWebEngineView: Decrease zoom factor
        self.web_zoom_factor /= 1.2
        self.web_view.setZoomFactor(self.web_zoom_factor)

        # QLabel: Decrease font size
        self.current_label_size = max(6, self.current_label_size - 2)
        new_font = QFont(self.label_base_font)
        new_font.setPointSize(self.current_label_size)
        self.label.setFont(new_font)

        # QGraphicsView: Scale down
        self.graphics_scale /= 1.2
        self.graphics_view.resetTransform()
        self.graphics_view.scale(self.graphics_scale, self.graphics_scale)

        # QTableWidget: Decrease font size and cell dimensions
        self.current_table_size = max(6, self.current_table_size - 2)
        self.current_row_height = max(20, int(self.current_row_height / 1.2))
        self.current_column_width = max(50, int(self.current_column_width / 1.2))
        new_table_font = QFont(self.table_base_font)
        new_table_font.setPointSize(self.current_table_size)
        self.table.setFont(new_table_font)
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, self.current_row_height)
        for col in range(self.table.columnCount()):
            self.table.setColumnWidth(col, self.current_column_width)

    def reset_zoom(self):
        # QTextEdit: Reset font size
        self.text_edit.setFont(self.label_base_font)

        # QWebEngineView: Reset zoom factor
        self.web_zoom_factor = 1.0
        self.web_view.setZoomFactor(self.web_zoom_factor)

        # QLabel: Reset font size
        self.current_label_size = self.label_base_font.pointSize()
        self.label.setFont(self.label_base_font)

        # QGraphicsView: Reset scale
        self.graphics_scale = 1.0
        self.graphics_view.resetTransform()

        # QTableWidget: Reset font size and cell dimensions
        self.current_table_size = self.table_base_font.pointSize()
        self.current_row_height = self.base_row_height
        self.current_column_width = self.base_column_width
        self.table.setFont(self.table_base_font)
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, self.current_row_height)
        for col in range(self.table.columnCount()):
            self.table.setColumnWidth(col, self.current_column_width)

    def resizeEvent(self, event):
        # Debug print to confirm window resizing
        print(f"Window resized to: {event.size().width()}x{event.size().height()}")
        super().resizeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)  # High-DPI support
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)  # Better rendering on Retina displays
    window = ZoomResizeDemoWindow()
    window.show()
    sys.exit(app.exec())

