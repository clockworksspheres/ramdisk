import sys
import unittest
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QScrollArea
)
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QWheelEvent


class ScrollWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Scroll Test")
        self.resize(400, 300)

        # Create tall content
        content = QWidget()
        layout = QVBoxLayout(content)
        for i in range(50):
            layout.addWidget(QLabel(f"Item {i + 1:02d} - Some content here"))
        layout.addStretch()

        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)


class TestScrollWithPySide6(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # One QApplication for the entire test run
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self):
        self.widget = ScrollWidget()
        self.widget.show()                    # Must be shown for events to work properly
        QApplication.processEvents()          # Let Qt initialize the widget fully

        # Find the scroll area and its vertical scrollbar
        self.scroll_area = self.widget.findChild(QScrollArea)
        self.vscrollbar = self.scroll_area.verticalScrollBar()

    def test_scroll_down_with_mouse_wheel(self):
        """Simulate mouse wheel scrolling down and check scrollbar position changes."""
        initial_value = self.vscrollbar.value()
        self.assertEqual(initial_value, 0, "Scrollbar should start at the top")

        # Move mouse to the center of the scroll area's viewport
        viewport = self.scroll_area.viewport()
        center_point = viewport.rect().center()
        QTest.mouseMove(viewport, center_point)

        # Simulate 15 wheel "notches" downward
        # Negative angleDelta.y() means scroll down
        for _ in range(15):
            wheel_event = QWheelEvent(
                center_point,                          # pos (local)
                viewport.mapToGlobal(center_point),    # globalPos
                QPoint(0, 0),                   # pixelDelta (usually empty)
                QPoint(0, -120),                 # angleDelta: -120 = one notch down
                Qt.NoButton,                           # buttons
                Qt.NoModifier,                         # modifiers
                Qt.ScrollUpdate,                       # phase
                False                                  # inverted
            )
            QApplication.postEvent(viewport, wheel_event)

        # Process all posted events
        QApplication.processEvents()

        final_value = self.vscrollbar.value()
        self.assertGreater(
            final_value, initial_value,
            f"Scrollbar did not move down. Initial: {initial_value}, Final: {final_value}"
        )

    def tearDown(self):
        self.widget.close()
        QApplication.processEvents()


if __name__ == "__main__":
    unittest.main(verbosity=2)

