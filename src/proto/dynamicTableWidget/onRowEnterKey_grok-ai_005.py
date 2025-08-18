from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QSpinBox, QVBoxLayout, QWidget
from PySide6.QtCore import QObject, QEvent

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Event Filter Example")

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Add a spin box
        self.spin_box = QSpinBox()
        self.spin_box.setRange(0, 100)
        layout.addWidget(self.spin_box)

        # Add a tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(QWidget(), "Tab 1")
        self.tabs.addTab(QWidget(), "Tab 2")
        layout.addWidget(self.tabs)

        # Install event filter on the tab bar
        self.tabs.tabBar().installEventFilter(self)

        # Connect spin box signal to control tab interaction
        self.spin_box.valueChanged.connect(self.update_tab_interaction)

    def update_tab_interaction(self, value):
        # Disable tab bar interaction when value > 5
        self.tabs.tabBar().setDisabled(value > 5)

    def eventFilter(self, obj, event):
        # Example: Filter mouse press events on the tab bar
        if obj == self.tabs.tabBar() and event.type() == QEvent.MouseButtonPress:
            if self.spin_box.value() > 5:
                return True  # Block the event
        return super().eventFilter(obj, event)

# Run the application
app = QApplication([])
window = MainWindow()
window.show()
app.exec()   

