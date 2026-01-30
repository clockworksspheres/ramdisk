import sys
import unittest
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QScrollBar, QLabel
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

class ScrollBarWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.value = 0
        layout = QVBoxLayout()
        self.scrollbar = QScrollBar(Qt.Horizontal)
        self.label = QLabel("Value: 0")
        layout.addWidget(self.label)
        layout.addWidget(self.scrollbar)
        self.setLayout(layout)
        self.scrollbar.valueChanged.connect(self.update_label)

    def update_label(self, value):
        self.value = value
        self.label.setText(f"Value: {value}")

class TestScrollBar(unittest.TestCase):
    def setUp(self):
        self.app = QApplication.instance() or QApplication([])
        self.widget = ScrollBarWidget()
        self.widget.show()

    def test_scrollbar_range(self):
        sb = self.widget.scrollbar
        sb.setValue(50)
        self.assertEqual(sb.value(), 50)

        # Test minimum
        sb.setValue(-10)
        self.assertEqual(sb.value(), 0)

        # Test maximum
        sb.setValue(200)
        self.assertEqual(sb.value(), 99)  # Default max is 99

    def test_scrollbar_interaction(self):
        sb = self.widget.scrollbar
        QTest.mouseClick(sb, Qt.LeftButton)
        self.assertIn(sb.value(), range(0, 100))

if __name__ == "__main__":
    unittest.main()   

