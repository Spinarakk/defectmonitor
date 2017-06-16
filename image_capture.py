"""
image_capture.py
Module to capture images from the camera.
"""
import os
import json

import pypylon

from PyQt4 import QtGui
from PyQt4.QtCore import QThread, SIGNAL, Qt

class PreCapture(QThread):
    """Part Slice Convertor:

    Converts the .cls files into ASCII format that the rest of the program can interpret.
    """

    def __init__(self, cls_folder):
        QThread.__init__(self)
        self.cls_folder = cls_folder
        self.file_list = os.listdir(self.cls_folder)
        self.file_dictionary = dict()

class Capture():
    """Image Capture:
    """
    def __init__(self, queue1, storage_folder, simulation=False):
        QThread.__init__(self)
        self.queue1 = queue1
        self.storage_folder = storage_folder
        self.simulation = simulation

        with open('config.json') as config:
            self.config = json.load(config)

        self.start_layer = self.config['StartLayer']
        self.start_phase = self.config['StartPhase']

        push_offset = 1
        self.push_counter = 2 * self.start_layer

        if self.start_phase == 'coat':
            self.push_counter += push_offset

        self.camera1 = None
        self.new_parameters = []
        self.stop = False
        self.available_cameras = []
        self.file_list = []
        self.calibration_output = []
        self.calibration_valid = False
        self.serial_trigger = []
        self.image_raw = None

    def run(self):
        self.emit(SIGNAL("update_status(QString)"), 'Pylon %s' % pypylon.pylon_version.version)
        if self.simulation:
            self.calibration_capture()
            self.acquire_image(self.simulation)