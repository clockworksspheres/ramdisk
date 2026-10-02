import sys
import re

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QDialog, QDialogButtonBox, QLabel, QTextBrowser
)
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QFont

# ---------------------------------------------------------
# URL detection for clickable links
# ---------------------------------------------------------
url_regex = re.compile(r"(https?://[^\s]+)")


def linkify(text):
    def repl(m):
        url = m.group(1)
        return f'<a href="{url}">{url}</a>'
    return url_regex.sub(repl, text)


# ---------------------------------------------------------
# Stream object
# ---------------------------------------------------------
class ConsoleStream(QObject):
    text_emitted = Signal(str, str)  # html, raw

    def __init__(self, logfile=None):
        super().__init__()
        self.logfile = logfile

    def write(self, text):
        if not text:
            return
        # keep empty lines if you want them, otherwise:
        # if not text.strip(): return

        html = linkify(text.rstrip("\n"))  # avoid double newlines from append
        self.text_emitted.emit(html, text)

        if self.logfile:
            with open(self.logfile, "a", encoding="utf-8") as f:
                f.write(text)

    def flush(self):
        pass


# ---------------------------------------------------------
# SimpleConsole
# ---------------------------------------------------------
class SimpleConsole(QTextBrowser):
    def __init__(self):
        super().__init__()

        self.font_size = 12
        font = QFont("Menlo")
        if not font.exactMatch():
            font = QFont("Consolas")
        if not font.exactMatch():
            font = QFont("DejaVu Sans Mono")
        font.setStyleHint(QFont.Monospace)
        font.setFixedPitch(True)
        font.setPointSize(self.font_size)
        self.setFont(font)

        self.setOpenExternalLinks(True)
        self.setOpenLinks(True)

    def append_html(self, html):
        self.append(html)

    def zoom_in(self):
        self.font_size += 1
        self._apply_font()

    def zoom_out(self):
        if self.font_size > 6:
            self.font_size -= 1
        self._apply_font()

    def reset_zoom(self):
        self.font_size = 12
        self._apply_font()

    def clear_console(self):
        self.clear()

    def _apply_font(self):
        font = self.font()
        font.setPointSize(self.font_size)
        self.setFont(font)


# ---------------------------------------------------------
# Console Dialog
# ---------------------------------------------------------
class ConsoleDialog(QDialog):
    def __init__(self, parent=None, title="Console"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(850, 550)

        layout = QVBoxLayout(self)

        self.console = SimpleConsole()
        layout.addWidget(self.console)

        # Controls
        controls = QHBoxLayout()
        btn_clear = QPushButton("Clear")
        btn_clear.clicked.connect(self.console.clear_console)

        btn_zoom_in = QPushButton("Zoom +")
        btn_zoom_in.clicked.connect(self.console.zoom_in)

        btn_zoom_out = QPushButton("Zoom -")
        btn_zoom_out.clicked.connect(self.console.zoom_out)

        btn_reset = QPushButton("Reset Zoom")
        btn_reset.clicked.connect(self.console.reset_zoom)

        controls.addWidget(btn_clear)
        controls.addWidget(btn_zoom_in)
        controls.addWidget(btn_zoom_out)
        controls.addWidget(btn_reset)
        controls.addStretch()
        layout.addLayout(controls)

        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def append_html(self, html):
        self.console.append_html(html)


