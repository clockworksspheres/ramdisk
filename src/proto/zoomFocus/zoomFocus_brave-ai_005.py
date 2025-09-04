import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt

def main():
    app = QApplication(sys.argv)
    # High DPI scaling is enabled by default in PySide6, so no need to set AA_EnableHighDpiScaling
    window = QMainWindow()
    window.setWindowTitle("High DPI Example")
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()


