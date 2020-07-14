"""
If this script is run rather than used as a library, it will show how it can
be used to create a basic menu.

@author: Roy Nielsen
"""
from __future__ import absolute_import
# system libraries
import re
import sys
import tty
import termios

sys.path.append("..")
from ..lib.loggers import CyLogger
from ..lib.loggers import LogPriority as lp
from ..lib.run_commands import RunWith, runMyThreadCommand

class NotASaneNameError(Exception):
    """
    Meant for being thrown when an action/class being run/instanciated is not
    applicable for the running operating system.

    @author: Roy Nielsen
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class NotASaneActionError(Exception):
    """
    Meant for being thrown when an action/class being run/instanciated is not
    applicable for the running operating system.

    @author: Roy Nielsen
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

logger = CyLogger()

class MenuComponent(object):
    """
    """
    g_dict = {"default": "default"}
    def __init__(self, name, action=False):
        """
        """
        #####
        # Check name and action first.
        if self.isSaneAction(name):
            self.name = name
            if self.isSaneAction(action):
                self.action = action
            else:
                logger.log(lp.INFO, "Parse error - (" + str(action) + \
                                         ") not a valid action.")
        else:
            raise NotASaneNameError("Parse error - (" + str(name) + \
                                    ") not a valid name.")

        if self.isSaneAction(action):
            self.action = action

        self.runner = RunWith(logger)
        self.logger = CyLogger(debug_mode=True)
        self.logger.initializeLogs()
        
        #####
        # Required specific to the menu system
        self.g_dict = {}
        self.action = False
        self.anchor = False
        
        self.previous = None

        self.run = runMyThreadCommand

    def menuAction(self, *args, **kwargs):
        """
        """
        pass

    def get_key(self):
        """
        Wait for a keypress and return a single character string.

        If either of the Unix-specific tty or termios are not found
        we allow the ImportError to proagate..
        
        @author: unknown
        """
        fd = sys.stdin.fileno()
        original_attributes = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, original_attributes)
        return ch

    def getValue(self, g_key=False):
        """
        Get the value of a psudo-global value.  Not using python globals.
        Child classes should be able to look up these values, found in the 
        MenuComposite with the Anchor (first MenuComponent)
        
        @author: Roy Nielsen
        """
        retval = False
        if isinstance(g_key, basestring):
            while not self.anchor:
                self = self.previous
            try:
                retval = self.g_dict[g_key]
            except IndexError:
                print "Damn it Jim!!! Key: " + str(g_key) + " is missing..."

        return retval

    def setValue(self, g_key=False, g_value=None):
        """
        Set a value in the 'anchor' node of the menu.

        s_value is the name of the self.conf.set_<var-name> routine to set
                that variable.
        equals is the value we want to set to
        type is the type, either string of int

        Author: Roy Nielsen
        """
        success = False
        if isinstance(g_key, basestring) and \
           isinstance(g_value, (bool, basestring, int)):
            while not self.anchor :
                self = self.previous
            try:
                self.g_dict[g_key] = g_value
                success = True
            except (KeyError, IndexError), err:
                pass

        return success

    def isSaneName(self, name=False):
        """
        Perform validation on the name to make sure it doen't have any
        potentially mallicious characters.
        """
        sane = False
        if isinstance(name, basestring):
            try:
                re.match("^[A-Za-z0-9\s\.,]*", name)
            except:
                pass
            else:
                sane = True
        return sane

    def isSaneAction(self, action=False):
        """
        Perform validation on the name to make sure it doen't have any
        potentially mallicious characters.
        """
        sane = False
        action = str(action)
        if isinstance(action, (basestring, bool)) and action is not True:
            try:
                re.match("^[A-Za-z0-9]*", str(action))
            except:
                pass
            else:
                sane = True
        elif isinstance(action, bool):
            sane = True

        return sane

    def printName(self) :
        """
        Print the name of the MenuItem for the menu.

        Author: Roy Nielsen
        """
        print self.name


class MenuItem(MenuComponent) :
    """
    Leaf class - Inherits the MenuComponent class.

    Author: Roy Nielsen
    """
    def __init__(self, name, action=False) :
        """
        Initialization method.  Initialize the MenuComponent, then set the "name"
        of the menu item.
        """
        MenuComponent.__init__(self, name)
        try:
            self.isSaneName(name)
        except NotASaneNameError, err:
            self.logger.log(lp.DEBUG, str(err))
            self.logger.log(lp.DEBUG, "name or action: " + str(name) + " is not valid.")
        else:
            self.name = name

        try:
            self.isSaneAction(action)
        except NotASaneActionError, err:
            self.logger.log(lp.DEBUG, str(err))
            self.logger.log(lp.DEBUG, "name or action: " + str(action) + " is not valid.")
        else:
            self.action = action

    def menuAction(self, *args, **kwargs):
        """
        Node specific action method. -- Run the function that is passed in.

        Author: Roy Nielsen
        """
        success = False
        if self.action:
            if self.isSaneAction(self.action):
                success = self.action(*args, **kwargs)

            print self.name

        return success

        
class MenuComposite(MenuComponent) :
    """
    Composite method found in the link above.  This controls a menu level.

    @author: Roy Nielsen
    """
    def __init__(self, name, action=False):
        """
        Initialization method.

        @author: Roy Nielsen
        """
        MenuComponent.__init__(self, name, action)
        try:
            self.isSaneName(name)
        except NotASaneNameError, err:
            self.logger.log(lp.DEBUG, str(err))
            self.logger.log(lp.DEBUG, "name or action: " + str(name) + " is not valid.")
        else:
            self.name = name

        try:
            self.isSaneAction(action)
        except NotASaneActionError, err:
            self.logger.log(lp.DEBUG, str(err))
            self.logger.log(lp.DEBUG, "name or action: " + str(action) + " is not valid.")
        else:
            self.action = action
            
        self.child_nodes = []

        self.printName()

    def goToMainMenu(self):
        """
        Go back to the main menu
        
        @author: rsn
        """
        while not self.anchor:
            self = self.previous
        self.menuAction()

    def menuAction(self, *args, **kwargs) :
        """
        Create the menu - execute the exec string first if it's not empty.

        Print each MenuItem of this MenuComposite in order,

        @author: Roy Nielsen
        """
        success = False

        #####
        # If the action parameter
        if self.action:
            success = self.action()

        self.logger.log(lp.DEBUG, "Action returns success: " + str(success))

        #####
        # Print the menu and act on the menu selection
        while True :
            try:
                quit = self.getValue("quit")
            except KeyError:
                quit = False

            #####
            # Write out the ANSI code to clear the screen - might not work
            # if a user's terminal is set to unicode
            print "\033c"
            sys.stdout.write("\033c")
            #####
            # Start menu logic
            print "\n" + self.name + " Menu\n"
            i = 1
            for item in self.child_nodes :
                print "[" + str(i) + "] " + self.child_nodes[(i-1)].name
                i = i + 1
            if not self.anchor :
                if not self.anchor:
                    print "[" + str(i) + "] Return to " + \
                          self.previous.name + \
                          " Menu"
                if self.anchor:
                    print "[" + str(i+1) + "] Quit"
                elif self.previous.anchor:
                    print "[" + str(i+1) + "] Quit"
                elif not self.anchor and not self.previous.anchor:
                    print "[" + str(i+1) + "] Main menu"
                    print "[" + str(i+2) + "] Quit"
            else :
                print "[" + str(i) + "] Quit"

            print "\nSelect an option and hit Enter"

            # get input from the command line
            enter = sys.stdin.readline()

            # Figure out which number (or [Q|q] they hit
            if re.match("^\d+$", enter) :
                enter = int(enter)
            elif re.match("^[Qq]$", enter) and not quit:
                break
            elif re.match("^[Qq]$", enter) and quit:
                try :
                    sys.exit()
                except OSError, err :
                    self.logger.log(lp.DEBUG, "OSError on attempt to exit: " + \
                                    str(err))
            elif re.match("^[Mm]$", enter):
                self.goToMainMenu()
            else :
                continue
            
            if enter == (len(self.child_nodes)+1) and self.anchor and not quit:
                while not self.anchor:
                    self = self.previous
                break
            if enter == (len(self.child_nodes)+1) and self.anchor and quit:
                try :
                    sys.exit()
                except OSError, err :
                    self.logger.log(lp.DEBUG, "OSError on attempt to exit: " + \
                                    str(err))
            # go back to the previous menu    
            if enter == (len(self.child_nodes)+1) and self.previous.anchor :
                while not self.anchor:
                    self = self.previous
                break
            if enter == (len(self.child_nodes)+1) and not self.anchor and not self.previous.anchor :
                break

            # Either quit, or execute the "execute" method of the MenuItem, or
            # MenuComposite
            if enter == (len(self.child_nodes)+ 1) and self.anchor and not quit:
                while not self.anchor:
                    self = self.previous
                break
            if enter == (len(self.child_nodes)+ 1) and self.anchor and quit:
                try :
                    sys.exit()
                except OSError, err :
                    self.logger.log(lp.DEBUG, "OSError on attempt to exit: " + str(err))
            elif enter == (len(self.child_nodes)+ 2) and self.previous.anchor and not quit:
                while not self.anchor:
                    self = self.previous
                break
            elif enter == (len(self.child_nodes)+ 2) and self.previous.anchor and quit:
                try :
                    sys.exit()
                except OSError, err :
                    self.logger.log(lp.DEBUG, "OSError on attempt to exit: " + str(err))
            elif enter == (len(self.child_nodes)+ 2) and not self.previous.anchor:
                self.goToMainMenu()
            elif enter == (len(self.child_nodes)+ 3) and not self.previous.anchor:
                while not self.anchor:
                    self = self.previous
                break
            elif enter == (len(self.child_nodes)+ 3) and not self.previous.anchor:
                try :
                    sys.exit()
                except OSError, err :
                    self.logger.log(lp.DEBUG, "OSError on attempt to exit: " + str(err))
                                    
            elif enter >= 0 and enter <= len(self.child_nodes) :
                #####
                # If the action parameter
                if self.action:
                    print "Action: " + str(self.action)
                    success = self.action(self, *args, **kwargs)

                self.logger.log(lp.DEBUG, "Action returns success: " + str(success))

                self.child_nodes[(enter-1)].menuAction()
            else :
                continue


    def appendChild(self, child) :
        """
        Append child to self's child nodes - IE: Add a MenuItem or MenuComposite
        to the current MenuComposite
        
        For this "menu" system, no "remove" method necessary
        
        Author: Roy Nielsen
        """
        self.child_nodes.append(child)
        child.previous = self
        child.current = child


    def setAnchor(self) :
        """
        Set this MenuComposite as the "anchor" or "head" of the tree
        
        Author: Roy Nielsen
        """
        self.anchor = True


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

    print "---------------------------------------"
    print "======================================="
    print "### Ready To Work...                ###"
    print "======================================="
    print "---------------------------------------"


