"""
extra_functions.py
Extraneous module that contains functions that supply features that are otherwise unnecessary for the proper operation
of the main program
Nevertheless they still add quality of life features to the main program
"""

import os
import time
from PyQt4.QtCore import QThread, SIGNAL


class Stopwatch(QThread):
    """
    A regular stopwatch module, working as a stopwatch would
    """

    def __init__(self):

        # Defines the class as a thread
        QThread.__init__(self)

        # Resets the stopwatch
        self.counter = 0
        self.seconds = 0
        self.minutes = 0
        self.hours = 0

        # Flag to start and terminate the while loop
        self.run_flag = True

    def run(self):
        while self.run_flag:
            # Send a formatted time string to the main function
            self.time = '%s:%s:%s' % (str(self.hours).zfill(2), str(self.minutes).zfill(2), str(self.seconds).zfill(2))
            self.emit(SIGNAL("update_stopwatch(QString)"), str(self.time))
            time.sleep(1)

            # Convert the counter into hours seconds and minutes
            self.counter += 1
            self.seconds = self.counter % 60
            self.minutes = int(self.counter / 60)
            self.hours = int(self.counter / 3600)

    def stop(self):
        self.run_flag = False
