import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Default Button on Enter")
        
        layout = QVBoxLayout()
        
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Press Enter to submit...")
        
        self.result_label = QLabel("No input yet")
        
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.on_submit)
        
        # Connect the 'Enter' key press in QLineEdit to the submit function
        self.line_edit.returnPressed.connect(self.on_submit)
        
        layout.addWidget(self.line_edit)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.result_label)
        
        self.setLayout(layout)
    
    def on_submit(self):
        text = self.line_edit.text()
        self.result_label.setText(f"You entered: {text}")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())   

