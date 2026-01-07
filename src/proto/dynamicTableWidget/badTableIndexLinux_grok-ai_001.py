from PySide6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem
import sys

app = QApplication(sys.argv)
table = QTableWidget(3, 3)
for i in range(3):
    for j in range(3):
        table.setItem(i, j, QTableWidgetItem(f"({i},{j})"))
table.show()
sys.exit(app.exec())


