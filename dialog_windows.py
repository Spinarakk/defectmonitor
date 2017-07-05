"""
dialog_window.py
Secondary module used to initiate any sub-windows that open when you click on the appropriate buttons on the main window
"""

# Import built-ins
import os
#import sys
import json

# Import external modules
import cv2
#import numpy as np
import pypylon
from PyQt4 import QtGui
from PyQt4.QtCore import SIGNAL, Qt

# Import related modules
import slice_converter
import image_capture
import camera_calibration
#import image_processing
import extra_functions

# Import PyQt GUIs
from gui import dialogNewBuild, dialogCameraCalibration, dialogSliceConverter, dialogImageCapture, dialogCameraSettings


class NewBuild(QtGui.QDialog, dialogNewBuild.Ui_dialogNewBuild):
    """
    Opens a Dialog Window:
    When File > New Build... is clicked.
    """

    def __init__(self, parent=None):

        # Setup the dialog window
        super(NewBuild, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
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


class ImageCapture(QtGui.QDialog, dialogImageCapture.Ui_dialogImageCapture):
    """
    Opens a Dialog Window:
    When Image Capture button is pressed
    """

    def __init__(self, parent=None):

        # Setup the dialog window
        super(ImageCapture, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        self.buttonBrowse.clicked.connect(self.browse)
        self.buttonCameraSettings.clicked.connect(self.camera_settings)
        self.buttonCheckCamera.clicked.connect(self.check_camera)
        self.buttonCheckTrigger.clicked.connect(self.check_trigger)
        self.buttonCapture.clicked.connect(self.capture)
        self.buttonRun.clicked.connect(self.run)
        self.buttonStop.clicked.connect(self.stop)
        self.checkApplyCorrection.toggled.connect(self.apply_correction)

        # These are flags to check if both the browse and check camera settings are successful
        self.browse_flag = False
        self.camera_flag = False
        self.trigger_flag = False
        self.save_folder = None

        self.counter = 0

    def browse(self):

        # Opens a folder select dialog, allowing the user to choose a folder
        self.save_folder = QtGui.QFileDialog.getExistingDirectory(self, 'Browse...')

        # Checks if a folder is actually selected
        if self.save_folder:
            # Display the folder name
            self.textSaveLocation.setText(self.save_folder)
            self.browse_flag = True
            if self.browse_flag & bool(self.camera_flag):
                self.buttonCapture.setEnabled(True)
            if self.browse_flag & bool(self.camera_flag) & bool(self.trigger_flag):
                self.buttonRun.setEnabled(True)

    def camera_settings(self):
        """Opens the Camera Settings dialog box
        If the OK button is clicked (success), it does the same thing as apply but also closes the box
        If the Apply button is clicked, it saves the settings to a text file
        """

        camera_settings_dialog = CameraSettings()
        camera_settings_dialog.exec_()

    def check_camera(self):
        """Checks that a camera is found and available"""

        self.camera_flag = image_capture.ImageCapture(self.save_folder).acquire_camera()

        if bool(self.camera_flag):
            self.labelCameraStatus.setText('FOUND')
            self.camera_flag = str(self.camera_flag).replace('DeviceInfo ', '')
            self.update_status(str(self.camera_flag))
            if self.browse_flag & bool(self.camera_flag):
                self.buttonCapture.setEnabled(True)
            if self.browse_flag & bool(self.camera_flag) & bool(self.trigger_flag):
                self.buttonRun.setEnabled(True)
        else:
            self.labelCameraStatus.setText('NOT FOUND')

    def check_trigger(self):
        """Checks that a triggering device is found and available"""
        self.trigger_flag = image_capture.ImageCapture(None).acquire_trigger()

        if bool(self.trigger_flag):
            self.labelTriggerStatus.setText(str(self.trigger_flag))
            if self.browse_flag & bool(self.camera_flag) & bool(self.trigger_flag):
                self.buttonRun.setEnabled(True)
        else:
            self.labelTriggerStatus.setText('NOT FOUND')

    def capture(self):
        # Instantiate and run an ImageCapture instance that will only take one image
        self.image_capture_instance_single = image_capture.ImageCapture(self.save_folder, True)
        self.connect(self.image_capture_instance_single, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.image_capture_instance_single, SIGNAL("update_progress(QString)"), self.update_progress)
        self.image_capture_instance_single.start()

    def run(self):

        # Disable buttons to prevent overlapping actions
        self.buttonBrowse.setEnabled(False)
        self.buttonCameraSettings.setEnabled(False)
        self.buttonCapture.setEnabled(False)
        self.buttonRun.setEnabled(False)
        self.buttonCheckCamera.setEnabled(False)
        self.buttonDone.setEnabled(False)
        self.buttonStop.setEnabled(True)

        # Instantiate and run a new Stopwatch instance to have a running timer
        self.stopwatch_instance = extra_functions.Stopwatch()
        self.connect(self.stopwatch_instance, SIGNAL("update_stopwatch(QString)"), self.update_stopwatch)
        self.stopwatch_instance.start()

        # Instantiate and run an ImageCapture instance that will run indefinitely until the stop button is pressed
        self.image_capture_instance = image_capture.ImageCapture(self.save_folder)
        self.connect(self.image_capture_instance, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.image_capture_instance, SIGNAL("update_progress(QString)"), self.update_progress)
        self.image_capture_instance.start()

    def update_stopwatch(self, time):
        self.labelTimeElapsed.setText('Time Elapsed: %s' % time)

    def apply_correction(self):
        pass

    def stop(self):
        """Terminates running QThreads, most notably the Stopwatch and ImageCapture instances
        Also enables or re-enables buttons
        """

        self.stopwatch_instance.terminate()
        self.image_capture_instance.terminate()

        # Re-enable buttons
        self.buttonBrowse.setEnabled(True)
        self.buttonCameraSettings.setEnabled(True)
        self.buttonCapture.setEnabled(True)
        self.buttonRun.setEnabled(True)
        self.buttonCheckCamera.setEnabled(True)
        self.buttonDone.setEnabled(True)
        self.buttonStop.setEnabled(False)

    def update_status(self, string):
        self.labelStatusBar.setText('Status: ' + string)
        return

    def update_progress(self, percentage):
        self.progressBar.setValue(int(percentage))
        return

class CameraSettings(QtGui.QDialog, dialogCameraSettings.Ui_dialogCameraSettings):
    """
    Opens a Dialog Window:
    When Camera Settings button is pressed within the Image Capture dialog window
    Or when Camera Settings action is pressed within the Setup menu bar
    """

    def __init__(self, parent=None):

        # Setup the dialog window
        super(CameraSettings, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        self.buttonApply.clicked.connect(self.apply)

        # Setup event listeners for all the setting boxes to detect a change
        self.comboPixelFormat.currentIndexChanged.connect(self.apply_enable)
        self.comboTriggerSelector.currentIndexChanged.connect(self.apply_enable)
        self.comboTriggerMode.currentIndexChanged.connect(self.apply_enable)
        self.comboTriggerSource.currentIndexChanged.connect(self.apply_enable)
        self.comboTriggerActivation.currentIndexChanged.connect(self.apply_enable)
        self.spinExposureTime.valueChanged.connect(self.apply_enable)
        self.spinAcquisitionFC.valueChanged.connect(self.apply_enable)

        # Load the camera settings which are saved to the config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Set the combo box and settings to the previously saved values
        # Combo box settings are saved as their index values in the config.json file
        self.comboPixelFormat.setCurrentIndex(int(self.config['PixelFormat']))
        self.comboTriggerSelector.setCurrentIndex(int(self.config['TriggerSelector']))
        self.comboTriggerMode.setCurrentIndex(int(self.config['TriggerMode']))
        self.comboTriggerSource.setCurrentIndex(int(self.config['TriggerSource']))
        self.comboTriggerActivation.setCurrentIndex(int(self.config['TriggerActivation']))
        self.spinExposureTime.setValue(int(self.config['ExposureTimeAbs']))
        self.spinAcquisitionFC.setValue(int(self.config['AcquisitionFrameCount']))

        self.buttonApply.setEnabled(False)

    def apply_enable(self):
        self.buttonApply.setEnabled(True)

    def apply(self):
        # Save the new index values from the changed settings to the config dictionary
        self.config['PixelFormat'] = self.comboPixelFormat.currentIndex()
        self.config['TriggerSelector'] = self.comboTriggerSelector.currentIndex()
        self.config['TriggerMode'] = self.comboTriggerMode.currentIndex()
        self.config['TriggerSource'] = self.comboTriggerSource.currentIndex()
        self.config['TriggerActivation'] = self.comboTriggerActivation.currentIndex()
        self.config['ExposureTimeAbs'] = self.spinExposureTime.value()
        self.config['AcquisitionFrameCount'] = self.spinAcquisitionFC.value()

        # Save the settings to the config.json file
        with open('config.json', 'w+') as config:
            json.dump(self.config, config)

        # Disable the Apply button until another setting is changed
        self.buttonApply.setEnabled(False)

    def accept(self):
        """When the OK button is pressed, if the settings have changed (Apply button is enabled):
        Does the apply function before closing the window"""

        if self.buttonApply.isEnabled():
            self.apply()

        self.done(1)

class SliceConverter(QtGui.QDialog, dialogSliceConverter.Ui_dialogSliceConverter):
    """
    Opens a Dialog Window:
    When Slice Converter button is pressed
    """

    def __init__(self, parent=None):

        # Setup the dialog window
        super(SliceConverter, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        self.buttonBrowse.clicked.connect(self.browse)
        self.buttonStartConversion.clicked.connect(self.conversion_start)

    def browse(self):
        self.slice_file = None
        self.slice_file = QtGui.QFileDialog.getOpenFileName(self, 'Browse...', '', 'Slice Files (*.cls *.cli)')

        if self.slice_file:
            self.textFileName.setText(self.slice_file)
            self.buttonStartConversion.setEnabled(True)
            self.update_status('Waiting to start process.')
        else:
            self.buttonStartConversion.setEnabled(False)

    def conversion_start(self):
        # Disable all buttons to prevent user from doing other tasks
        self.buttonStartConversion.setEnabled(False)
        self.buttonBrowse.setEnabled(False)

        self.slice_converter_instance = slice_converter.SliceConverter(self.slice_file)
        self.connect(self.slice_converter_instance, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.slice_converter_instance, SIGNAL("update_progress(QString)"), self.update_progress)
        self.connect(self.slice_converter_instance, SIGNAL("successful()"), self.conversion_done)
        self.slice_converter_instance.start()

    def conversion_done(self):
        self.buttonStartConversion.setEnabled(True)
        self.buttonBrowse.setEnabled(True)

    def update_status(self, string):
        self.labelProgress.setText(string)
        return

    def update_progress(self, percentage):
        self.progressBar.setValue(int(percentage))
        return

    def accept(self):
        """If you press the 'done' button, this just closes the dialog window without doing anything"""
        self.done(1)


class CameraCalibration(QtGui.QDialog, dialogCameraCalibration.Ui_dialogCameraCalibration):
    """
    Opens a Dialog Window:
    When Calibrate Camera button is pressed
    """

    def __init__(self, parent=None):

        # Setup the dialog window
        super(CameraCalibration, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        self.buttonBrowse.clicked.connect(self.browse)
        self.buttonStartCalibration.clicked.connect(self.calibration_start)

    def browse(self):

        # Empty the image lists
        self.image_list_valid = []

        # Opens a folder select dialog, allowing the user to choose a folder
        self.calibration_folder = None
        self.calibration_folder = QtGui.QFileDialog.getExistingDirectory(self, 'Browse...')

        # Checks if a folder is actually selected
        if self.calibration_folder:
            # Store a list of the files found in the folder
            self.image_list = os.listdir(self.calibration_folder)
            self.listImages.clear()

            # Search for images containing the word calibration_image in the folder
            for image_name in self.image_list:
                if 'calibration_image' in str(image_name):
                    self.image_list_valid.append(str(image_name))

            if not self.image_list_valid:
                self.update_status('No valid calibration images found.')
                self.buttonStartCalibration.setEnabled(False)
            else:
                # Remove previous entries and fill with new entries
                self.listImages.addItems(self.image_list_valid)
                self.textFolderName.setText(self.calibration_folder)
                self.buttonStartCalibration.setEnabled(True)
                self.update_status('Waiting to start process.')

    def calibration_start(self):

        # Disable all buttons to prevent user from doing other tasks
        self.buttonStartCalibration.setEnabled(False)
        self.buttonBrowse.setEnabled(False)

        self.camera_calibration_instance = camera_calibration.Calibration(self.calibration_folder)
        self.connect(self.camera_calibration_instance, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.camera_calibration_instance, SIGNAL("update_progress(QString)"), self.update_progress)
        self.connect(self.camera_calibration_instance, SIGNAL("successful()"), self.calibration_done)
        self.camera_calibration_instance.start()

    def calibration_done(self):
        """Used to turn buttons back on after processes are done"""
        self.buttonStartCalibration.setEnabled(True)
        self.buttonBrowse.setEnabled(True)

    def update_status(self, string):
        self.labelProgress.setText(string)
        return

    def update_progress(self, percentage):
        self.progressBar.setValue(int(percentage))
        return

    def accept(self):
        """If you press the 'done' button, this just closes the dialog window without doing anything"""
        self.done(1)