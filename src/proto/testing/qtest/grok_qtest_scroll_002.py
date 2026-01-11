import os
import sys
import unittest
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QScrollArea
)
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QWheelEvent

# Force headless/offscreen mode (critical for CI/headless)
os.environ["QT_QPA_PLATFORM"] = "offscreen"

class ScrollWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Scroll Test (Headless)")
        self.resize(400, 300)

        content = QWidget()
        layout = QVBoxLayout(content)
        for i in range(50):
            layout.addWidget(QLabel(f"Item {i + 1:02d} - Some content here"))
        layout.addStretch()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)


class TestScrollWithPySide6(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Force offscreen platform via args if env var not sufficient
        sys.argv += ['-platform', 'offscreen']  # Alternative/backup
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self):
        self.widget = ScrollWidget()
        # NO show() needed in offscreen mode!
        QApplication.processEvents()  # Initialize layout/geometry

        self.scroll_area = self.widget.findChild(QScrollArea)
        self.vscrollbar = self.scroll_area.verticalScrollBar()

        # Ensure scrollbar range is valid (content taller than viewport)
        self.assertGreater(self.vscrollbar.maximum(), 0)

    def test_scroll_down_with_mouse_wheel(self):
        initial_value = self.vscrollbar.value()
        self.assertEqual(initial_value, 0, "Scrollbar should start at top")

        viewport = self.scroll_area.viewport()
        center_point = viewport.rect().center()

        # Simulate 20 wheel notches down
        for _ in range(20):
            wheel_event = QWheelEvent(
                center_point,
                viewport.mapToGlobal(center_point),
                QPoint(0, 0),          # pixelDelta
                QPoint(0, -120),       # angleDelta: negative = down
                Qt.NoButton,
                Qt.NoModifier,
                Qt.ScrollUpdate,
                False
            )
            QApplication.postEvent(viewport, wheel_event)

        QApplication.processEvents()  # Process all events

        final_value = self.vscrollbar.value()
        self.assertGreater(
            final_value, initial_value,
            f"Scrollbar did not move. Initial: {initial_value}, Final: {final_value}"
        )

    def tearDown(self):
        self.widget.deleteLater()  # Clean up without closing window
        QApplication.processEvents()


if __name__ == "__main__":
    unittest.main(verbosity=2)


