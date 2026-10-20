#!/usr/bin/env -S python -u
"""
"""

#--- Native python libraries
import os
import sys
from optparse import OptionParser
from datetime import datetime

#from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

#--- non-native python libraries in this source tree
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.ui.main import _CreateRamdisk
from ramdisk.RamDisk import RamDisk


parser = OptionParser(usage="\n\n%prog [options]\n\n", version="2.8.6")

size = str(500) # in Megabytes
parser.add_option("-s", "--size", dest="size",
                  default=str(size),
                  help="Size of ramdisk you want to create in 1 Megabyte blocks")
parser.add_option("-m", "--mount-point", dest="mntpnt",
                  default="",
                  help="Name of the mountpoint you want to mount to")
parser.add_option("-g", "--gui", action="store_true", dest="gui",
                  default=0, help="Print debug messages")
parser.add_option("-d", "--debug", action="store_true", dest="debug",
                  default=0, help="Print debug messages")
parser.add_option("-v", "--verbose", action="store_true",
                  dest="verbose", default=0,
                  help="Print status messages")

(opts, args) = parser.parse_args()

if len(sys.argv) == 1:
    opts.gui = True

if opts.verbose != 0:
    level = lp.INFO
elif opts.debug != 0:
    level = level=lp.DEBUG
else:
    level=lp.WARNING

logger = CyLogger(level)
logger.initializeLogs()

if opts.size:
    size = str(opts.size)  # in Megabytes
if opts.gui:

    def is_night(start_hour=18, end_hour=6):
        """Returns True if current time is between start_hour and end_hour."""
        current_hour = datetime.now().hour
        if start_hour > end_hour: # Spans midnight (e.g., 18:00 to 06:00)
            return current_hour >= start_hour or current_hour < end_hour
        return start_hour <= current_hour < end_hour

    def set_dark_palette(app):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(106, 106, 106))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(42, 42, 42))
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        app.setPalette(dark_palette)

    def set_light_palette(app):
        # Reverting to default usually requires clearing the palette or setting a standard one
        app.setPalette(QApplication.style().standardPalette())

    try:
        #####
        # Must make sure environment is set correctly if OS is Linux
        # and the window manager is Wayland.  Must be set before 
        # creating QApplication.  Does not check if X11 is running.
        if sys.platform.lower().startswith("linux"):
            logger.log(lp.INFO, "Found Linux Checking for Wayland")
            if os.environ.get("WAYLAND_DISPLAY") is not None or \
               os.environ.get("XDG_SESSION_TYPE") == "wayland":
                logger.log(lp.INFO, "Found Wayland, setting QT_QPA_PLATFORM")
                os.environ["QT_QPA_PLATFORM"] = "xcb"
    except OSError:
        logger.log(lp.INFO, "Problem checking for and setting environment variable in linux")

    app = QApplication(sys.argv)

    if sys.platform.lower().startswith("win"):
        app.setStyle("Fusion") # Required for dark mode on Windows

    if is_night():
        set_dark_palette(app)
    else:
        set_light_palette(app)
    #set_dark_palette(app)

    print("started app...")
    window = _CreateRamdisk()
    print("initiated window")
    # window.setCentralWidget(QPushButton("Night Mode Active" if is_night() else "Day Mode Active"))
    print("initiating app color mode")
    window.show()
    print("showing window...")
    window.raise_()
    print("raising_ window")
    sys.exit(app.exec())
else:
    mntpnt = opts.mntpnt

    ramdisk = RamDisk(str(size), str(mntpnt), logger)
    ramdisk.getNlogData()
    ramdisk.getNprintData()

