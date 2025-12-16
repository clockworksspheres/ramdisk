from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QApplication

class CustomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Signal Example")
        
        # Create UI elements
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Demonstrating button box signals"))
        
        # Create button box with OK and Cancel
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        
        # Connect standard signals
        self.button_box.accepted.connect(self.on_accepted)
        self.button_box.rejected.connect(self.on_rejected)
        
        layout.addWidget(self.button_box)
        self.setLayout(layout)
    
    def on_accepted(self):
        # Custom logic when OK is clicked
        print("OK button clicked - performing custom actions")
        # Emit custom signals, save data, etc.
        # Dialog will close automatically with Accepted status
        self.accept()  # Explicitly accept
    
    def on_rejected(self):
        print("Cancel button clicked")
        self.reject()

# Usage
app = QApplication([])
dialog = CustomDialog()
result = dialog.exec()
print(f"Dialog result: {'Accepted' if result else 'Rejected'}")   

