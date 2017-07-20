# Import external libraries
import os
import json
from PyQt4 import QtGui
from PyQt4.QtCore import SIGNAL, Qt

# Import related modules
import slice_converter
import image_capture
import extra_functions
import camera_calibration

# Import PyQt GUIs
from gui import dialogNewBuild, dialogCameraCalibration, dialogSliceConverter, dialogImageCapture, dialogCameraSettings


class NewBuild(QtGui.QDialog, dialogNewBuild.Ui_dialogNewBuild):
    """Opens a Dialog Window when File > New Build... is clicked
    Allows user to setup a new build and change settings
    Setup as a Modal window, blocking input to other visible windows until this window is closed
    """

    def __init__(self, parent=None):

        # Setup Dialog UI with MainWindow as parent
        super(NewBuild, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        # Load configuration settings from config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        self.working_directory = self.config['WorkingDirectory']

        # Setup event listeners for all the relevent UI components, and connect them to specific functions
        # Buttons
        self.buttonBrowseCF.clicked.connect(self.browse_calibration)
        self.buttonBrowseSF.clicked.connect(self.browse_slice)
        self.buttonChangeWD.clicked.connect(self.change_working_directory)

        # Set and display the default calibration file and slice file as stated in the config.json file
        self.lineCalibrationFile.setText(self.config['CalibrationFile'])
        self.lineSliceFile.setText(self.config['SliceFile'])
        self.lineWorkingDirectory.setText(self.working_directory)

    def browse_calibration(self):

        # Opens a file select dialog, allowing user to select a calibration file
        self.calibration_file = QtGui.QFileDialog.getOpenFileName(self, 'Browse...', '', 'Calibration Files (*.txt)')

        if self.calibration_file:
            self.calibration_file = self.calibration_file.replace(self.working_directory + '/', '')
            self.lineCalibrationFile.setText(self.calibration_file)
            self.config['CalibrationFile'] = str(self.calibration_file)

    def browse_slice(self):

        # Opens a file select dialog, allowing user to select a slice file
        self.slice_file = QtGui.QFileDialog.getOpenFileName(self, 'Browse...', '', 'Slice Files (*.cls *.cli)')

        if self.slice_file:
            self.slice_file = self.slice_file.replace(self.working_directory + '/', '')
            self.lineSliceFile.setText(self.slice_file)
            self.config['SliceFile'] = str(self.slice_file)

    def change_working_directory(self):
        pass

    def accept(self):
        """Executes when the OK button is clicked
        Saves important selection options to the config.json file and closes the window
        """
        self.config['BuildName'] = str(self.lineBuildName.text())

        if self.comboPlatform.currentIndex() == 0:
            self.config['PlatformDimension'] = [636.0, 406.0]
        elif self.comboPlatform.currentIndex() == 1:
            self.config['PlatformDimension'] = [800.0, 400.0]
        elif self.comboPlatform.currentIndex() == 2:
            self.config['PlatformDimension'] = [250.0, 250.0]

        # Save configuration settings to config.json file
        with open('config.json', 'w+') as config:
            json.dump(self.config, config)

        self.done(1)


class ImageCapture(QtGui.QDialog, dialogImageCapture.Ui_dialogImageCapture):
    """Opens a Dialog Window when Image Capture button is clicked
    Allows user to capture images using a connected camera
    Setup as a Modeless window, operating independently of other windows
    """

    def __init__(self, parent=None, image_folder=None):

        # Setup Dialog UI with MainWindow as parent
        super(ImageCapture, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        # Set and display the default image folder name to be used to store all acquired images
        self.image_folder = image_folder
        self.lineImageFolder.setText(self.image_folder)

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        # Buttons
        self.buttonBrowse.clicked.connect(self.browse)
        self.buttonCameraSettings.clicked.connect(self.camera_settings)
        self.buttonCheckCamera.clicked.connect(self.check_camera)
        self.buttonCheckTrigger.clicked.connect(self.check_trigger)
        self.buttonCapture.clicked.connect(self.capture)
        self.buttonRun.clicked.connect(self.run)
        self.buttonStop.clicked.connect(self.stop)

        # These are flags to check if both the browse and check camera settings are successful
        self.camera_flag = False
        self.trigger_flag = False

    def browse(self):

        # Opens a folder select dialog, allowing the user to choose a folder
        self.image_folder = QtGui.QFileDialog.getExistingDirectory(self, 'Browse...')

        # Checks if a folder is actually selected
        if self.image_folder:
            # Display the folder name
            self.lineImageFolder.setText(self.image_folder)
            if bool(self.camera_flag):
                self.buttonCapture.setEnabled(True)
            if bool(self.camera_flag) & bool(self.trigger_flag):
                self.buttonRun.setEnabled(True)

    def camera_settings(self):
        """Opens the Camera Settings dialog box
        If the OK button is clicked (success), it does the same thing as apply but also closes the box
        If the Apply button is clicked, it saves the settings to a text file
        """

        camera_settings_dialog = CameraSettings(self)
        camera_settings_dialog.show()

    def check_camera(self):
        """Checks that a camera is found and available"""

        self.camera_flag = image_capture.ImageCapture(self.image_folder).acquire_camera()

        if bool(self.camera_flag):
            self.labelCameraStatus.setText('FOUND')
            self.camera_flag = str(self.camera_flag).replace('DeviceInfo ', '')
            self.update_status(str(self.camera_flag))
            if bool(self.camera_flag):
                self.buttonCapture.setEnabled(True)
            if bool(self.camera_flag) & bool(self.trigger_flag):
                self.buttonRun.setEnabled(True)
        else:
            self.labelCameraStatus.setText('NOT FOUND')

    def check_trigger(self):
        """Checks that a triggering device is found and available"""
        self.trigger_flag = image_capture.ImageCapture(None).acquire_trigger()

        if bool(self.trigger_flag):
            self.labelTriggerStatus.setText(str(self.trigger_flag))
            self.update_status('Trigger detected on %s' % str(self.trigger_flag) + '.')
            if bool(self.camera_flag) & bool(self.trigger_flag):
                self.buttonRun.setEnabled(True)
        else:
            self.labelTriggerStatus.setText('NOT FOUND')

    def capture(self):
        """Captures and saves a single image to the save location"""

        # Enable or disable relevant UI elements to prevent concurrent processes
        self.buttonBrowse.setEnabled(False)
        self.buttonCameraSettings.setEnabled(False)
        self.buttonCapture.setEnabled(False)
        self.buttonCheckCamera.setEnabled(False)
        self.buttonCheckTrigger.setEnabled(False)
        self.buttonDone.setEnabled(False)

        # Instantiate and run an ImageCapture instance that will only take one image
        self.ICS_instance = image_capture.ImageCapture(self.image_folder, single_flag=True,
                                                       correction_flag=self.checkApplyCorrection.isChecked())
        self.connect(self.ICS_instance, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.ICS_instance, SIGNAL("display_image(QString)"), self.display_image)
        self.connect(self.ICS_instance, SIGNAL("finished()"), self.capture_finished)
        self.ICS_instance.start()

    def capture_finished(self):
        """Executes when the ImageCapture instance has finished"""

        # Enable or disable relevant UI elements to prevent concurrent processes
        self.buttonBrowse.setEnabled(True)
        self.buttonCameraSettings.setEnabled(True)
        self.buttonCapture.setEnabled(True)
        self.buttonCheckCamera.setEnabled(True)
        self.buttonCheckTrigger.setEnabled(True)
        self.buttonDone.setEnabled(True)

    def run(self):
        """Wait indefinitely until trigger device sends a signal
        An image is captured and saved to the save location, and goes back to waiting after a pre-determined timeout
        """

        ## Enable or disable relevant UI elements to prevent concurrent processes
        self.buttonBrowse.setEnabled(False)
        self.buttonCameraSettings.setEnabled(False)
        self.buttonCapture.setEnabled(False)
        self.buttonRun.setEnabled(False)
        self.buttonCheckCamera.setEnabled(False)
        self.buttonCheckTrigger.setEnabled(False)
        self.buttonDone.setEnabled(False)
        self.buttonStop.setEnabled(True)

        # Instantiate and run a new Stopwatch instance to have a running timer
        self.stopwatch_instance = extra_functions.Stopwatch()
        self.connect(self.stopwatch_instance, SIGNAL("update_stopwatch(QString)"), self.update_stopwatch)
        self.stopwatch_instance.start()

        # Instantiate and run an ImageCapture instance that will run indefinitely until the stop button is pressed
        self.ICR_instance = image_capture.ImageCapture(self.image_folder, run_flag=True,
                                                       correction_flag=self.checkApplyCorrection.isChecked())
        self.connect(self.ICR_instance, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.ICR_instance, SIGNAL("display_image(QString)"), self.display_image)
        self.connect(self.ICR_instance, SIGNAL("finished()"), self.run_finished)
        self.ICR_instance.start()

    def run_finished(self):
        """Executes when the ImageCapture Run instance has finished"""

        # Enable or disable relevant UI elements to prevent concurrent processes
        self.buttonBrowse.setEnabled(True)
        self.buttonCameraSettings.setEnabled(True)
        self.buttonCapture.setEnabled(True)
        self.buttonRun.setEnabled(True)
        self.buttonCheckCamera.setEnabled(True)
        self.buttonCheckTrigger.setEnabled(True)
        self.buttonDone.setEnabled(True)
        self.buttonStop.setEnabled(False)

        self.update_status('Stopped.')

    def stop(self):
        """Terminates running QThreads, most notably the Stopwatch and ImageCapture instances"""

        self.update_status('Stopped. Waiting for timeout to end.')
        self.stopwatch_instance.stop()
        self.ICR_instance.stop()

    def display_image(self, image_name):
        """Sends the image name as received from the ImageCapture back to the Main Window to be displayed
        Depends if the Display Image checkbox is checked or not
        """

        if self.checkDisplayImage.isChecked():
            self.emit(SIGNAL("update_display_iv(QString)"), image_name)

    def update_stopwatch(self, time):
        """Updates the stopwatch label at the bottom of the dialog window with the received time"""
        self.labelTimeElapsed.setText('Time Elapsed: %s' % time)

    def update_status(self, string):
        self.labelStatusBar.setText('Status: ' + string)

    def closeEvent(self, event):
        """Executes when the top-right X is clicked"""

        # Stop any running QThreads cleanly before closing the dialog window
        if self.ICR_instance.isRunning:
            self.stopwatch_instance.stop()
            self.ICR_instance.stop()


class CameraSettings(QtGui.QDialog, dialogCameraSettings.Ui_dialogCameraSettings):
    """Opens a Dialog Window when Camera Settings button is clicked within the Image Capture dialog window
    Or when Setup > Camera Settings is clicked
    Allows the user to change camera settings which will be sent to the camera before images are taken
    Setup as a Modeless window, operating independently of other windows
    """

    def __init__(self, parent=None):

        # Setup Dialog UI with MainWindow as parent
        super(CameraSettings, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        self.buttonApply.clicked.connect(self.apply)

        # Setup event listeners for all the setting boxes to detect a change
        self.comboPixelFormat.currentIndexChanged.connect(self.apply_enable)
        self.spinExposureTime.valueChanged.connect(self.apply_enable)
        self.spinPacketSize.valueChanged.connect(self.apply_enable)
        self.spinInterPacketDelay.valueChanged.connect(self.apply_enable)
        self.spinFrameDelay.valueChanged.connect(self.apply_enable)
        self.spinTriggerTimeout.valueChanged.connect(self.apply_enable)

        # Load configuration settings from config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Set the combo box and settings to the previously saved values
        # Combo box settings are saved as their index values in the config.json file
        self.comboPixelFormat.setCurrentIndex(int(self.config['PixelFormat']))
        self.spinExposureTime.setValue(int(self.config['ExposureTimeAbs']))
        self.spinPacketSize.setValue(int(self.config['PacketSize']))
        self.spinInterPacketDelay.setValue(int(self.config['InterPacketDelay']))
        self.spinFrameDelay.setValue(int(self.config['FrameTransmissionDelay']))
        self.spinTriggerTimeout.setValue(int(self.config['TriggerTimeout']))

        self.buttonApply.setEnabled(False)

    def apply_enable(self):
        """Enable the Apply button on any change of setting values"""
        self.buttonApply.setEnabled(True)

    def apply(self):
        # Save the new index values from the changed settings to the config dictionary
        self.config['PixelFormat'] = self.comboPixelFormat.currentIndex()
        self.config['ExposureTimeAbs'] = self.spinExposureTime.value()
        self.config['PacketSize'] = self.spinPacketSize.value()
        self.config['InterPacketDelay'] = self.spinInterPacketDelay.value()
        self.config['FrameTransmissionDelay'] = self.spinFrameDelay.value()
        self.config['TriggerTimeout'] = self.spinTriggerTimeout.value()

        # Save configuration settings to config.json file
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
    """Opens a Dialog Window when Slice Converter button is clicked
    Allows user to convert .cls or .cli files into OpenCV readable ASCII format
    Setup as a Modal window, blocking input to other visible windows until this window is closed
    """

    def __init__(self, parent=None):

        # Setup Dialog UI with MainWindow as parent
        super(SliceConverter, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        self.buttonBrowse.clicked.connect(self.browse)
        self.buttonStartConversion.clicked.connect(self.start_conversion)

    def browse(self):

        # Opens a file select dialog, allowing user to select a slice file
        self.slice_file = None
        self.slice_file = QtGui.QFileDialog.getOpenFileName(self, 'Browse...', '', 'Slice Files (*.cls *.cli)')

        if self.slice_file:
            self.lineSliceFile.setText(self.slice_file)
            self.buttonStartConversion.setEnabled(True)
            self.update_status('Waiting to start conversion.')

    def start_conversion(self):
        # Disable all buttons to prevent user from doing other tasks
        self.buttonStartConversion.setEnabled(False)
        self.buttonBrowse.setEnabled(False)
        self.buttonDone.setEnabled(False)
        self.update_status('Conversion in progress...')

        # Instantiate and run a SliceConverter instance
        self.SC_instance = slice_converter.SliceConverter(self.slice_file)
        self.connect(self.SC_instance, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.SC_instance, SIGNAL("update_progress(QString)"), self.update_progress)
        self.connect(self.SC_instance, SIGNAL("finished()"), self.start_conversion_finished)
        self.SC_instance.start()

    def start_conversion_finished(self):
        """Executes when the SliceConverter instance has finished"""

        self.buttonStartConversion.setEnabled(True)
        self.buttonBrowse.setEnabled(True)
        self.buttonDone.setEnabled(True)
        self.update_status('Conversion completed successfully.')

    def update_status(self, string):
        self.labelStatus.setText(string)

    def update_progress(self, percentage):
        self.progressBar.setValue(int(percentage))

    def accept(self):
        """If you press the 'done' button, this just closes the dialog window without doing anything"""
        self.done(1)


class CameraCalibration(QtGui.QDialog, dialogCameraCalibration.Ui_dialogCameraCalibration):
    """Opens a Dialog Window when Camera Calibration button is clicked
    Or when Setup > Camera Calibration is clicked
    Allows the user to select a folder of checkboard images to calculate the camera's intrinsic values
    Setup as a Modal window, blocking input to other visible windows until this window is closed
    """

    def __init__(self, parent=None):

        # Setup Dialog UI with MainWindow as parent
        super(CameraCalibration, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        self.buttonBrowse.clicked.connect(self.browse)
        self.buttonStartCalibration.clicked.connect(self.calibration_start)

        # Load configuration settings from config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Set the spinbox settings to the previously saved values
        self.spinWidth.setValue(int(self.config['CalibrationWidth']))
        self.spinHeight.setValue(int(self.config['CalibrationHeight']))
        self.spinRatio.setValue(int(self.config['DownscalingRatio']))

    def browse(self):

        # Empty the image lists
        self.image_list_valid = []

        # Opens a folder select dialog, allowing the user to choose a folder
        self.calibration_folder = None
        self.calibration_folder = QtGui.QFileDialog.getExistingDirectory(self, 'Browse...', '')

        # Checks if a folder is actually selected
        if self.calibration_folder:
            # Store a list of the files found in the folder
            self.image_list = os.listdir(self.calibration_folder)
            self.listImages.clear()

            # Update the lineEdit with the new folder name
            self.lineCalibrationFolder.setText(self.calibration_folder)

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

                self.buttonStartCalibration.setEnabled(True)
                self.update_status('Waiting to start process.')

    def calibration_start(self):
        """Executes when the Start Calibration button is clicked
        Starts the calibration process after saving the calibration settings to config.json file
        """

        # Enable or disable relevant UI elements to prevent concurrent processes
        self.buttonBrowse.setEnabled(False)
        self.buttonStartCalibration.setEnabled(False)
        self.buttonDone.setEnabled(False)

        # Save calibration settings
        self.save_settings()

        # Instantiate and run a CameraCalibration instance
        self.CC_instance = camera_calibration.Calibration(self.calibration_folder)
        self.connect(self.CC_instance, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.CC_instance, SIGNAL("update_progress(QString)"), self.update_progress)
        self.connect(self.CC_instance, SIGNAL("finished()"), self.calibration_finished)
        self.CC_instance.start()

    def calibration_finished(self):
        """Used to re-enable buttons after the calibration process is finished"""

        self.buttonBrowse.setEnabled(True)
        self.buttonStartCalibration.setEnabled(True)
        self.buttonDone.setEnabled(True)

    def save_settings(self):
        """Save the spinxbox values to config.json file"""

        # Save the new values from the changed settings to the config dictionary
        self.config['CalibrationWidth'] = self.spinWidth.value()
        self.config['CalibrationHeight'] = self.spinHeight.value()
        self.config['DownscalingRatio'] = self.spinRatio.value()

        # Save configuration settings to config.json file
        with open('config.json', 'w+') as config:
            json.dump(self.config, config)

    def update_status(self, string):
        self.labelStatus.setText(string)

    def update_progress(self, percentage):
        self.progressBar.setValue(int(percentage))

    def accept(self):
        """Executes when the Done button is clicked
         Saves the settings before closing the dialog window
        """

        self.save_settings()
        self.done(1)
