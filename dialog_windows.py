# Import external libraries
import os
import time
from datetime import datetime
import cv2
import numpy as np
import json
import gc
from PyQt4 import QtGui
from PyQt4.QtCore import SIGNAL, Qt, QSettings, QString, SLOT

# Import related modules
import slice_converter
import image_processing
import extra_functions
import camera_calibration
import defect_analysis

# Import PyQt GUIs
from gui import dialogNewBuild, dialogCameraCalibration, dialogCalibrationResults, \
    dialogSliceConverter, dialogImageCapture, dialogCameraSettings, dialogNotificationSettings, dialogOverlayAdjustment


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

        # Setup event listeners for all the relevent UI components, and connect them to specific functions
        # Buttons
        self.buttonBrowseCF.clicked.connect(self.browse_calibration)
        self.buttonBrowseSF.clicked.connect(self.browse_slice)
        self.buttonBrowseBF.clicked.connect(self.browse_build_folder)
        self.buttonSendTestEmail.clicked.connect(self.send_test)
        self.checkAll.toggled.connect(self.toggle_all)
        self.lineEmailAddress.textChanged.connect(self.enable_button)

        # Set and display the default image folder, calibration file and slice file as stated in the config.json file
        self.lineCalibrationFile.setText(QString(self.config['CalibrationFile']).section('/', -1))
        for index, item in enumerate(self.config['SliceFiles']):
            self.listSliceFiles.addItem(os.path.basename(item))
            if '.cls' in item:
                self.listSliceFiles.item(index).setBackground(QtGui.QColor('blue'))
            elif '.cli' in item:
                self.listSliceFiles.item(index).setBackground(QtGui.QColor('yellow'))
        self.lineBuildFolder.setText(self.config['BuildFolder'])
        self.lineUsername.setText(self.config['Username'])
        self.lineEmailAddress.setText(self.config['EmailAddress'])

    def browse_calibration(self):

        # Opens a file select dialog, allowing user to select a calibration file
        calibration_file = QtGui.QFileDialog.getOpenFileName(self, 'Browse...', '', 'Calibration Files (*.txt)')

        if calibration_file:
            # Save the file path to the configuration file
            self.config['CalibrationFile'] = str(calibration_file)
            # Display just the file name on the line box
            self.lineCalibrationFile.setText(os.path.basename(calibration_file))

    def browse_slice(self):
        # Opens a file select dialog, allowing user to select one or multiple slice files
        slice_list = list()
        files = QtGui.QFileDialog.getOpenFileNames(self, 'Browse...', '', 'Slice Files (*.cls *.cli)')

        # Turn the received QtFileList into a Python list of names
        for item in files:
            slice_list.append(str(item).replace('\\', '/'))

        if slice_list:
            self.config['SliceFiles'] = slice_list
            self.listSliceFiles.clear()
            for index, item in enumerate(slice_list):
                self.listSliceFiles.addItem(os.path.basename(item))
                if '.cls' in item:
                    self.listSliceFiles.item(index).setBackground(QtGui.QColor('blue'))
                elif '.cli' in item:
                    self.listSliceFiles.item(index).setBackground(QtGui.QColor('yellow'))

    def browse_build_folder(self):
        # Opens a folder select dialog, allowing the user to select a folder
        folder = QtGui.QFileDialog.getExistingDirectory(self, 'Browse...', '')

        if folder:
            # Save the folder path to the configuration file
            self.config['BuildFolder'] = folder.replace('\\', '/')
            # Display just the file name on the line box
            self.lineBuildFolder.setText(self.config['BuildFolder'])

    def send_test(self):
        """Sends a test notification email to the inputted email address"""

        # Open a message box with a send test email confirmation message so accidental emails don't get sent
        self.send_confirmation = QtGui.QMessageBox()
        self.send_confirmation.setIcon(QtGui.QMessageBox.Question)
        self.send_confirmation.setText('Are you sure you want to send a test email notification to %s?' %
                                       self.lineEmailAddress.text())
        self.send_confirmation.setWindowTitle('Send Test Email')
        self.send_confirmation.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

        confirmation = self.send_confirmation.exec_()

        # If the user clicked Yes
        if confirmation == 16384:
            valid_email = self.verify_email()

            if valid_email:
                # Disable the Send Test Email button to prevent SPAM
                self.buttonSendTestEmail.setEnabled(False)

                # Instantiate and run a Notifications instance
                self.N_instance = extra_functions.Notifications('Test Email Notification')
                self.N_instance.start()
                self.connect(self.N_instance, SIGNAL("finished()"), self.send_test_finished)

        else:
            # Do nothing
            pass

    def send_test_finished(self):
        """Open a message box with a send test confirmation message"""
        self.send_test_confirmation = QtGui.QMessageBox()
        self.send_test_confirmation.setIcon(QtGui.QMessageBox.Information)
        self.send_test_confirmation.setText('An email notification has been sent to %s at %s.' %
                                            (self.lineEmailAddress.text(), self.lineUsername.text()))
        self.send_test_confirmation.setWindowTitle('Send Test Email')
        self.send_test_confirmation.exec_()

    def toggle_all(self):
        """Toggling the All checkbox causes all the subsequent checkboxes to toggle being check"""
        self.checkMinor.setChecked(self.checkAll.isChecked())
        self.checkMajor.setChecked(self.checkAll.isChecked())
        self.checkFailure.setChecked(self.checkAll.isChecked())
        self.checkError.setChecked(self.checkAll.isChecked())

    def verify_email(self):
        """Checks if the entered email address is valid or not"""
        if '@' in self.lineEmailAddress.text():
            return True
        else:
            # Opens a message box indicating that the entered email address is invalid
            self.invalid_email_error = QtGui.QMessageBox()
            self.invalid_email_error.setIcon(QtGui.QMessageBox.Critical)
            self.invalid_email_error.setText('Invalid email address. Please enter a valid email address.')
            self.invalid_email_error.setWindowTitle('Error')
            self.invalid_email_error.exec_()
            return False

    def enable_button(self):
        """Re-enables the Send Test Email button if someone changes the email address text"""
        self.buttonSendTestEmail.setEnabled(True)

    def accept(self):
        """Executes when the OK button is clicked
        Saves important selection options to the config.json file and closes the window
        """

        self.config['BuildName'] = str(self.lineBuildName.text())
        self.config['Username'] = str(self.lineUsername.text())
        self.config['EmailAddress'] = str(self.lineEmailAddress.text())
        self.config['ConvertContours'] = str(self.checkConvert.isChecked())

        # Save the selected platform dimensions to the config.json file
        if self.comboPlatform.currentIndex() == 0:
            self.config['PlatformDimensions'] = [636.0, 406.0]
        elif self.comboPlatform.currentIndex() == 1:
            self.config['PlatformDimensions'] = [800.0, 400.0]
        elif self.comboPlatform.currentIndex() == 2:
            self.config['PlatformDimensions'] = [250.0, 250.0]

        # Generate a timestamp for folder labelling purposes
        time = datetime.now()

        # Set the full name of the main storage folder for all acquired images
        image_folder = """%s/%s-%s-%s [%s''%s'%s] %s""" % \
                            (self.config['BuildFolder'], time.year, str(time.month).zfill(2),
                             str(time.day).zfill(2), str(time.hour).zfill(2),
                             str(time.minute).zfill(2), str(time.second).zfill(2), self.config['BuildName'])

        # Save the created image folder's name to the config.json file
        self.config['ImageFolder'] = image_folder

        # Create new directories to store camera images and processing outputs
        # Includes error checking in case the folder already exist (shouldn't due to the seconds output)
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)
        else:
            os.makedirs(image_folder + '_2')

        # Create respective sub-directories for images
        os.makedirs('%s/raw/coat' % image_folder)
        os.makedirs('%s/raw/scan' % image_folder)
        os.makedirs('%s/raw/single' % image_folder)
        os.makedirs('%s/processed/coat' % image_folder)
        os.makedirs('%s/processed/scan' % image_folder)
        os.makedirs('%s/processed/single' % image_folder)
        os.makedirs('%s/defects/coat' % image_folder)
        os.makedirs('%s/defects/scan' % image_folder)
        os.makedirs('%s/defects/single' % image_folder)
        os.makedirs('%s/contours' % image_folder)

        # Save configuration settings to config.json file
        with open('config.json', 'w+') as config:
            json.dump(self.config, config, indent=4, sort_keys=True)

        # Close the dialog window
        self.done(1)


class NotificationSettings(QtGui.QDialog, dialogNotificationSettings.Ui_dialogNotificationSettings):
    """Opens a Dialog Window when Setup > Report Settings > Notification Settings is clicked
    Allows user to enter and change the email address and what notifications to be notified of
    Setup as a Modal window, blocking input to other visible windows until this window is closed
    """

    def __init__(self, parent=None):

        # Setup Dialog UI with MainWindow as parent
        super(NotificationSettings, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        # Load configuration settings from config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Set and display the default saved username and email address as stated in the config.json file
        self.lineUsername.setText(self.config['Username'])
        self.lineEmailAddress.setText(self.config['EmailAddress'])

        # Setup event listeners for all the relevent UI components, and connect them to specific functions
        self.buttonSendTestEmail.clicked.connect(self.send_test)
        self.checkAll.toggled.connect(self.toggle_all)
        self.lineEmailAddress.textChanged.connect(self.enable_button)

    def send_test(self):
        """Sends a test notification email to the inputted email address"""

        # Open a message box with a send test email confirmation message so accidental emails don't get sent
        self.send_confirmation = QtGui.QMessageBox()
        self.send_confirmation.setIcon(QtGui.QMessageBox.Question)
        self.send_confirmation.setText('Are you sure you want to send a test email notification to %s?' %
                                       self.lineEmailAddress.text())
        self.send_confirmation.setWindowTitle('Send Test Email')
        self.send_confirmation.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

        confirmation = self.send_confirmation.exec_()

        # If the user clicked Yes
        if confirmation == 16384:
            valid_email = self.verify_email()

            if valid_email:
                # Disable the Send Test Email button to prevent SPAM
                self.buttonSendTestEmail.setEnabled(False)
                
                # Instantiate and run a Notifications instance
                self.N_instance = extra_functions.Notifications('Test Email Notification')
                self.N_instance.start()
                self.connect(self.N_instance, SIGNAL("finished()"), self.send_test_finished)

        else:
            # Do nothing
            pass

    def send_test_finished(self):
        """Open a message box with a send test confirmation message"""
        self.send_test_confirmation = QtGui.QMessageBox()
        self.send_test_confirmation.setIcon(QtGui.QMessageBox.Information)
        self.send_test_confirmation.setText('An email notification has been sent to %s at %s.' %
                                            (self.lineEmailAddress.text(), self.lineUsername.text()))
        self.send_test_confirmation.setWindowTitle('Send Test Email')
        self.send_test_confirmation.exec_()

    def toggle_all(self):
        """Toggling the All checkbox causes all the subsequent checkboxes to toggle being check"""
        self.checkMinor.setChecked(self.checkAll.isChecked())
        self.checkMajor.setChecked(self.checkAll.isChecked())
        self.checkFailure.setChecked(self.checkAll.isChecked())
        self.checkError.setChecked(self.checkAll.isChecked())

    def verify_email(self):
        """Checks if the entered email address is valid or not"""
        if '@' in self.lineEmailAddress.text():
            return True
        else:
            # Opens a message box indicating that the entered email address is invalid
            self.invalid_email_error = QtGui.QMessageBox()
            self.invalid_email_error.setIcon(QtGui.QMessageBox.Critical)
            self.invalid_email_error.setText('Invalid email address. Please enter a valid email address.')
            self.invalid_email_error.setWindowTitle('Error')
            self.invalid_email_error.exec_()
            return False

    def enable_button(self):
        """Re-enables the Send Test Email button if someone changes the email address text"""
        self.buttonSendTestEmail.setEnabled(True)

    def accept(self):
        """Executes when the OK button is clicked
        Saves important input and selection options to the config.json file and closes the window
        """

        self.config['Username'] = str(self.lineUsername.text())
        self.config['EmailAddress'] = str(self.lineEmailAddress.text())

        # Save configuration settings to config.json file
        with open('config.json', 'w+') as config:
            json.dump(self.config, config, indent=4, sort_keys=True)

        # Close the dialog window
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

        # Import related module
        import image_capture
        # Set the imported module as an instance variable
        self.image_capture = image_capture

        # Set and display the default image folder name to be used to store all acquired images
        self.image_folder = image_folder
        self.lineImageFolder.setText(self.image_folder)

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        self.buttonBrowse.clicked.connect(self.browse)
        self.buttonCameraSettings.clicked.connect(self.camera_settings)
        self.buttonCheckCamera.clicked.connect(self.check_camera)
        self.buttonCheckTrigger.clicked.connect(self.check_trigger)
        self.buttonCapture.clicked.connect(self.capture)
        self.buttonRun.clicked.connect(self.run)
        self.buttonStop.clicked.connect(self.stop)

        # These are flags to check if the camera and/or trigger are detected
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
        camera_settings_dialog.activateWindow()

    def check_camera(self):
        """Checks that a camera is found and available"""

        self.camera_flag = self.image_capture.ImageCapture().acquire_camera()

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
        self.trigger_flag = self.image_capture.ImageCapture().acquire_trigger()

        if bool(self.trigger_flag):
            self.labelTriggerStatus.setText(str(self.trigger_flag))
            self.update_status('Trigger detected on %s' % str(self.trigger_flag) + '.')
            if bool(self.camera_flag) & bool(self.trigger_flag):
                self.buttonRun.setEnabled(True)
        else:
            self.labelTriggerStatus.setText('NOT FOUND')

    def capture(self):
        """Captures and saves a single image to the save location"""

        self.set_start_layer()

        # Enable or disable relevant UI elements to prevent concurrent processes
        self.buttonBrowse.setEnabled(False)
        self.buttonCameraSettings.setEnabled(False)
        self.buttonCapture.setEnabled(False)
        self.buttonCheckCamera.setEnabled(False)
        self.buttonCheckTrigger.setEnabled(False)
        self.buttonDone.setEnabled(False)

        # Instantiate and run an ImageCapture instance that will only take one image
        self.ICS_instance = self.image_capture.ImageCapture(single_flag=True)
        self.connect(self.ICS_instance, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.ICS_instance, SIGNAL("image_correction(PyQt_PyObject, QString, QString)"), self.image_correction)
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

        self.set_start_layer()

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
        self.connect(self.stopwatch_instance, SIGNAL("update_time(QString, QString)"), self.update_time)
        #self.connect(self.stopwatch_instance, SIGNAL("send_notification()"), self.send_notification)
        self.stopwatch_instance.start()

        # Instantiate and run an ImageCapture instance that will run indefinitely until the stop button is pressed
        self.ICR_instance = self.image_capture.ImageCapture(run_flag=True)
        self.connect(self.ICR_instance, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.ICR_instance, SIGNAL("image_correction(PyQt_PyObject, QString, QString)"), self.image_correction)
        self.connect(self.ICR_instance, SIGNAL("reset_time_idle()"), self.reset_time_idle)
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

    def image_correction(self, image, layer, phase):
        """Apply distortion fix, perspective fix and crop to the captured image and save it to the processed folder
        Then send it back to the MainWindow to be displayed if Display Image checkbox is checked
        """

        # Store the received arguments as instance variables
        self.layer = str(layer)
        self.phase = str(phase)

        self.update_status('Saving raw image.')

        # Save the raw image to the stated folder
        cv2.imwrite('%s/raw/%s/image_%s_%s.png' %
                    (self.image_folder, self.phase, self.phase, self.layer.zfill(4)), image)

        # Instantiate and run an ImageCorrection instance
        self.IC_instance = image_processing.ImageCorrection(image)
        self.connect(self.IC_instance, SIGNAL("finished()"), self.image_correction_finished)
        self.IC_instance.start()

    def image_correction_finished(self):
        """Executes when the ImageCorrection instance has finished
        """

        self.update_status('Image correction applied. Saving image')

        # Grab the corrected image from the instance variable
        image = self.IC_instance.image_DPC

        # Save the corrected image to the stated folder
        cv2.imwrite('%s/processed/%s/imageC_%s_%s.png' %
                    (self.image_folder, self.phase, self.phase, self.layer.zfill(4)), image)

        self.update_status('Image saved.')

        # Setting the appropriate tab index to send depending on which phase the image is
        if self.phase == 'coat': index = '0'
        elif self.phase == 'scan': index = '1'
        else: index = '4'

        time.sleep(1)

        self.emit(SIGNAL("tab_focus(QString, QString)"), index, self.layer)

        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        # Defect Analysis (To be modified)
        try:
            overlay = cv2.imread('%s/contours/image_contours_%s.png' % (self.image_folder, self.layer.zfill(4)))
        except:
            overlay = cv2.imread('%s/contours.png' % self.config['WorkingDirectory'])

        if self.phase == 'coat':
            detector = defect_analysis.DefectDetection(image, overlay, self.layer)
            detector.run()
        elif self.phase == 'scan':
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (27, 27), 0)
            edge = cv2.Laplacian(gray, cv2.CV_64F)
            for i in xrange(3):
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * i + 1, 2 * i + 1))
                edge = cv2.morphologyEx(edge, cv2.MORPH_CLOSE, kernel)
                edge = cv2.morphologyEx(edge, cv2.MORPH_OPEN, kernel)

            edge = cv2.morphologyEx(edge, cv2.MORPH_CLOSE, kernel, iterations=3)
            kernel = cv2.getStructuringElement(cv2.MORPH_ERODE, (5, 5))
            edge = cv2.erode(edge, kernel, iterations=1)
            edge = cv2.convertScaleAbs(edge)
            out, contours, hierarchy = cv2.findContours(edge, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
            cont = []
            for cnt in contours:
                if cv2.contourArea(cnt) > 1000:
                    cont.append(cnt)

            cv2.drawContours(image, cont, -1, (0, 255, 0), thickness=5)
            cv2.imwrite('%s/defects/scan/scan_contours_%s.jpg' % (self.image_folder, self.layer), image)
        else:
            detector = defect_analysis.DefectDetection(image, overlay, self.layer)
            detector.run()
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (27, 27), 0)
            edge = cv2.Laplacian(gray, cv2.CV_64F)
            for i in xrange(3):
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * i + 1, 2 * i + 1))
                edge = cv2.morphologyEx(edge, cv2.MORPH_CLOSE, kernel)
                edge = cv2.morphologyEx(edge, cv2.MORPH_OPEN, kernel)

            edge = cv2.morphologyEx(edge, cv2.MORPH_CLOSE, kernel, iterations=3)
            kernel = cv2.getStructuringElement(cv2.MORPH_ERODE, (5, 5))
            edge = cv2.erode(edge, kernel, iterations=1)
            edge = cv2.convertScaleAbs(edge)
            out, contours, hierarchy = cv2.findContours(edge, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
            cont = []
            for cnt in contours:
                if cv2.contourArea(cnt) > 1000:
                    cont.append(cnt)

            cv2.drawContours(image, cont, -1, (0, 255, 0), thickness=5)
            cv2.imwrite('%s/defects/single/single_contours_%s.jpg' % (self.image_folder, self.layer), image)

        self.update_status('Defects analyzed.')

    def reset_time_idle(self):
        """Resets the internal countdown that checks if a new image has been captured within a preset period of time"""
        self.stopwatch_instance.reset_time_idle()

    def send_notification(self):
        """Sends a notification to a user if a certain criteria is met
        In this case, this method executes if a picture hasn't been taken in a preset period of time
        Depends if the Notification checkbox is checked or not
        """

        if self.checkNotifications.isChecked():
            self.update_status('Sending email notification.')
            
            # Instantiate and run a Notifications instance
            self.N_instance = extra_functions.Notifications()
            self.N_instance.start()

    def stop(self):
        """Terminates running QThreads, most notably the Stopwatch and ImageCapture instances"""

        self.update_status('Stopped. Waiting for timeout to end.')
        self.stopwatch_instance.stop()
        self.ICR_instance.stop()

    def set_start_layer(self):
        with open('config.json') as config:
            self.config = json.load(config)

        self.config['CaptureCount'] = self.spinStartingLayer.value()
        self.config['CurrentLayer'] = self.spinStartingLayer.value() - 0.5

        with open('config.json', 'w+') as config:
            json.dump(self.config, config, indent=4, sort_keys=True)

    def update_time(self, time_elapsed, time_idle):
        """Updates the stopwatch label at the bottom of the dialog window with the received time"""
        self.labelTimeElapsed.setText('Time Elapsed: %s' % time_elapsed)
        self.labelTimeIdle.setText('Time Idle: %s' % time_idle)

    def update_status(self, string):
        self.labelStatusBar.setText('Status: ' + string)

    def update_progress(self, percentage):
        self.progressBar.setValue(int(percentage))

    def closeEvent(self, event):
        """Executes when the top-right X is clicked"""

        # Stop any running QThreads cleanly before closing the dialog window
        # Try statement in case the ICR_instance doesn't exist
        try:
            if self.ICR_instance.isRunning:
                self.stopwatch_instance.stop()
                self.ICR_instance.stop()
        except (AttributeError, RuntimeError):
            pass

        self.emit(SIGNAL("accepted()"))


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
            json.dump(self.config, config, indent=4, sort_keys=True)

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

        with open('config.json') as config:
            self.config = json.load(config)

        self.buttonBrowseSF.clicked.connect(self.browse_slice)
        self.buttonBrowseF.clicked.connect(self.browse_folder)
        self.buttonStartConversion.clicked.connect(self.start_conversion)
        self.checkDraw.toggled.connect(self.toggle_fill)

        self.slice_list = list()
        self.contours_folder = '%s/contours' % self.config['WorkingDirectory']

        self.lineFolder.setText(self.contours_folder)

    def browse_slice(self):

        # Opens a file select dialog, allowing user to select one or multiple slice files
        files = QtGui.QFileDialog.getOpenFileNames(self, 'Browse...', '', 'Slice Files (*.cls *.cli)')

        for item in files:
            self.slice_list.append(str(item).replace('\\', '/'))

        if self.slice_list:
            self.listSliceFiles.clear()
            self.buttonStartConversion.setEnabled(True)
            self.update_status('Waiting to start conversion.')
            for index, item in enumerate(self.slice_list):
                self.listSliceFiles.addItem(os.path.basename(item))
                if '.cls' in item:
                    self.listSliceFiles.item(index).setBackground(QtGui.QColor('blue'))
                elif '.cli' in item:
                    self.listSliceFiles.item(index).setBackground(QtGui.QColor('yellow'))

    def browse_folder(self):
        # Opens a folder select dialog, allowing the user to select a folder
        self.contours_folder = QtGui.QFileDialog.getExistingDirectory(self, 'Browse...', '')

        if self.folder:
            self.lineFolder.setText(self.contours_folder)

    def start_conversion(self):
        # Disable all buttons to prevent user from doing other tasks
        self.buttonStartConversion.setEnabled(False)
        self.buttonBrowseSF.setEnabled(False)
        self.buttonBrowseF.setEnabled(False)
        self.buttonDone.setEnabled(False)
        self.update_progress(0)

        # Instantiate and run a SliceConverter instance
        self.SC_instance = slice_converter.SliceConverter(self.slice_list, self.checkDraw.isChecked(),
                                                          self.checkFill.isChecked(), self.contours_folder)
        self.connect(self.SC_instance, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.SC_instance, SIGNAL("update_status_slice(QString)"), self.update_status_slice)
        self.connect(self.SC_instance, SIGNAL("update_progress(QString)"), self.update_progress)
        self.connect(self.SC_instance, SIGNAL("finished()"), self.start_conversion_finished)
        self.SC_instance.start()

    def start_conversion_finished(self):
        """Executes when the SliceConverter instance has finished"""

        self.buttonStartConversion.setEnabled(True)
        self.buttonBrowseSF.setEnabled(True)
        self.buttonBrowseF.setEnabled(True)
        self.buttonDone.setEnabled(True)
        self.update_status('Conversion completed successfully.')

    def toggle_fill(self):
        """Enables or disables the Fill Contours checkbox depending if the Draw Contours is checked or not"""
        if self.checkDraw.isChecked():
            self.checkFill.setEnabled(True)
        else:
            self.checkFill.setEnabled(False)
            self.checkFill.setChecked(False)

    def update_status(self, string):
        self.labelStatus.setText(string)

    def update_status_slice(self, string):
        self.labelStatusSlice.setText('Current Slice: ' + string)

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
        self.buttonResults.clicked.connect(self.view_results)

        # Load configuration settings from config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Set the spinbox settings to the previously saved values
        self.spinWidth.setValue(int(self.config['CalibrationWidth']))
        self.spinHeight.setValue(int(self.config['CalibrationHeight']))
        self.spinRatio.setValue(int(self.config['DownscalingRatio']))

    def browse(self):

        # Empty the image list
        self.image_list = list()

        # Opens a folder select dialog, allowing the user to select a folder
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
                if 'image_calibration' in str(image_name):
                    self.image_list.append(str(image_name))

            if not self.image_list:
                self.update_status('No valid calibration images found.')
                self.buttonStartCalibration.setEnabled(False)
            else:
                # Remove previous entries and fill with new entries
                self.listImages.addItems(self.image_list)

                self.buttonStartCalibration.setEnabled(True)
                self.update_status('Waiting to start process.')
                self.update_progress(0)

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

        # Reset the colours of the items in the list widget
        # Try exception causes this function to be skipped the first time when
        try:
            for index in xrange(self.listImages.count()):
                self.listImages.item(index).setBackground(QtGui.QColor('white'))
        except AttributeError:
            pass

        # Instantiate and run a CameraCalibration instance
        self.CC_instance = camera_calibration.Calibration(self.calibration_folder, self.checkSaveC.isChecked(),
                                                          self.checkSaveU.isChecked())
        self.connect(self.CC_instance, SIGNAL("change_colour(QString, QString)"), self.change_colour)
        self.connect(self.CC_instance, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.CC_instance, SIGNAL("update_progress(QString)"), self.update_progress)
        self.connect(self.CC_instance, SIGNAL("finished()"), self.calibration_finished)
        self.CC_instance.start()

    def change_colour(self, index, valid):
        """Changes the background colour of the received item in the listImages box
        Changes to green if image is valid, red if image is invalid for calibration
        """
        if int(valid):
            self.listImages.item(int(index)).setBackground(QtGui.QColor('green'))
        else:
            self.listImages.item(int(index)).setBackground(QtGui.QColor('red'))

    def calibration_finished(self):
        """Executes when the CameraCalibration instance has finished"""

        # Opens a Dialog Window to view Calibration Results
        self.view_results()

        # If the Apply to Sample Image checkbox is checked
        # Applies the image processing techniques using the updated camera parameters
        if self.checkApply.isChecked():
            self.update_status('Processing image...')
            self.update_progress(0)
            image = cv2.imread('%s/calibration/image_sample.png' % self.config['WorkingDirectory'])
            image = image_processing.ImageCorrection(None, None, None).distortion_fix(image)
            self.update_progress(25)
            image = image_processing.ImageCorrection(None, None, None).perspective_fix(image)
            self.update_progress(50)
            image = image_processing.ImageCorrection(None, None, None).crop(image)
            self.update_progress(75)
            cv2.imwrite('%s/calibration/image_sample_DPC.png' % self.config['WorkingDirectory'], image)
            self.update_status('Image successfully processed.')
            self.update_progress(100)

        # Enable or disable relevant UI elements to prevent concurrent processes
        self.buttonBrowse.setEnabled(True)
        self.buttonStartCalibration.setEnabled(True)
        self.buttonDone.setEnabled(True)

    def view_results(self):
        """Opens a Dialog Window when the CameraCalibration instance has finished
        Or when the View Results button is clicked
        Displays the results of the camera calibration to the user"""

        # Check if a camera_parameters.txt file exists
        if os.path.isfile('%s/camera_parameters.txt' % self.config['WorkingDirectory']):
            # Check if the window is already open, if so, reopens the window with any updated parameters
            try:
                self.calibration_results_dialog.close()
            except:
                pass

            self.calibration_results_dialog = CalibrationResults(self)
            self.calibration_results_dialog.show()
        else:
            self.update_status('Camera Parameters text file not found.')

    def save_settings(self):
        """Save the spinxbox values to config.json file"""

        # Save the new values from the changed settings to the config dictionary
        self.config['CalibrationWidth'] = self.spinWidth.value()
        self.config['CalibrationHeight'] = self.spinHeight.value()
        self.config['DownscalingRatio'] = self.spinRatio.value()

        # Save configuration settings to config.json file
        with open('config.json', 'w+') as config:
            json.dump(self.config, config, indent=4, sort_keys=True)

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


class CalibrationResults(QtGui.QDialog, dialogCalibrationResults.Ui_dialogCalibrationResults):
    """Opens a Dialog Window when the CameraCalibration instance has finished
    Allows user to look at pertinent calibration parameters and information
    Setup as a Modeless window, opereating independently of other windows
    """

    def __init__(self, parent=None):

        # Setup Dialog UI with CameraCalibration as parent
        super(CalibrationResults, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        # Restore the last window position when the window is closed and reopened by saving it using QSettings
        self.window_position = QSettings('MCAM', 'Defect Monitor')
        self.restoreGeometry(self.window_position.value('geometry', '').toByteArray())

        # Initialize a list to store camera parameters
        self.camera_parameters = []

        # Load configuration settings from config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Load camera parameters from specified calibration file
        with open('%s/camera_parameters.txt' % self.config['WorkingDirectory'], 'r') as camera_parameters:
            for line in camera_parameters.readlines():
                self.camera_parameters.append(line.split(' '))

        # Split camera parameters into their own respective values to be used in OpenCV functions
        self.camera_matrix = np.array(self.camera_parameters[1:4]).astype('float')
        self.distortion_coefficients = np.array(self.camera_parameters[5]).astype('float')
        self.homography_matrix = np.array(self.camera_parameters[7:10]).astype('float')
        self.rms = np.array(self.camera_parameters[13]).astype('float')

        # Nested for loops to access each of the table boxes in order
        for row in xrange(3):
            for column in xrange(3):

                # Setting the item using the corresponding index of the matrix arrays
                self.tableCameraMatrix.setItem(row, column, QtGui.QTableWidgetItem(
                    format(self.camera_matrix[row][column], '.10g')))
                self.tableHomographyMatrix.setItem(row, column, QtGui.QTableWidgetItem(
                    format(self.homography_matrix[row][column], '.10g')))

                # Because the distortion coefficients matrix is a 1x5, a slight modification needs to be made
                # Exception used to ignore the 2x3 box and 3rd row of the matrix
                if row >= 1: column += 3
                try:
                    self.tableDistortionCoefficients.setItem(row, column % 3, QtGui.QTableWidgetItem(
                        format(self.distortion_coefficients[column], '.10g')))
                except IndexError:
                    pass

        # Displaying the re-projection error on the appropriate text label
        self.labelRMS.setText('Re-Projection Error: ' + format(self.rms[0], '.10g'))

    def accept(self):
        """Executes when the Done button is clicked"""
        self.done(1)

    def closeEvent(self, event):
        """Executes when the window is closed"""

        # Save the current position of the dialog window
        self.window_position.setValue('geometry', self.saveGeometry())


class OverlayAdjustment(QtGui.QDialog, dialogOverlayAdjustment.Ui_dialogOverlayAdjustment):
    """Opens a Dialog Window when the Overlay Adjustment button is clicked
    If an overlay is on the display, allows the user to adjust its position in quite a few ways
    Setup as a Modeless window, opereating independently of other windows
    """

    def __init__(self, parent=None):

        # Setup Dialog UI with CameraCalibration as parent
        super(OverlayAdjustment, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        # Load configuration settings from config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Transformation Parameters saved as a list of the respective transformation values
        self.transform = self.config['TransformationParameters']
        self.transform_states = list()

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        # General
        self.buttonReset.clicked.connect(self.reset)
        self.buttonUndo.clicked.connect(self.undo)

        # Translation
        self.buttonTranslateUp.clicked.connect(self.translate_up)
        self.buttonTranslateDown.clicked.connect(self.translate_down)
        self.buttonTranslateLeft.clicked.connect(self.translate_left)
        self.buttonTranslateRight.clicked.connect(self.translate_right)

        # Rotation / Flip
        self.buttonRotateACW.clicked.connect(self.rotate_acw)
        self.buttonRotateCW.clicked.connect(self.rotate_cw)
        self.buttonFlipHorizontal.clicked.connect(self.flip_horizontal)
        self.buttonFlipVertical.clicked.connect(self.flip_vertical)

        # Stretch / Pull
        self.buttonResetStretch.clicked.connect(self.stretch_reset)
        self.buttonStretchN.clicked.connect(self.stretch_n)
        self.buttonStretchNE.clicked.connect(self.stretch_ne)
        self.buttonStretchE.clicked.connect(self.stretch_e)
        self.buttonStretchSE.clicked.connect(self.stretch_se)
        self.buttonStretchS.clicked.connect(self.stretch_s)
        self.buttonStretchSW.clicked.connect(self.stretch_sw)
        self.buttonStretchW.clicked.connect(self.stretch_w)
        self.buttonStretchNW.clicked.connect(self.stretch_nw)

        self.buttonStretchUpLeft.clicked.connect(self.stretch_ul)
        self.buttonStretchLeftUp.clicked.connect(self.stretch_lu)
        self.buttonStretchUpRight.clicked.connect(self.stretch_ur)
        self.buttonStretchRightUp.clicked.connect(self.stretch_ru)
        self.buttonStretchDownLeft.clicked.connect(self.stretch_dl)
        self.buttonStretchLeftDown.clicked.connect(self.stretch_ld)
        self.buttonStretchDownRight.clicked.connect(self.stretch_dr)
        self.buttonStretchRightDown.clicked.connect(self.stretch_rd)

    def reset(self):
        self.transform = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.save()

    def undo(self):
        del self.transform_states[-1]
        self.transform = self.transform_states[-1]
        self.save(True)

    def translate_up(self):
        self.transform[0] -= self.spinPixels.value()
        self.save()

    def translate_down(self):
        self.transform[0] += self.spinPixels.value()
        self.save()

    def translate_left(self):
        self.transform[1] -= self.spinPixels.value()
        self.save()

    def translate_right(self):
        self.transform[1] += self.spinPixels.value()
        self.save()

    def rotate_acw(self):
        self.transform[2] += self.spinDegrees.value()
        self.save()

    def rotate_cw(self):
        self.transform[2] -= self.spinDegrees.value()
        self.save()

    def flip_horizontal(self):
        self.transform[3] ^= 1
        self.save()

    def flip_vertical(self):
        self.transform[4] ^= 1
        self.save()

    def stretch_reset(self):
        self.transform[5:] = [0] * (len(self.transform) - 5)
        self.save()

    def stretch_n(self):
        self.transform[5] -= self.spinPixels.value()
        self.save()

    def stretch_ne(self):
        self.transform[5] -= self.spinPixels.value()
        self.transform[6] += self.spinPixels.value()
        self.save()

    def stretch_e(self):
        self.transform[6] += self.spinPixels.value()
        self.save()

    def stretch_se(self):
        self.transform[7] += self.spinPixels.value()
        self.transform[6] += self.spinPixels.value()
        self.save()

    def stretch_s(self):
        self.transform[7] += self.spinPixels.value()
        self.save()

    def stretch_sw(self):
        self.transform[7] += self.spinPixels.value()
        self.transform[8] -= self.spinPixels.value()
        self.save()

    def stretch_w(self):
        self.transform[8] -= self.spinPixels.value()
        self.save()

    def stretch_nw(self):
        self.transform[5] -= self.spinPixels.value()
        self.transform[8] -= self.spinPixels.value()
        self.save()

    def stretch_ul(self):
        self.transform[9] -= self.spinPixels.value()
        self.save()

    def stretch_lu(self):
        self.transform[10] -= self.spinPixels.value()
        self.save()

    def stretch_ur(self):
        self.transform[11] += self.spinPixels.value()
        self.save()

    def stretch_ru(self):
        self.transform[12] -= self.spinPixels.value()
        self.save()

    def stretch_dl(self):
        self.transform[13] -= self.spinPixels.value()
        self.save()

    def stretch_ld(self):
        self.transform[14] += self.spinPixels.value()
        self.save()

    def stretch_dr(self):
        self.transform[15] += self.spinPixels.value()
        self.save()

    def stretch_rd(self):
        self.transform[16] += self.spinPixels.value()
        self.save()

    def save(self, undo_flag=False):

        self.emit(SIGNAL("overlay_adjustment_execute(PyQt_PyObject)"), self.transform)

        if not undo_flag:
            self.transform_states.append(self.transform[:])

        if len(self.transform_states) > 10:
            del self.transform_states[0]

        self.config['TransformationParameters'] = self.transform

        # Save configuration settings to config.json file
        with open('config.json', 'w+') as config:
            json.dump(self.config, config, indent=4, sort_keys=True)

    def closeEvent(self, event):
        """Executes when the top-right X is clicked"""
        self.emit(SIGNAL("accepted()"))