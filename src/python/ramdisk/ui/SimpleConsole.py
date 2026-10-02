# Created for the mvm project: https://github.com/clockworksspheres/mvm

import sys
import re
import argparse

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QTextBrowser, QStackedWidget
)
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QFont

# ---------------------------------------------------------
# URL detection for clickable links
# ---------------------------------------------------------
url_regex = re.compile(r"(https?://[^\s]+)")


def linkify(text):
    """Wrap URLs in <a> tags."""
    def repl(m):
        url = m.group(1)
        return f'<a href="{url}">{url}</a>'
    return url_regex.sub(repl, text)


# ---------------------------------------------------------
# Stream object (stdout/stderr redirection)
# ---------------------------------------------------------
class ConsoleStream(QObject):
    text_emitted = Signal(str, str)  # html_text, raw_text

    def __init__(self, logfile=None):
        super().__init__()
        self.logfile = logfile

    def write(self, text):
        if not text.strip():
            return

        html = linkify(text)
        self.text_emitted.emit(html, text)

        if self.logfile:
            with open(self.logfile, "a", encoding="utf-8") as f:
                f.write(text + "\n")

    def flush(self):
        pass


# ---------------------------------------------------------
# Simple QTextBrowser console
# ---------------------------------------------------------
class SimpleConsole(QTextBrowser):
    def __init__(self):
        super().__init__()

        # Fixed-width font for proper alignment
        self.font_size = 12
        font = QFont("Menlo")  # macOS default monospace
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
# Main Window (NO THREADS)
# ---------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self, args):
        super().__init__()
        self.setWindowTitle("Simple PySide6 Console (No Colors, No Threads)")

        # Stacked widget
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Page 1
        page1 = QWidget()
        layout1 = QVBoxLayout(page1)
        btn_console = QPushButton("Open Console")
        btn_demo = QPushButton("Run Demo Output")
        layout1.addWidget(btn_console)
        layout1.addWidget(btn_demo)

        # Page 2 (console)
        page2 = QWidget()
        layout2 = QVBoxLayout(page2)
        self.console = SimpleConsole()
        layout2.addWidget(self.console)
        btn_back = QPushButton("Back")
        layout2.addWidget(btn_back)

        self.stack.addWidget(page1)
        self.stack.addWidget(page2)

        btn_console.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_demo.clicked.connect(self.demo_output)

        # Create stdout/stderr streams
        self.stdout_stream = ConsoleStream(logfile=args.logfile)
        self.stderr_stream = ConsoleStream(logfile=args.logfile)

        self.stdout_stream.text_emitted.connect(self.console.append_html)
        self.stderr_stream.text_emitted.connect(self.console.append_html)

        # Redirect Python stdout/stderr
        sys.stdout = self.stdout_stream
        sys.stderr = self.stderr_stream

        # Initial messages
        print("Application started.")
        print(f"Argparse message: {args.message}")

        if args.logfile:
            print(f"Logging to file: {args.logfile}")

    # Demo output without threads
    def demo_output(self):
        print("This is a normal line.")
        print("This is stderr!", file=sys.stderr)
        print("Clickable link: https://www.qt.io")
        print("Another link: https://www.python.org")
        print("Back to normal text.")


# ---------------------------------------------------------
# argparse
# ---------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Simple PySide6 Console (No Colors)")
    parser.add_argument(
        "-m", "--message",
        type=str,
        default="Hello from argparse!",
        help="Startup message"
    )
    parser.add_argument(
        "-l", "--logfile",
        type=str,
        default=None,
        help="Optional log file to mirror console output"
    )
    return parser.parse_args()


# ---------------------------------------------------------
# Main entry point
# ---------------------------------------------------------
def main():
    args = parse_args()

    app = QApplication(sys.argv)
    window = MainWindow(args)
    window.resize(700, 450)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()


