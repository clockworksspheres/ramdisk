#!/usr/bin/env python3
"""
Trigger (run) a Jenkins job or Pipeline from the command line.

Requires: pip install python-jenkins
"""

import argparse
import sys
import time
import urllib.parse
import jenkins
from jenkins import JenkinsException


