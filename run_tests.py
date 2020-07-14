#!/usr/bin/python
"""
Test harness creating a test suite, and running it.

@author: Roy Nielsen
@note Initial working model: 1/15/2015
"""
#--- Native python libraries
import os
import re
import sys
import traceback
import unittest
from optparse import OptionParser, SUPPRESS_HELP, OptionValueError, Option

testdir = "./tests"

from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp

###############################################################################

class TestResultsErrors(BaseException):
    """
    Meant for being thrown when an action/class being run/instanciated is not
    applicable for the running operating system.

    @author: Roy Nielsen
    """
    def __init__(self, *args, **kwargs):
        BaseException.__init__(self, *args, **kwargs)

###########################################################################

class BuildAndRunSuite(object):

    def __init__(self, logger):
        """
        """
        if logger:
            self.logger = logger
        else:
            self.logger = CyLogger()
        self.module_version = '20160224.032043.009191'
        self.prefix = []

    ##############################################

    def setPrefix(self, prefix=[]):
        """
        Setter for the prefix variable...
        """
        if prefix and isinstance(prefix, list):
            self.prefix = prefix
        else:
            self.prefix=["test_", "Test_"]

    ##############################################

    def get_all_tests(self, prefix=[]):
        """
        Collect all available tests using the test prefix(s)

        @author: Roy Nielsen
        """
        test_list = []
        if not self.modules:
            allfiles = os.listdir(testdir)
            for check_file in allfiles:
                test_name = str(check_file).split(".")[0]
                pycfile = os.path.join("./tests/", test_name + ".pyc")
                if os.path.exists(pycfile):
                    os.unlink(pycfile)
                for item in self.prefix:
                    if re.match("^%s.+\.py$"%item, check_file):
                        print "Loading test: " + str(check_file)
                        test_list.append(os.path.join("./tests/", check_file))
            print str(test_list)

        return test_list

    ##############################################

    def run_suite(self, modules=[]):
        """
        Gather all the tests from this module in a test suite.

        @author: Roy Nielsen
        """
        self.test_dir_name = testdir.split("/")[1]
        self.modules = modules

        #####
        # Initialize the test suite
        self.test_suite = unittest.TestSuite()

        #####
        # Generate the test list
        if self.modules and isinstance(self.modules, list):
            test_list = self.modules
        else:
            test_list = self.get_all_tests(prefix)

        #####
        # Import each of the tests and add them to the suite
        for check_file in test_list:
            self.logger.log(lp.DEBUG, str(check_file))
            test_name = str(check_file).split("/")[-1]
            test_name = str(test_name).split(".")[0]
            self.logger.log(lp.DEBUG, "test_name: " + str(test_name))
            test_name_import_path = ".".join([self.test_dir_name, test_name])
            self.logger.log(lp.DEBUG, "test_name_import_path: " +
                            str(test_name_import_path))

            try:
                ################################################
                # Test class needs to be named the same as the
                #   filename for this to work.
                # import the file named in "test_name" variable
                module_to_run = __import__(test_name_import_path, 
                                           fromlist=test_name, level=-1)
                # getattr(x, 'foobar') is equivalent to x.foobar
                test_to_run = getattr(module_to_run, test_name)
                # Add the test class to the test suite
                self.test_suite.addTest(unittest.makeSuite(test_to_run))
            except AttributeError, err:
                pass
        #####
        # calll the run_action to execute the test suite
        self.run_action()

    ##############################################

    def run_action(self):
        """
        Run the Suite.
        """
        runner = unittest.TextTestRunner()
        runner.run(self.test_suite)

###############################################################################

# Get all of the possible options passed in to OptionParser that are passed
# in with the -m or --modules flag
class ModulesOption(Option):

    ACTIONS = Option.ACTIONS + ("extend",)
    STORE_ACTIONS = Option.STORE_ACTIONS + ("extend",)
    TYPED_ACTIONS = Option.TYPED_ACTIONS + ("extend",)
    ALWAYS_TYPED_ACTIONS = Option.ALWAYS_TYPED_ACTIONS + ("extend",)

    def take_action(self, action, dest, opt, value, values, parser):
        if action == "extend":
            lvalue = value.split(",")
            values.ensure_value(dest, []).extend(lvalue)
        else:
            Option.take_action(
                self, action, dest, opt, value, values, parser)

###############################################################################

if __name__ == "__main__":
    """
    Executes if this file is run.
    """

    VERSION="0.4.0"
    description = "Generic test runner."
    parser = OptionParser(option_class=ModulesOption,
                          usage='usage: %prog [OPTIONS]',
                          version='%s' % (VERSION),
                          description=description)

    parser.add_option("-a", "--all-automatable", action="store_true", dest="all",
                      default=False, help="Run all tests except interactive tests.")

    parser.add_option("-v", "--verbose", action="store_true",
                      dest="verbose", default=False, \
                      help="Print status messages")

    parser.add_option("-d", "--debug", action="store_true", dest="debug",
                      default=False, help="Print debug messages")

    parser.add_option('-p', '--prefix', action="extend", type="string",
                      dest='prefix', default=[],
                      help="Collect tests with these prefixes")

    parser.add_option('-m', '--modules', action="extend", type="string",
                      dest='modules', default=[], help="Name of the test" +
                      " to run.  May indicate multiple tests to run," +
                      " if this switch is used multiple times, each with" +
                      " different test name")

    parser.add_option("-s", "--skip", action="store_true", 
                      dest="skip_syslog", default=False,
                      help="Skip syslog logging so we don't fill up the logs." + \
                           "This will leave an incremental log by default in " + \
                           "/tmp/<uid>.stonixtest.<log number>, where log number" +\
                           " is the order of the last ten stonixtest runs")

    if len(sys.argv) == 1:
        parser.parse_args(['--help'])

    options, __ = parser.parse_args()

    #####
    # Options processing

    #####
    # ... processing modules ...
    if options.all:
        modules = None
    elif options.modules:
        modules = options.modules
    else:
        modules = None

    #####
    # ... processing logging options...
    if options.verbose:
        level = 20
    elif options.debug:
        level = 10
    else:
        level = 30
    logger = CyLogger(level=level)
    logger.initializeLogs(filename="ramdiskTestLog")

    logger.log(lp.DEBUG, "Modules: " + str(modules))

    #####
    # ... processing test prefixes
    if options.prefix:
        prefix = options.prefix
    else:
        prefix = ["test_", "Test_"]

    if os.geteuid != 0:
        print("\n\nNote - Some tests will fail if not run with superuser privilege.")
        raw_input("Press any key to continue...\n\n")

    bars = BuildAndRunSuite(logger)
    bars.setPrefix(prefix)
    bars.run_suite(modules)
