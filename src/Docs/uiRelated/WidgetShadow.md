PySide6 Widget Shadow

To add a shadow effect to a widget in PySide6, you can use the `QGraphicsDropShadowEffect` class. This class allows you to create a drop shadow effect for any widget. Here's how you can do it:

1. **Create a `QGraphicsDropShadowEffect` object**:
   ```python
   shadow = QGraphicsDropShadowEffect()
   ```

2. **Set the properties of the shadow**:
   - **Blur radius**: Controls the blurriness of the shadow. A higher value results in a more blurred shadow.
     ```python
     shadow.setBlurRadius(10)
     ```
   - **X offset**: Controls the horizontal offset of the shadow.
     ```python
     shadow.setXOffset(5)
     ```
   - **Y offset**: Controls the vertical offset of the shadow.
     ```python
     shadow.setYOffset(5)
     ```

3. **Apply the shadow effect to the widget**:
   ```python
   widget.setGraphicsEffect(shadow)
   ```

For example, to apply a drop shadow to a button, you can use the following code:
```python
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QGraphicsDropShadowEffect

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(5)
        shadow.setYOffset(5)
        self.button = QPushButton(self)
        self.button.setGraphicsEffect(shadow)

if __name__ == '__main__':
    app = QApplication([])
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec()
```

This code creates a main window with a button that has a drop shadow effect applied to it  The `QGraphicsDropShadowEffect` class provides a drop shadow effect, and you can customize the shadow's appearance by adjusting the blur radius, offset, and color  Additionally, there are other methods and properties available to further customize the shadow effect, such as setting the color of the shadow 

-----

