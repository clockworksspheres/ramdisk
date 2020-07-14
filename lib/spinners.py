#!/usr/bin/env python

import itertools
import sys
import time
import threading


class Spinner(object):
    spinner_cycle = itertools.cycle(['-', '\\', '|', '/'])

    def __init__(self):
        self.stop_running = threading.Event()
        self.spin_thread = threading.Thread(target=self.init_spin)

    def start(self):
        self.spin_thread.start()

    def stop(self):
        self.stop_running.set()
        self.spin_thread.join()

    def init_spin(self):
        while not self.stop_running.is_set():
            sys.stdout.write(self.spinner_cycle.next())
            sys.stdout.flush()
            time.sleep(.33)
            sys.stdout.write('\b')

def do_work():
    time.sleep(3)

if __name__ == "__main__":
    """
    """
    print 'starting work'    

    spinner = Spinner()
    spinner.start()

    do_work()

    spinner.stop()
    print 'all done!'

