# PySide6 Widget Shadow

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

# DOES NOT WORK AS I INTENDED.  I want the window shadowed, not all the widgets in the window shadowed.

-----

# Found 7 relevant pages for: "PySide6 window shadow effect without widgets"

![🌐](https://imgs.search.brave.com/UimwW7-xdtNZmUG_Ido_geAdivV313qSVcBN6YRjjnw/rs:fit:32:32:1:0/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvM2MwY2NkN2I5/M2NhYzY5NmEyMDli/Njg1NzQ4MTE1Njk2/MDIzN2M3ZTNmN2Qx/MzQxYTE5YWMxZDVl/YmVmYWI2YS93d3cu/cHl0aG9uZ3Vpcy5j/b20v)

![🌐](https://imgs.search.brave.com/xxsA4YxzaR0cl-DBsH9-lpv2gsif3KMYgM87p26bs_o/rs:fit:32:32:1:0/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvYWQyNWM1NjA5/ZjZmZjNlYzI2MDNk/N2VkNmJhYjE2MzZl/MDY5ZTMxMDUzZmY1/NmU3NWIzNWVmMjk0/NTBjMjJjZi9naXRo/dWIuY29tLw)

![🌐](https://imgs.search.brave.com/UimwW7-xdtNZmUG_Ido_geAdivV313qSVcBN6YRjjnw/rs:fit:32:32:1:0/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvM2MwY2NkN2I5/M2NhYzY5NmEyMDli/Njg1NzQ4MTE1Njk2/MDIzN2M3ZTNmN2Qx/MzQxYTE5YWMxZDVl/YmVmYWI2YS93d3cu/cHl0aG9uZ3Vpcy5j/b20v)

![🌐](https://imgs.search.brave.com/UimwW7-xdtNZmUG_Ido_geAdivV313qSVcBN6YRjjnw/rs:fit:32:32:1:0/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvM2MwY2NkN2I5/M2NhYzY5NmEyMDli/Njg1NzQ4MTE1Njk2/MDIzN2M3ZTNmN2Qx/MzQxYTE5YWMxZDVl/YmVmYWI2YS93d3cu/cHl0aG9uZ3Vpcy5j/b20v)

+3

To apply a shadow effect to a PySide6 window without involving individual widgets, you can utilize the `QGraphicsDropShadowEffect` on the main window itself. This approach allows you to cast a shadow around the entire window, enhancing its visual appearance without affecting specific child widgets.

Here’s how you can implement a drop shadow effect directly on a PySide6 main window:

(in proto directory as windowShadow.py)

```
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the window properties
        self.setWindowTitle("Window with Shadow")
        self.setGeometry(100, 100, 400, 300)

        # Create a drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)  # Adjust the blur radius for more or less shadow
        shadow.setColor(Qt.black)  # Set the color of the shadow
        shadow.setOffset(5, 5)     # Set the offset of the shadow (x, y)

        # Apply the shadow effect to the main window
        self.setGraphicsEffect(shadow)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

# Explanation:

- **`QGraphicsDropShadowEffect`**: This class provides a drop shadow effect that can be applied to any `QGraphicsItem` or `QWidget`. In this case, it is applied to the `QMainWindow` to create a shadow around the entire window.
    
- **`setBlurRadius`**: This method controls how blurred the shadow appears. A higher value results in a softer, more spread-out shadow.
    
- **`setColor`**: This method sets the color of the shadow. By default, it is a semi-transparent dark gray, but you can change it to any `QColor`.
    
- **`setOffset`**: This method determines how far the shadow is offset from the window. The first value is the horizontal offset, and the second is the vertical offset.
    

This method ensures that the shadow effect is applied to the entire window, not just specific widgets, providing a clean and modern look to your application interface.7

AI-generated answer. Please verify critical facts.

-----

