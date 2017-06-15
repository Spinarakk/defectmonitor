"""Main Window

Primary module used to initiate the main GUI window and all its associated dialog/widgets
"""

# Import built-ins
import os
import re
import time
import sys
import json
import math
import shutil
from datetime import datetime
from threading import Thread
from Queue import Queue

# Import external modules
import cv2
import numpy as np
import serial

from PyQt4 import QtGui
from PyQt4.QtCore import QThread, SIGNAL, Qt

# Import related modules

# Compile and import PyQt GUIs
os.system('build_gui.bat')
from gui import mainWindow, dialogNewBuild


class MainWindow(QtGui.QMainWindow, mainWindow.Ui_mainWindow):
    """Main Window:
    Assigns the following methods to the interactable elements of the UI.
    Emcompasses the main window when you open the application.
    """

    def __init__(self):

        # Setup Main Window UI
        QtGui.QMainWindow.__init__(self)
        # super(self.__class__, self).__init__()
        self.setupUi(self)

        # Set whether this is a simulation or using real camera
        self.simulation = True

        # Initial UI button configuration
        self.buttonInitialize.setEnabled(False)
        self.checkToggleOverlay.setEnabled(False)
        self.groupDisplayOptions.setEnabled(False)

        # Setup event listeners for all the UI components, and connect them to specific functions
        self.actionNewBuild.triggered.connect(self.new_build)
        self.actionOpenBuild.triggered.connect(self.open_build)
        self.actionAdjustCrop.triggered.connect(self.crop_adjustment)
        self.actionAdjustRotation.triggered.connect(self.rotation_adjustment)
        self.buttonInitialize.clicked.connect(self.initialize_images)
        self.buttonPhase.clicked.connect(self.set_phase)
        self.buttonStart.clicked.connect(self.thread_cascade)
        self.actionExit.triggered.connect(self.closeEvent)

        # Load configuration settings from respective .json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Store config settings as respective variables
        self.root_directory = self.config['RootDirectory']
        self.build_name = self.config['BuildName']
        self.platform_dimensions = self.config['PlatformDimension']
        self.boundary_offset = self.config['BoundaryOffset']

        # Initialize multithreading queues
        self.queue_1 = Queue()
        self.queue_2 = Queue()

        # Generate a timestamp for folder label purposes
        current_time = datetime.now()
        self.folder_name = '%s-%s-%s [%s-%s]' % (
            current_time.year, str(current_time.month).zfill(2), str(current_time.day).zfill(2),
            str(current_time.hour).zfill(2), str(current_time.minute).zfill(2)
        )

        # Create new directories to store camera images and processing outputs
        try:
            os.mkdir('%s/%s' % (self.root_directory, self.folder_name))
        except WindowsError:
            self.folder_name = self.folder_name + "_2"
            os.mkdir('%s/%s' % (self.root_directory, self.folder_name))

        os.mkdir('%s/%s/scan' % (self.root_directory, self.folder_name))
        os.mkdir('%s/%s/coat' % (self.root_directory, self.folder_name))
        self.storage_folder = {'scan': '%s/%s/scan' % (self.root_directory, self.folder_name),
                               'coat': '%s/%s/coat' % (self.root_directory, self.folder_name)}

        # Setup input .cls directory
        self.cls_folder = '%s/cls' % self.root_directory

    def new_build(self):

        new_build_dialog = NewBuild()
        success = new_build_dialog.exec_()

        if success:
            with open('config.json') as config:
                self.config = json.load(config)

            self.build_name = self.config['BuildName']
            self.platform_dimensions = self.config['PlatformDimension']
            self.buttonInitialize.setEnabled(True)
            self.update_status('New build created. Click INITIALIZE to image process the images.')

            print 'Build Name = ' + str(self.build_name)

    def open_build(self):
        pass

    def crop_adjustment(self):
        pass

    def rotation_adjustment(self):
        pass

    def initialize_images(self):
        pass

    def set_phase(self):
        pass

    def thread_cascade(self):
        pass

    def update_status(self, string):
        """Updates the status bar at the bottom of the Main Window with the sent string argument"""
        self.statusBar.showMessage(string)
        return

    def closeEvent(self, event):

        with open('config.json', 'w+') as config:
            self.config['BuildName'] = ""
            json.dump(self.config, config)

        # Deleting the created folders (for simulation purposes)
        if self.simulation:
            shutil.rmtree('%s/%s' % (self.root_directory, self.folder_name))


class NewBuild(QtGui.QDialog, dialogNewBuild.Ui_dialogNewBuild):
    """Dialog Window:
    When File > New Build... is clicked.
    """

    def __init__(self):

        QtGui.QDialog.__init__(self)
        # super(NewBuild, self).__init__(parent)

        self.setupUi(self)
        with open('config.json') as config:
            self.config = json.load(config)

    def accept(self):
        self.config['BuildName'] = str(self.lineBuildName.text())

        if self.comboPlatform.currentIndex() == 0:
            self.config['PlatformDimension'] = [636.0, 406.0]
        elif self.comboPlatform.currentIndex() == 1:
            self.config['PlatformDimension'] = [800.0, 400.0]
        elif self.comboPlatform.currentIndex() == 2:
            self.config['PlatformDimension'] = [250.0, 250.0]

        with open('config.json', 'w+') as config:
            json.dump(self.config, config)

        self.done(1)


if __name__ == '__main__':
    def main():
        application = QtGui.QApplication(sys.argv)
        interface = MainWindow()
        interface.show()
        sys.exit(application.exec_())


    main()
