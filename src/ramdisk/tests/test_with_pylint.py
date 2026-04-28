#!/usr/bin/env -S python -u

import os
import re
import sys
import json
import traceback
import unittest
from pathlib import Path

# Add project root to sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from PylintIface import PylintIface


excludeUnlessUid0 = ["environment.py"]


# ---------------------------------------------------------------------------
# File discovery helpers
# ---------------------------------------------------------------------------

def getRecursiveTree(targetRootDir="."):
    filesList = []
    for root, dirs, files in os.walk(targetRootDir):
        for myfile in files:
            if myfile.endswith(".py"):
                if os.geteuid() != 0 and myfile in excludeUnlessUid0:
                    continue
                filesList.append(os.path.abspath(os.path.join(root, myfile)))
    return filesList


def getDirList(targetDir="."):
    filesList = []
    for myfile in os.listdir(targetDir):
        if myfile.endswith(".py"):
            if os.geteuid() != 0 and myfile in excludeUnlessUid0:
                continue
            filesList.append(os.path.abspath(os.path.join(targetDir, myfile)))
    return filesList


# ---------------------------------------------------------------------------
# Generate test data using the SAFE wrapper
# ---------------------------------------------------------------------------

def genTestData(fileList, excludeFiles, excludeFromLines):
    test_case_data = []

    if not fileList:
        return []

    for myfile in fileList:
        if myfile in excludeFiles:
            continue

        if not myfile.endswith(".py"):
            continue

        try:
            jsonData = PylintIface().processFile(myfile)

            for item in jsonData:
                try:
                    if item["category"] in ("error", "fatal"):
                        message = item["message"]
                        message = re.sub("'", "", message)
                        message = re.sub("/", "_", message)
                        message = re.sub("::", "_", message)

                        if any(re.search(pattern, message) for pattern in excludeFromLines):
                            continue

                        test_case_data.append((myfile, item["line"], message))

                except KeyError:
                    print(traceback.format_exc())

        except Exception:
            print(f"Unexpected exception while processing {myfile}")
            print(traceback.format_exc())

    return test_case_data


# ---------------------------------------------------------------------------
# Dynamic unittest generation
# ---------------------------------------------------------------------------

def pylint_test_template(myfile, lineNum, text):
    def foo(self):
        self.assertTrue(False, f"{myfile}_{lineNum}_{text}")
    return foo


class test_with_pylint(unittest.TestCase):
    pass


# ---------------------------------------------------------------------------
# CLI option parsing
# ---------------------------------------------------------------------------

from optparse import OptionParser, Option

class MultipleOptions(Option):
    ACTIONS = Option.ACTIONS + ("extend",)
    STORE_ACTIONS = Option.STORE_ACTIONS + ("extend",)
    TYPED_ACTIONS = Option.TYPED_ACTIONS + ("extend",)
    ALWAYS_TYPED_ACTIONS = Option.ALWAYS_TYPED_ACTIONS + ("extend",)

    def take_action(self, action, dest, opt, value, values, parser):
        if action == "extend":
            values.ensure_value(dest, []).extend(value.split(","))
        else:
            Option.take_action(self, action, dest, opt, value, values, parser)


parser = OptionParser(option_class=MultipleOptions)

parser.add_option("-f", "--do_files", action="extend", type="string",
                  dest="doFiles", default=[])

parser.add_option("-x", "--exclude_files", action="extend", type="string",
                  dest="excludeFiles", default=[])

parser.add_option("-l", "--exclude_lines_with", action="extend", type="string",
                  dest="excludeLinesWith", default=[])

parser.add_option("-r", "--recursive-tree", dest="treeRoot", default="")
parser.add_option("-d", "--dir-to-check", dest="dirToCheck", default="")
parser.add_option("--debug", action="store_true", dest="debug", default=False)
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False)

# If pytest imports this file, sys.argv is pytest's argv.
# We must NOT parse pytest's arguments.
if __name__ == "__main__":
    opts, args = parser.parse_args()
else:
    # Provide safe defaults for pytest
    class Dummy:
        doFiles = []
        excludeFiles = []
        excludeLinesWith = []
        treeRoot = ""
        dirToCheck = ""
        debug = False
        verbose = False
    opts = Dummy()


# ---------------------------------------------------------------------------
# Unified dynamic test runner (used by both CLI and pytest)
# ---------------------------------------------------------------------------

def run_dynamic_tests():
    test_case_data = []

    if opts.treeRoot:
        test_case_data += genTestData(
            getRecursiveTree(os.path.abspath(opts.treeRoot)),
            opts.excludeFiles,
            opts.excludeLinesWith,
        )

    if opts.dirToCheck:
        test_case_data += genTestData(
            getDirList(opts.dirToCheck),
            opts.excludeFiles,
            opts.excludeLinesWith,
        )

    if opts.doFiles:
        test_case_data += genTestData(
            opts.doFiles,
            opts.excludeFiles,
            opts.excludeLinesWith,
        )

    # Build dynamic tests
    for myfile, lineNum, text in test_case_data:
        safe_name = "_".join(myfile.replace("/", "_").split("."))
        test_name = f"test_with_pylint_{safe_name}_{lineNum}_{text}"
        setattr(test_with_pylint, test_name, pylint_test_template(myfile, lineNum, text))

    return unittest.defaultTestLoader.loadTestsFromTestCase(test_with_pylint)


# ---------------------------------------------------------------------------
# Entry point logic — CLI + pytest
# ---------------------------------------------------------------------------

RUNNING_PYTEST = "pytest" in sys.modules

if __name__ == "__main__":
    # CLI mode
    suite = run_dynamic_tests()
    runner = unittest.TextTestRunner()
    runner.run(suite)

elif RUNNING_PYTEST:
    # pytest mode — run the SAME dynamic tests as CLI
    suite = run_dynamic_tests()

else:
    # Imported normally — do nothing
    pass

