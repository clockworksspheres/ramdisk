#!/usr/bin/env -S python -u
"""
@author: Roy Nielsen
"""

#--- Native python libraries
import re
import sys
from optparse import OptionParser, SUPPRESS_HELP

sys.path.append("../")

#--- non-native python libraries in this source tree
from ramdisk.macRamdisk import detach
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp

parser = OptionParser(usage="\n\n%prog [options]", version="0.9.2")

parser.add_option("-D", "--detach", dest="device", default="",
                  help="Name of the device to detach")
parser.add_option("-d", "--debug", action="store_true", dest="debug", 
                  default=0, help="Print debug messages")
parser.add_option("-v", "--verbose", action="store_true", 
                  dest="verbose", default=0, 
                  help="Print status messages")

(opts, args) = parser.parse_args()

if opts.verbose != 0:
    level = CyLogger(level=lp.INFO)
elif opts.debug != 0:
    level = CyLogger(level=lp.DEBUG)
else:
    level=lp.WARNING

if (not isinstance(opts.device, str) and \
   re.match("^[A-Za-z0-9/]+$", opts.device)) or not opts.device:
    print("Cannot detach a device with no name..")
    parser.print_help()
else:
    device = opts.device

    logger = CyLogger(level=level)
    logger.initializeLogs()
        
    if detach(device):
        logger.log(lp.INFO, r"Successfully detached disk: " + str(device).strip())
    else:
        logger.log(lp.ERROR, r"Couldn't detach disk: " + str(device).strip())
        parser.print_help()

