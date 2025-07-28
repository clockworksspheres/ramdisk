#!/usr/bin/env -S python -u
"""


"""

#--- Native python libraries
import sys
import time
from optparse import OptionParser

from PySide6.QtWidgets import QApplication

#--- non-native python libraries in this source tree
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.ui.main import _CreateRamdisk
from ramdisk.RamDisk import RamDisk


parser = OptionParser(usage="\n\n%prog [options]\n\n", version="0.8.6")

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
    app = QApplication(sys.argv)
    """
    # Set up event logger
    init_event_logger(
        os.path.join(get_current_directory(), "event.log"),
        "%(asctime)s - %(levelname)s - %(message)s",
        stdout=True,
        debug=True if "--debug" in sys.argv else False,
    )
    """
    print("started app...")
    window = _CreateRamdisk()
    print("initiated window")
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

#if not ramdisk.success:
#    raise Exception("Ramdisk setup failed..")

#print(ramdisk.getDevice())
#time.sleep(9000)
