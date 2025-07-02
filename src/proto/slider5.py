import sys


from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, QLineEdit, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator

sys.path.append("../")


#--- non-native python libraries in this source tree
from ramdisk.lib.dev.getMemStatus import GetMemStatus


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Slider with Editable Line Edit")

        # Create a central widget and a layout
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Create a label
        self.label = QLabel("Value: 0")
        layout.addWidget(self.label)

        #####
        # getMacosMemStatus.getAvailableMem
        getMemStatus = GetMemStatus()
        availableMem = getMemStatus.getAvailableMem()

        # Create a slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, availableMem)
        layout.addWidget(self.slider)

        # Create an editable line edit
        self.line_edit = QLineEdit()
        self.line_edit.setValidator(QIntValidator(0, 100))  # Ensure the input is within the slider's range
        layout.addWidget(self.line_edit)

        # Connect the slider's valueChanged signal to the update_line_edit method
        self.slider.valueChanged.connect(self.update_line_edit)

        # Connect the line edit's textChanged signal to the update_slider method
        self.line_edit.textChanged.connect(self.update_slider)

        # Set the central widget and layout
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def update_line_edit(self, value):
        self.line_edit.setText(str(value))
        self.label.setText(f"Value: {value}")

    def update_slider(self, text):
        try:
            value = int(text)
            self.slider.setValue(value)
            self.label.setText(f"Value: {value}")
        except ValueError:
            pass  # Ignore invalid input

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

