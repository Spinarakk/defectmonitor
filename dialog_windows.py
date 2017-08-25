# Import external libraries
import os
import time
import cv2
import numpy as np
import json
from datetime import datetime
from validate_email import validate_email
from PyQt4.QtGui import *
from PyQt4.QtCore import *

# Import related modules
import slice_converter
import image_processing
import extra_functions
import camera_calibration
import defect_analysis

# Import PyQt GUIs
from gui import dialogNewBuild, dialogCameraCalibration, dialogCalibrationResults, \
    dialogSliceConverter, dialogImageCapture, dialogCameraSettings, dialogOverlayAdjustment


class NewBuild(QDialog, dialogNewBuild.Ui_dialogNewBuild):
    """Opens a Modal Dialog Window when File -> New... or File -> Open... or Tools -> Settings is clicked
    Allows the user to setup a new build and change settings
    """

    def __init__(self, parent=None, open_flag=False):

        # Setup Dialog UI with MainWindow as parent
        super(NewBuild, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        # Setup event listeners for all the relevent UI components, and connect them to specific functions
        # Buttons
        self.buttonBrowseSF.clicked.connect(self.browse_slice)
        self.buttonBrowseBF.clicked.connect(self.browse_build_folder)
        self.buttonSendTestEmail.clicked.connect(self.send_test)
        self.lineEmailAddress.textChanged.connect(self.enable_button)

        with open('config.json') as config:
            self.config = json.load(config)

        # Flag to prevent additional image folders from being created
        self.open_flag = open_flag

        # Set and display the default build image save folder
        self.slice_file_list = list()
        self.build_folder_name = self.config['BuildInfo']['Folder']
        self.lineBuildFolder.setText(self.build_folder_name)

        # If this dialog window was opened as a result of the Open... action, then the following is executed
        # Set and display the relevant names/values of the following text boxes as outlined in the opened config file
        if self.open_flag:
            self.setWindowTitle('Open Build')
            self.lineBuildName.setText(self.config['BuildInfo']['Name'])
            self.comboPlatform.setCurrentIndex(self.config['BuildInfo']['Platform'])
            self.slice_file_list = self.config['SliceConverter']['Files']
            self.set_list(self.config['SliceConverter']['Files'])
            self.lineUsername.setText(self.config['BuildInfo']['Username'])
            self.lineEmailAddress.setText(self.config['BuildInfo']['EmailAddress'])
            self.checkConvert.setChecked(self.config['BuildInfo']['Convert'])
            self.checkDraw.setChecked(self.config['BuildInfo']['Draw'])
            self.checkMinor.setChecked(self.config['Notifications']['Minor'])
            self.checkMajor.setChecked(self.config['Notifications']['Major'])
            self.checkFailure.setChecked(self.config['Notifications']['Failure'])
            self.checkError.setChecked(self.config['Notifications']['Error'])

    def browse_slice(self):
        """Opens a File Dialog, allowing the user to select one or multiple slice files"""

        file_names = QFileDialog.getOpenFileNames(self, 'Browse...', '', 'Slice Files (*.cls *.cli)')

        # Turn the received QFileList into a Python list of file names using list comprehension
        file_list = [str(item).replace('\\', '/') for item in file_names]

        # Check if a file has been selected as QFileDialog returns an empty string if cancel was pressed
        if file_list:
            self.set_list(file_list)
            self.slice_file_list = file_list

    def browse_build_folder(self):
        """Opens a File Dialog, allowing the user to select a folder to store the current build's image folder"""

        folder_name = str(QFileDialog.getExistingDirectory(self, 'Browse...', '')).replace('\\', '/')

        if folder_name:
            # Display just the file name on the line box
            self.lineBuildFolder.setText(folder_name)
            self.build_folder_name = folder_name

    def send_test(self):
        """Sends a test notification email to the entered email address"""

        # Open a message box with a send test email confirmation message so accidental emails don't get sent
        send_confirmation = QMessageBox()
        send_confirmation.setIcon(QMessageBox.Question)
        send_confirmation.setText('Are you sure you want to send a test email notification to %s?\n\n'
                                  'Note: This will save your entered Username and Email Address to the config file.' %
                                  self.lineEmailAddress.text())
        send_confirmation.setWindowTitle('Send Test Email')
        send_confirmation.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        retval = send_confirmation.exec_()

        # If the user clicked Yes
        if retval == 16384:
            if validate_email(self.lineEmailAddress.text()):
                # Disable the Send Test Email button to prevent SPAM
                self.buttonSendTestEmail.setEnabled(False)

                self.config['BuildInfo']['Username'] = str(self.lineUsername.text())
                self.config['BuildInfo']['EmailAddress'] = str(self.lineEmailAddress.text())
                with open('config.json', 'w+') as config:
                    json.dump(self.config, config, indent=4, sort_keys=True)

                # Construct the subject lien and message to be sent here
                subject = 'Test Email Notification'
                message = 'This is a test email to check if the entered email address is valid.'
                if self.checkAddAttachment.isChecked():
                    attachment = 'test_image.jpg'
                else:
                    attachment = None

                # Instantiate and run a Notifications instance
                self.N_instance = extra_functions.Notifications(subject, message, attachment)
                self.N_instance.start()
                self.connect(self.N_instance, SIGNAL("finished()"), self.send_test_finished)
            else:
                # Opens a message box indicating that the entered email address is invalid
                invalid_email_error = QMessageBox()
                invalid_email_error.setIcon(QMessageBox.Critical)
                invalid_email_error.setText('Invalid email address. Please enter a valid email address.')
                invalid_email_error.setWindowTitle('Error')
                invalid_email_error.exec_()

    def send_test_finished(self):
        """Open a message box with a send test confirmation message"""
        send_test_confirmation = QMessageBox()
        send_test_confirmation.setIcon(QMessageBox.Information)
        send_test_confirmation.setText('An email notification has been sent to %s at %s.' %
                                            (self.lineEmailAddress.text(), self.lineUsername.text()))
        send_test_confirmation.setWindowTitle('Send Test Email')
        send_test_confirmation.exec_()

    def set_list(self, file_list):
        """Adds file names to the ListWidget and sets the background colour depending on the stated conditions"""

        self.listSliceFiles.clear()

        for index, item in enumerate(file_list):
            self.listSliceFiles.addItem(os.path.basename(item))
            if '.cls' in item:
                self.listSliceFiles.item(index).setBackground(QColor('blue'))
            elif '.cli' in item:
                self.listSliceFiles.item(index).setBackground(QColor('yellow'))

    def enable_button(self):
        """(Re-)Enables the Send Test Email button if the email address box is changed and not empty"""

        if self.lineEmailAddress.text():
            self.buttonSendTestEmail.setEnabled(True)
            self.checkAddAttachment.setEnabled(True)
        else:
            self.buttonSendTestEmail.setEnabled(False)
            self.checkAddAttachment.setEnabled(False)

    def accept(self):
        """Executes when the Create button is clicked
        First checks if all the required boxes have been filled, otherwise a MessageBox will be opened
        Saves important selection options to the config.json file and closes the window
        """

        error_message = str()

        if not self.lineBuildName.text():
            error_message += 'Build Name not entered.\n'
        if not self.slice_file_list:
            error_message += 'Slice files not selected.\n'
        if not self.lineUsername.text():
            error_message += 'Username not entered.\n'
        if not validate_email(self.lineEmailAddress.text()):
            error_message += 'Email Address not valid.\n'

        if error_message:
            invalid_entries_error = QMessageBox()
            invalid_entries_error.setIcon(QMessageBox.Critical)
            invalid_entries_error.setText(error_message.rstrip('\n'))
            invalid_entries_error.setWindowTitle('Error')
            invalid_entries_error.exec_()
        else:
            # Save all the entered information to the config file
            self.config['BuildInfo']['Name'] = str(self.lineBuildName.text())
            self.config['BuildInfo']['Platform'] = self.comboPlatform.currentIndex()
            self.config['BuildInfo']['Username'] = str(self.lineUsername.text())
            self.config['BuildInfo']['EmailAddress'] = str(self.lineEmailAddress.text())
            self.config['BuildInfo']['Convert'] = self.checkConvert.isChecked()
            if self.checkConvert.isChecked():
                self.config['BuildInfo']['Draw'] = self.checkDraw.isChecked()
            self.config['BuildInfo']['Folder'] = self.build_folder_name
            self.config['SliceConverter']['Files'] = self.slice_file_list
            self.config['Notifications']['Minor'] = self.checkMinor.isChecked()
            self.config['Notifications']['Major'] = self.checkMajor.isChecked()
            self.config['Notifications']['Failure'] = self.checkFailure.isChecked()
            self.config['Notifications']['Error'] = self.checkError.isChecked()

            # Save the selected platform dimensions to the config.json file
            if self.comboPlatform.currentIndex() == 0:
                self.config['BuildInfo']['PlatformDimensions'] = [636.0, 406.0]
            elif self.comboPlatform.currentIndex() == 1:
                self.config['BuildInfo']['PlatformDimensions'] = [800.0, 400.0]
            elif self.comboPlatform.currentIndex() == 2:
                self.config['BuildInfo']['PlatformDimensions'] = [250.0, 250.0]

            if not self.open_flag:
                # Generate a timestamp for folder labelling purposes
                current_time = datetime.now()

                # Set the full name of the main storage folder for all acquired images
                image_folder = """%s/%s-%s-%s [%s''%s'%s] %s""" % \
                               (self.config['BuildInfo']['Folder'], current_time.year, str(current_time.month).zfill(2),
                                str(current_time.day).zfill(2), str(current_time.hour).zfill(2),
                                str(current_time.minute).zfill(2), str(current_time.second).zfill(2),
                                self.config['BuildInfo']['Name'])

                # Save the created image folder's name to the config.json file
                self.config['ImageCapture']['Folder'] = image_folder

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

            with open('config.json', 'w+') as config:
                json.dump(self.config, config, indent=4, sort_keys=True)

            # Close the dialog window and return True
            self.done(1)


class CameraCalibration(QDialog, dialogCameraCalibration.Ui_dialogCameraCalibration):
    """Opens a Modeless Dialog Window when the Camera Calibration button is clicked
    Or when Tools -> Camera -> Calibration is clicked
    Allows the user to select a folder of chessboard images to calculate the camera's intrinsic values for calibration
    """

    def __init__(self, parent=None):

        # Setup Dialog UI with MainWindow as parent and restore the previous window state
        super(CameraCalibration, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.window_settings = QSettings('MCAM', 'Defect Monitor')
        self.restoreGeometry(self.window_settings.value('geometry', '').toByteArray())

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        self.buttonBrowseF.clicked.connect(self.browse_folder)
        self.buttonBrowseHI.clicked.connect(self.browse_homography)
        self.buttonBrowseTI.clicked.connect(self.browse_test_image)
        self.buttonStart.clicked.connect(self.start)
        self.buttonResults.clicked.connect(self.view_results)
        self.buttonSave.clicked.connect(self.save_results)

        # Load configuration settings from config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Set the SpinBox settings to the previously saved values
        self.spinWidth.setValue(int(self.config['CameraCalibration']['Width']))
        self.spinHeight.setValue(int(self.config['CameraCalibration']['Height']))
        self.spinRatio.setValue(int(self.config['CameraCalibration']['DownscalingRatio']))

        # Set the LineEdit text to the previously saved file names
        self.lineHomographyImage.setText(os.path.basename(self.config['CameraCalibration']['HomographyImage']))
        self.lineTestImage.setText(os.path.basename(self.config['CameraCalibration']['TestImage']))

    def browse_folder(self):

        # Empty the image list
        self.image_list = list()

        # Opens a folder select dialog, allowing the user to select a folder
        self.calibration_folder = None
        self.calibration_folder = QFileDialog.getExistingDirectory(self, 'Browse...', '')

        # Checks if a folder is actually selected
        if self.calibration_folder:
            # Store a list of the files found in the folder
            image_list = os.listdir(self.calibration_folder)
            self.listImages.clear()

            # Update the lineEdit with the new folder name
            self.lineCalibrationFolder.setText(self.calibration_folder)

            # Search for images containing the word calibration_image in the folder
            for image_name in image_list:
                if 'image_calibration' in str(image_name):
                    self.image_list.append(str(image_name))

            if not self.image_list:
                self.update_status('No calibration images found.')
                self.buttonStart.setEnabled(False)
            else:
                # Remove previous entries and fill with new entries
                self.listImages.addItems(self.image_list)

                self.buttonStart.setEnabled(True)
                self.update_status('Waiting to start process.')
                self.update_progress(0)

    def browse_homography(self):
        """Opens a File Dialog, allowing the user to select an homography image"""

        file_name = str(QFileDialog.getOpenFileName(self, 'Browse...', '', 'Image File (*.png)')).replace('\\', '/')

        if file_name:
            self.config['CameraCalibration']['HomographyImage'] = file_name
            self.lineHomographyImage.setText(os.path.basename(self.config['CameraCalibration']['HomographyImage']))

    def browse_test_image(self):
        """Opens a File Dialog, allowing the user to select a test image"""

        file_name = str(QFileDialog.getOpenFileName(self, 'Browse...', '', 'Image File (*.png)')).replace('\\', '/')

        if file_name:
            self.config['CameraCalibration']['TestImage'] = file_name
            self.lineTestImage.setText(os.path.basename(self.config['CameraCalibration']['TestImage']))

    def start(self):
        """Executes when the Start Calibration button is clicked
        Starts the calibration process after saving the calibration settings to config.json file
        """

        # Enable or disable relevant UI elements to prevent concurrent processes
        self.buttonBrowseF.setEnabled(False)
        self.buttonBrowseHI.setEnabled(False)
        self.buttonBrowseTI.setEnabled(False)
        self.buttonStart.setEnabled(False)
        self.buttonDone.setEnabled(False)

        # Save calibration settings
        self.save()

        # Reset the colours of the items in the list widget
        # Try exception causes this function to be skipped the first time
        try:
            for index in xrange(self.listImages.count()):
                self.listImages.item(index).setBackground(QColor('white'))
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
            self.listImages.item(int(index)).setBackground(QColor('green'))
        else:
            self.listImages.item(int(index)).setBackground(QColor('red'))

    def calibration_finished(self):
        """Executes when the CameraCalibration instance has finished"""

        # Opens a Dialog Window to view Calibration Results
        self.view_results(True)

        # If the Apply to Sample Image checkbox is checked
        # Applies the image processing techniques using the updated camera parameters
        if self.checkApply.isChecked():
            self.update_status('Processing test image...')
            self.update_progress(0)
            image = cv2.imread(self.config['CameraCalibration']['TestImage'])
            image = image_processing.ImageCorrection(None, test_flag=True).distortion_fix(image)
            self.update_progress(25)
            image = image_processing.ImageCorrection(None, test_flag=True).perspective_fix(image)
            self.update_progress(50)
            image = image_processing.ImageCorrection(None, test_flag=True).crop(image)
            self.update_progress(75)
            cv2.imwrite(self.config['CameraCalibration']['TestImage'].replace('.png', '_DPC.png'), image)
            self.update_status('Test Image successfully processed.')
            self.update_progress(100)

        # Enable or disable relevant UI elements to prevent concurrent processes
        self.buttonBrowseF.setEnabled(True)
        self.buttonBrowseHI.setEnabled(True)
        self.buttonBrowseTI.setEnabled(True)
        self.buttonStart.setEnabled(True)
        self.buttonSave.setEnabled(True)
        self.buttonDone.setEnabled(True)

    def view_results(self, calibration_flag=False):
        """Opens a Dialog Window when the CameraCalibration instance has finished
        Or when the View Results button is clicked
        Displays the results of the camera calibration to the user
        """

        if calibration_flag:
            with open('%s/calibration_results.json' % self.config['WorkingDirectory']) as file:
                results = json.load(file)
        else:
            results = self.config.copy()

        try:
            self.calibration_results_dialog.close()
        except:
            pass

        self.calibration_results_dialog = CalibrationResults(self, results['ImageCorrection'])
        self.calibration_results_dialog.show()

    def save_results(self):
        with open('%s/calibration_results.json' % self.config['WorkingDirectory']) as file:
            results = json.load(file)
        self.config.update(results)
        self.save()
        self.update_status('Calibration results saved to the config file.')
        self.buttonSave.setEnabled(False)

    def save(self):
        """Save the spinxBox values to the config.json file"""

        self.config['CameraCalibration']['Width'] = self.spinWidth.value()
        self.config['CameraCalibration']['Height'] = self.spinHeight.value()
        self.config['CameraCalibration']['DownscalingRatio'] = self.spinRatio.value()

        with open('config.json', 'w+') as config:
            json.dump(self.config, config, indent=4, sort_keys=True)

    def update_status(self, string):
        self.labelStatus.setText(string)

    def update_progress(self, percentage):
        self.progressBar.setValue(int(percentage))

    def closeEvent(self, event):
        """Executes when the window is closed"""

        self.save()

        # Save the current position of the Dialog Window before the window is closed
        self.window_settings.setValue('geometry', self.saveGeometry())


class ImageCapture(QDialog, dialogImageCapture.Ui_dialogImageCapture):
    """Opens a Modeless Dialog Window when the Image Capture button is clicked
    Or when Tools -> Camera -> Image Capture is clicked
    Allows the user to capture images from an attached camera, either a single shot or continuously using a trigger
    """

    def __init__(self, parent=None, image_folder=None):

        # Setup Dialog UI with MainWindow as parent and restore the previous window state
        super(ImageCapture, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.window_settings = QSettings('MCAM', 'Defect Monitor')
        self.restoreGeometry(self.window_settings.value('geometry', '').toByteArray())

        # Import module and set as instance variable only within this class so that the other classes can run without it
        import image_capture
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

        # Flags to check if the camera and/or trigger is detected
        self.camera_flag = False
        self.trigger_flag = False

        # Instantiate dialog variables that cannot have multiple windows for existence validation purposes
        self.CS_dialog = None

    def browse(self):

        # Opens a folder select dialog, allowing the user to choose a folder
        self.image_folder = QFileDialog.getExistingDirectory(self, 'Browse...')

        # Checks if a folder is actually selected
        if self.image_folder:
            # Display the folder name
            self.lineImageFolder.setText(self.image_folder)
            if bool(self.camera_flag):
                self.buttonCapture.setEnabled(True)
            if bool(self.camera_flag) & bool(self.trigger_flag):
                self.buttonRun.setEnabled(True)

    def camera_settings(self):
        """Opens a Modeless Dialog Window when the Camera Settings button is clicked
        Allows the user to change camera settings which will be sent to the camera before images are taken
        """

        if self.CS_dialog is None:
            self.CS_dialog = CameraSettings(self)
            self.connect(self.CS_dialog, SIGNAL("destroyed()"), self.camera_settings_closed)
            self.CS_dialog.show()
        else:
            self.CS_dialog.activateWindow()

    def camera_settings_closed(self):
        """When the Dialog Window is closed, its object is set to None to allow another window to be opened"""
        self.CS_dialog = None

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
        self.connect(self.ICS_instance, SIGNAL("image_correction(PyQt_PyObject, QString, QString)"),
                     self.image_correction)
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
        # self.connect(self.stopwatch_instance, SIGNAL("send_notification()"), self.send_notification)
        self.stopwatch_instance.start()

        # Instantiate and run an ImageCapture instance that will run indefinitely until the stop button is pressed
        self.ICR_instance = self.image_capture.ImageCapture(run_flag=True)
        self.connect(self.ICR_instance, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.ICR_instance, SIGNAL("image_correction(PyQt_PyObject, QString, QString)"),
                     self.image_correction)
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
        if self.phase == 'coat':
            index = '0'
        elif self.phase == 'scan':
            index = '1'
        else:
            index = '4'

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

        self.config['ImageCapture']['Single'] = self.spinStartingLayer.value()
        self.config['ImageCapture']['Layer'] = self.spinStartingLayer.value() - 0.5

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
        """Executes when the window is closed"""

        self.window_settings.setValue('geometry', self.saveGeometry())

        # Stop any running QThreads cleanly before closing the dialog window
        # Try statement in case the ICR_instance doesn't exist
        try:
            if self.ICR_instance.isRunning:
                self.stopwatch_instance.stop()
                self.ICR_instance.stop()
        except (AttributeError, RuntimeError):
            pass


class CameraSettings(QDialog, dialogCameraSettings.Ui_dialogCameraSettings):
    """Opens a Modeless Dialog Window when Tools -> Camera -> Settings is clicked
    Or when the Camera Settings button in the Image Capture Dialog Window is clicked
    Allows the user to change camera settings which will be sent to the camera before images are taken
    """

    def __init__(self, parent=None):

        # Setup Dialog UI with MainWindow as parent and restore the previous window state
        super(CameraSettings, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.window_settings = QSettings('MCAM', 'Defect Monitor')
        self.restoreGeometry(self.window_settings.value('geometry', '').toByteArray())

        with open('config.json') as config:
            self.config = json.load(config)

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        self.buttonApply.clicked.connect(self.apply)

        # Setup event listeners for all the setting boxes to detect a change
        self.comboPixelFormat.currentIndexChanged.connect(self.apply_enable)
        self.spinExposureTime.valueChanged.connect(self.apply_enable)
        self.spinPacketSize.valueChanged.connect(self.apply_enable)
        self.spinInterPacketDelay.valueChanged.connect(self.apply_enable)
        self.spinFrameDelay.valueChanged.connect(self.apply_enable)
        self.spinTriggerTimeout.valueChanged.connect(self.apply_enable)

        # Set the combo box and settings to the previously saved values
        # Combo box settings are saved as their index values in the config.json file
        self.comboPixelFormat.setCurrentIndex(int(self.config['CameraSettings']['PixelFormat']))
        self.spinExposureTime.setValue(int(self.config['CameraSettings']['ExposureTimeAbs']))
        self.spinPacketSize.setValue(int(self.config['CameraSettings']['PacketSize']))
        self.spinInterPacketDelay.setValue(int(self.config['CameraSettings']['InterPacketDelay']))
        self.spinFrameDelay.setValue(int(self.config['CameraSettings']['FrameTransmissionDelay']))
        self.spinTriggerTimeout.setValue(int(self.config['ImageCapture']['TriggerTimeout']))

        self.buttonApply.setEnabled(False)

    def apply_enable(self):
        """Enable the Apply button on any change of setting values"""
        self.buttonApply.setEnabled(True)

    def apply(self):
        # Save the new index values from the changed settings to the config dictionary
        self.config['CameraSettings']['PixelFormat'] = self.comboPixelFormat.currentIndex()
        self.config['CameraSettings']['ExposureTimeAbs'] = self.spinExposureTime.value()
        self.config['CameraSettings']['PacketSize'] = self.spinPacketSize.value()
        self.config['CameraSettings']['InterPacketDelay'] = self.spinInterPacketDelay.value()
        self.config['CameraSettings']['FrameTransmissionDelay'] = self.spinFrameDelay.value()
        self.config['ImageCapture']['TriggerTimeout'] = self.spinTriggerTimeout.value()

        # Save configuration settings to config.json file
        with open('config.json', 'w+') as config:
            json.dump(self.config, config, indent=4, sort_keys=True)

        # Disable the Apply button until another setting is changed
        self.buttonApply.setEnabled(False)

    def accept(self):
        """Executes when the OK button is pressed
        If the settings have changed, the apply function is executed before closing the window"""

        if self.buttonApply.isEnabled():
            self.apply()

        self.closeEvent(self.close())

    def closeEvent(self, event):
        """Executes when the window is closed"""
        self.window_settings.setValue('geometry', self.saveGeometry())


class SliceConverter(QDialog, dialogSliceConverter.Ui_dialogSliceConverter):
    """Opens a Modeless Dialog Window when the Slice Converter button is clicked
    Or when Tools -> Slice Converter is clicked
    Allows user to convert .cls or .cli files into ASCII encoded scaled contours that OpenCV can draw
    """

    def __init__(self, parent=None):

        # Setup Dialog UI with MainWindow as parent and restore the previous window state
        super(SliceConverter, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.window_settings = QSettings('MCAM', 'Defect Monitor')
        self.restoreGeometry(self.window_settings.value('geometry', '').toByteArray())

        with open('config.json') as config:
            self.config = json.load(config)

        self.buttonBrowseSF.clicked.connect(self.browse_slice)
        self.buttonBrowseF.clicked.connect(self.browse_folder)
        self.buttonStart.clicked.connect(self.start)

        self.slice_list = list()
        self.contours_folder = '%s/contours' % self.config['WorkingDirectory']

        self.lineFolder.setText(self.contours_folder)

    def browse_slice(self):
        """Opens a File Dialog, allowing the user to select one or multiple slice files
        The slice files are displayed on the ListWidget and saved to the config file
        """

        file_names = QFileDialog.getOpenFileNames(self, 'Browse...', '', 'Slice Files (*.cls *.cli)')

        file_list = [str(item).replace('\\', '/') for item in file_names]

        for item in file_list:
            self.slice_list.append(str(item).replace('\\', '/'))

        if self.slice_list:
            self.listSliceFiles.clear()
            self.buttonStart.setEnabled(True)
            self.update_status('Current Part: None | Waiting to start conversion.')
            for index, item in enumerate(self.slice_list):
                self.listSliceFiles.addItem(os.path.basename(item))
                if '.cls' in item:
                    self.listSliceFiles.item(index).setBackground(QColor('blue'))
                elif '.cli' in item:
                    self.listSliceFiles.item(index).setBackground(QColor('yellow'))

    def browse_folder(self):
        # Opens a folder select dialog, allowing the user to select a folder
        self.contours_folder = QFileDialog.getExistingDirectory(self, 'Browse...', '')

        if self.contours_folder:
            self.lineFolder.setText(self.contours_folder)

    def start(self):
        # Disable all buttons to prevent user from doing other tasks
        self.buttonStart.setEnabled(False)
        self.buttonBrowseSF.setEnabled(False)
        self.buttonBrowseF.setEnabled(False)
        self.buttonDone.setEnabled(False)
        self.update_progress(0)

        # Instantiate and run a SliceConverter instance
        self.SC_instance = slice_converter.SliceConverter(self.slice_list, self.checkDraw.isChecked(), self.contours_folder)
        self.connect(self.SC_instance, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.SC_instance, SIGNAL("update_progress(QString)"), self.update_progress)
        self.connect(self.SC_instance, SIGNAL("finished()"), self.start_conversion_finished)
        self.SC_instance.start()

    def start_conversion_finished(self):
        """Executes when the SliceConverter instance has finished"""

        self.buttonStart.setEnabled(True)
        self.buttonBrowseSF.setEnabled(True)
        self.buttonBrowseF.setEnabled(True)
        self.buttonDone.setEnabled(True)
        self.update_status('Current Part: None | Conversion completed successfully.')

    def update_status(self, string):
        string = string.split(' | ')
        self.labelStatus.setText(string[1])
        self.labelStatusSlice.setText(string[0])

    def update_progress(self, percentage):
        self.progressBar.setValue(int(percentage))

    def closeEvent(self, event):
        """Executes when the window is closed"""
        self.window_settings.setValue('geometry', self.saveGeometry())


class OverlayAdjustment(QDialog, dialogOverlayAdjustment.Ui_dialogOverlayAdjustment):
    """Opens a Modeless Dialog Window when the Overlay Adjustment button is clicked
    Or when Tools -> Overlay Adjustment is clicked
    Allows the user to adjust and transform the overlay image in a variety of ways
    """

    def __init__(self, parent=None):

        # Setup Dialog UI with MainWindow as parent and restore the previous window state
        super(OverlayAdjustment, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.window_settings = QSettings('MCAM', 'Defect Monitor')
        self.restoreGeometry(self.window_settings.value('geometry', '').toByteArray())

        with open('config.json') as config:
            self.config = json.load(config)

        # Transformation Parameters saved as a list of the respective transformation values
        self.transform = self.config['ImageCorrection']['TransformParameters']
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

        self.emit(SIGNAL("update_overlay(PyQt_PyObject)"), self.transform)

        if not undo_flag:
            self.transform_states.append(self.transform[:])

        if len(self.transform_states) > 10:
            del self.transform_states[0]

        self.config['ImageCorrection']['TransformParameters'] = self.transform

        with open('config.json', 'w+') as config:
            json.dump(self.config, config, indent=4, sort_keys=True)

    def closeEvent(self, event):
        """Executes when the window is closed"""
        self.window_settings.setValue('geometry', self.saveGeometry())


class CalibrationResults(QDialog, dialogCalibrationResults.Ui_dialogCalibrationResults):
    """Opens a Modeless Dialog Window when the CameraCalibration instance has finished
    Or when the View Results button within the Camera Calibration Dialog Window is clicked
    Allows user to look at the pertinent calibration parameters and results
    """

    def __init__(self, parent=None, results=None):

        # Setup Dialog UI with CameraCalibration as parent and restore the previous window state
        super(CalibrationResults, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.window_settings = QSettings('MCAM', 'Defect Monitor')
        self.restoreGeometry(self.window_settings.value('geometry', '').toByteArray())

        # Split camera parameters into their own respective values to be used in OpenCV functions
        camera_matrix = np.array(results['CameraMatrix'])
        distortion_coefficients = np.array(results['DistortionCoefficients'])
        homography_matrix = np.array(results['HomographyMatrix'])

        # Nested for loops to access each of the table boxes in order
        for row in xrange(3):
            for column in xrange(3):

                # Setting the item using the corresponding index of the matrix arrays
                self.tableCameraMatrix.setItem(row, column, QTableWidgetItem(
                    format(camera_matrix[row][column], '.10g')))
                self.tableHomographyMatrix.setItem(row, column, QTableWidgetItem(
                    format(homography_matrix[row][column], '.10g')))

                # Because the distortion coefficients matrix is a 1x5, a slight modification needs to be made
                # Exception used to ignore the 2x3 box and 3rd row of the matrix
                if row >= 1: column += 3
                try:
                    self.tableDistortionCoefficients.setItem(row, column % 3, QTableWidgetItem(
                        format(distortion_coefficients[0][column], '.10g')))
                except (ValueError, IndexError):
                    pass

        # Displaying the re-projection error on the appropriate text label
        self.labelRMS.setText('Re-Projection Error: ' + format(results['RMS'], '.10g'))

    def closeEvent(self, event):
        """Executes when the window is closed"""
        self.window_settings.setValue('geometry', self.saveGeometry())
