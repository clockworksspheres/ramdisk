# Drag and Drop Problems on Linux

## Code solution introduced into ramdisk-setup.py:

``` python
try:
    #####
    # Must make sure environment is set correctly if OS is Linux
    # and the window manager is Wayland.  Must be set before 
    # creating QApplication.  Does not check if X11 is running.
    if sys.platform.lower().startswith("linux"):
        logging.info("Found Linux Checking for Wayland")
        if os.environ.get("WAYLAND_DISPLAY") is not None or \
           os.environ.get("XDG_SESSION_TYPE") == "wayland":
            logging.info("Found Wayland, setting QT_QPA_PLATFORM")
            os.environ["QT_QPA_PLATFORM"] = "xcb"
except OSError:
    logging.info("Problem checking for and setting environment variable in linux")
```

Note, it does not currently check if X11 is active.  The code has to be before ``` app = QApplication(sys.argv) ```,  code is currently in global context.

# Discussion given by chatgpt v5

from chatgpt.com (version 5)

Recommended:

put 
``` 
export QT_QPA_PLATFORM=xcb 
``` 

in your ~/.bashrc (or equivalant in other shell)

-or-

run the command by:

```
QT_QPA_OLATFORM=xcb <script> <script-options>
```

## prompt: pyside6 drag drop linux problems

Drag & drop with **PySide6 on Linux** is unfortunately a common pain point. The problems usually come from a mix of **Qt bugs, Wayland vs X11 differences, and desktop environment behavior**.

Below is a **practical breakdown of the most common issues and fixes**.

---

## 1. Wayland vs X11 (BIGGEST SOURCE OF PROBLEMS)

### Symptoms

- Drag starts but drop never fires
    
- `dropEvent()` not called
    
- Cursor changes but nothing is delivered
    
- Works on Windows/macOS but not Linux
    

### Cause

Qt’s drag-and-drop support is **incomplete on Wayland** (especially for external drags or between apps).

### How to check

```bash
echo $XDG_SESSION_TYPE
```

- `wayland` → expect issues
    
- `x11` → drag & drop usually works
    

### Workarounds

**Option A: Force X11 (recommended)**

```bash
QT_QPA_PLATFORM=xcb your_app.py
```

Or log into an **Xorg session** instead of Wayland.

**Option B: Disable native drag**

```python
QtGui.QDrag.setDragCursor(QtGui.QPixmap(), QtCore.Qt.MoveAction)
```

Still buggy on Wayland, but helps sometimes.

---

## 2. `setAcceptDrops(True)` Missing or Overridden

### Symptoms

- No drag enter
    
- Drop ignored silently
    

### Required setup

```python
widget.setAcceptDrops(True)
```

And make sure **parent widgets are not blocking events**.

Also implement **both**:

```python
def dragEnterEvent(self, event):
    event.acceptProposedAction()

def dropEvent(self, event):
    event.acceptProposedAction()
```

If you forget `acceptProposedAction()`, Linux often rejects the drop.

---

## 3. MIME Type Mismatch (Very Common)

Linux is stricter about MIME types than Windows.

### Debug what you're receiving

```python
def dragEnterEvent(self, event):
    print(event.mimeData().formats())
    event.acceptProposedAction()
```

### Common MIME types

- Files:
    
    ```
    text/uri-list
    ```
    
- Internal Qt drags:
    
    ```
    application/x-qabstractitemmodeldatalist
    ```
    

### Example fix for file drops

```python
def dropEvent(self, event):
    for url in event.mimeData().urls():
        print(url.toLocalFile())
```

---

## 4. Drag Source Garbage-Collected (Subtle Linux Bug)

On Linux, **the QDrag object must stay alive**.

### ❌ Broken

```python
drag = QtGui.QDrag(self)
drag.exec()
```

### ✅ Correct

```python
self.drag = QtGui.QDrag(self)
self.drag.setMimeData(mime)
self.drag.exec()
```

If `QDrag` is GC’d early, the drop silently fails.

---

## 5. `exec()` vs `exec_()` Action Problems

Linux sometimes requires explicit actions.

### Recommended

```python
drag.exec(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction)
```

And in `dropEvent`:

```python
event.setDropAction(QtCore.Qt.CopyAction)
event.accept()
```

---

## 6. KDE / GNOME Desktop Quirks

### KDE

- Often stricter MIME handling
    
- Requires explicit `acceptProposedAction()`
    

### GNOME

- Wayland by default → broken external drag/drop
    
- X11 session fixes most issues
    

---

## 7. Known Qt / PySide6 Bugs

Some issues are **not your fault**:

- External file drag broken on Wayland
    
- Cross-application drag unreliable
    
- Some widgets (notably `QGraphicsView`) have incomplete DnD support
    

If this is **external drag/drop** on Wayland → **there is no full fix yet**.

---

## Minimal Known-Good Example (Internal Drag)

```python
class DropLabel(QtWidgets.QLabel):
    def __init__(self):
        super().__init__("Drop here")
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.setText(event.mimeData().text())
        event.acceptProposedAction()
```

---

## TL;DR (What Usually Fixes It)

✅ Run under **X11**  
✅ Call `setAcceptDrops(True)`  
✅ Use `acceptProposedAction()` everywhere  
✅ Keep `QDrag` alive  
✅ Match MIME types exactly

---

If you want, tell me:

- **Wayland or X11?**
    
- **Internal drag or external (files from Nautilus)?**
    
- **Which widget (QWidget, QListView, QGraphicsView)?**
    

I can give you a **targeted fix instead of guesswork**.