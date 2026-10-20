#!/usr/bin/env -S python -u
"""

"""
#--- Native python libraries
import sys
from pathlib import Path

parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

#--- non-native python libraries in this source tree
from ramdisk.lib.composite_menu import MenuComposite, MenuItem 

def basic():
    """ 
    """
    print("You have chosen a basic choice")
    print("Press any key to continue")
    # get input from the command line
    sys.stdin.readline()
    
def advanced1():
    """ 
    """
    print("You have chosen the first advanced option")
    print("Press any key to continue")
    # get input from the command line
    sys.stdin.readline()
    
def advanced2():
    """ 
    """
    print("You have chosen the second advanced option")
    print("Press any key to continue")
    # get input from the command line
    sys.stdin.readline()
    
def advanced3():
    """ 
    """
    print("You have chosen the third advanced option")
    print("Press any key to continue")
    # get input from the command line
    sys.stdin.readline()
       

if __name__ == "__main__" :
    """
    Example usage of this library
    
    
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

