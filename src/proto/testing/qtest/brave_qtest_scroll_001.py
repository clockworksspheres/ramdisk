import sys
import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt
import MargaritaMixer

app = QApplication(sys.argv)

class MargaritaMixerTest(unittest.TestCase):
    '''Test the margarita mixer GUI'''
    def setUp(self):
        '''Create the GUI'''
        self.form = MargaritaMixer.MargaritaMixer()

    def setFormToZero(self):
        '''Set all ingredients to zero'''
        self.form.ui.tequilaScrollBar.setValue(0)
        self.form.ui.tripleSecSpinBox.setValue(0)
        self.form.ui.limeJuiceLineEdit.setText("0.0")
        self.form.ui.iceHorizontalSlider.setValue(0)

    def test_tequilaScrollBar(self):
        '''Test the tequila scroll bar'''
        self.setFormToZero()
        # Test maximum value (clamped to 11)
        self.form.ui.tequilaScrollBar.setValue(12)
        self.assertEqual(self.form.ui.tequilaScrollBar.value(), 11)
        # Test minimum value (clamped to 0)
        self.form.ui.tequilaScrollBar.setValue(-1)
        self.assertEqual(self.form.ui.tequilaScrollBar.value(), 0)
        # Set valid value
        self.form.ui.tequilaScrollBar.setValue(5)
        # Simulate OK button click
        okWidget = self.form.ui.buttonBox.button(self.form.ui.buttonBox.Ok)
        QTest.mouseClick(okWidget, Qt.LeftButton)
        self.assertEqual(self.form.jiggers, 5)

    def test_defaults(self):
        '''Test default GUI values'''
        self.assertEqual(self.form.ui.tequilaScrollBar.value(), 8)
        self.assertEqual(self.form.ui.tripleSecSpinBox.value(), 4)
        self.assertEqual(self.form.ui.limeJuiceLineEdit.text(), "12.0")
        self.assertEqual(self.form.ui.iceHorizontalSlider.value(), 12)

if __name__ == "__main__":
    unittest.main()   

