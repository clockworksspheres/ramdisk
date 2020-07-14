#!/usr/bin/python
"""
@author: Roy Nielsen
"""
#--- Native python libraries
import sys
from optparse import OptionParser, SUPPRESS_HELP

sys.path.append("../..")
#--- non-native python libraries in this source tree
import ramdisk
from ramdisk.lib.run_commands import RunWith
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.lib.composite_menu import MenuComposite, MenuItem 
"""
parser = OptionParser(usage="\n\n%prog [options]\n\n", version="0.7.2")

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

if opts.device == 0:
    raise Exception("Cannot detach a device with no name..")
else:
    device = opts.device
"""
def basic():
    """ 
    """
    print "You have chosen a basic choice"
    print "Press any key to continue"
    # get input from the command line
    sys.stdin.readline()
    
def advanced1():
    """ 
    """
    print "You have chosen the first advanced option"
    print "Press any key to continue"
    # get input from the command line
    sys.stdin.readline()
    
def advanced2():
    """ 
    """
    print "You have chosen the second advanced option"
    print "Press any key to continue"
    # get input from the command line
    sys.stdin.readline()
    
def advanced3():
    """ 
    """
    print "You have chosen the third advanced option"
    print "Press any key to continue"
    # get input from the command line
    sys.stdin.readline()
       

if __name__ == "__main__" :
    """
    Example usage of this library
    
    @author: Roy Nielsen
    """
    main_menu = MenuComposite("Main")
    basic_choice = MenuItem("Basic Choice", basic)
    advanced_choice = MenuComposite("Advanced Choice")

    main_menu.setAnchor()

    main_menu.appendChild(basic_choice)
    main_menu.appendChild(advanced_choice)

    child1 = MenuItem("First advanced option", advanced1)
    child2 = MenuItem("Second advanced option", advanced2)
    child3 = MenuItem("Third advanced option", advanced3)

    advanced_choice.appendChild(child1)
    advanced_choice.appendChild(child2)
    advanced_choice.appendChild(child3)

    ##########
    # Call main menu
    main_menu.menuAction()

