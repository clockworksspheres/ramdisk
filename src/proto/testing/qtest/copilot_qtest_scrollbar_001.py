import sys
import unittest
from PySide6.QtWidgets import QApplication, QScrollBar
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt, QPoint

# QApplication must be created once for tests
app = QApplication.instance() or QApplication(sys.argv)


class TestScrollBarClick(unittest.TestCase):
    def setUp(self):
        # Create a fresh scrollbar for each test
        self.scrollbar = QScrollBar(Qt.Vertical)
        self.scrollbar.setMinimum(0)
        self.scrollbar.setMaximum(100)
        self.scrollbar.setValue(50)  # start in the middle
        self.scrollbar.show()

    def tearDown(self):
        self.scrollbar.close()

    def test_click_increase_value(self):
        """Simulate clicking near the bottom of the scrollbar"""
        rect = self.scrollbar.rect()
        click_point = QPoint(rect.center().x(), rect.bottom() - 5)

        QTest.mouseClick(self.scrollbar, Qt.LeftButton, Qt.NoModifier, click_point)

        # After clicking near the bottom, value should increase
        self.assertGreater(self.scrollbar.value(), 50)

    def test_click_decrease_value(self):
        """Simulate clicking near the top of the scrollbar"""
        rect = self.scrollbar.rect()
        click_point = QPoint(rect.center().x(), rect.top() + 5)

        QTest.mouseClick(self.scrollbar, Qt.LeftButton, Qt.NoModifier, click_point)

        # After clicking near the top, value should decrease
        self.assertLess(self.scrollbar.value(), 50)


if __name__ == "__main__":
    unittest.main()

