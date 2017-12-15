# Import libraries and modules
import os
import cv2
import numpy as np
import json
from datetime import datetime
from validate_email import validate_email

# Import PyQt modules
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

# Import related modules
import slice_converter
import image_processing
import extra_functions
import camera_calibration
import qt_multithreading

# Import PyQt GUIs
from gui import dialogNewBuild, dialogPreferences, dialogCameraSettings, dialogCameraCalibration, \
    dialogCalibrationResults, dialogSliceConverter, dialogPartAdjustment, dialogImageConverter, dialogDefectReports


class NewBuild(QDialog, dialogNewBuild.Ui_dialogNewBuild):
    """Opens a Modal Dialog Window when File -> New... or File -> Open... or Tools -> Settings is clicked
    Allows the user to setup a new build and change settings
    """

    def __init__(self, parent=None, open_flag=False, settings_flag=False):

        # Setup Dialog UI with MainWindow as parent
        super(NewBuild, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)

        # Load from the build.json file
        with open('build.json') as build:
            self.build = json.load(build)

        # Load from the config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Flag to prevent additional image folders from being created
        self.open_flag = open_flag
        self.settings_flag = settings_flag

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        # Buttons
        self.pushBrowseIF.clicked.connect(self.browse_folder)
        self.pushSendTestEmail.clicked.connect(self.send_test_email)
        self.pushCreate.clicked.connect(self.create)

        # Lines
        self.lineBuildName.textChanged.connect(self.change_folder)
        self.lineEmailAddress.textChanged.connect(self.enable_button)

        # Set default placeholder text in some of the fields
        self.lineBuildName.setPlaceholderText(self.config['Defaults']['BuildName'])
        self.lineUsername.setPlaceholderText(self.config['Defaults']['Username'])
        self.lineEmailAddress.setPlaceholderText(self.config['Defaults']['EmailAddress'])

        # Set and display a default image folder name to save images for the current build
        # Generate a timestamp for folder labelling purposes
        time = datetime.now()
        self.image_folder = """%s/%s-%s-%s [%s''%s'%s]""" % \
                            (self.config['BuildFolder'], time.year, str(time.month).zfill(2), str(time.day).zfill(2),
                             str(time.hour).zfill(2), str(time.minute).zfill(2), str(time.second).zfill(2))
        self.change_folder()

        # If this dialog window was opened as a result of the Open... action, then the following is executed
        # Set and display the relevant names/values of the following text boxes as outlined in the opened config file
        if self.open_flag:
            self.setWindowTitle('Open Build')
            self.pushCreate.setText('Load')
            self.pushBrowseIF.setEnabled(False)
            self.lineBuildName.setText(self.build['BuildInfo']['Name'])
            self.lineBuildName.blockSignals(True)
            self.lineImageFolder.setText(self.build['BuildInfo']['Folder'])
            self.lineUsername.setText(self.build['BuildInfo']['Username'])
            self.lineEmailAddress.setText(self.build['BuildInfo']['EmailAddress'])
            self.checkMinor.setChecked(self.build['Notifications']['Minor'])
            self.checkMajor.setChecked(self.build['Notifications']['Major'])

        # If this dialog window was opened as a result of the Build Settings... action, then the following is executed
        # Disable a few of the buttons to disallow changing of the slice files and build folder
        if settings_flag:
            self.pushBrowseIF.setEnabled(False)
            self.setWindowTitle('Build Settings')
            self.pushCreate.setText('OK')

        self.threadpool = QThreadPool()

    def browse_folder(self):
        """Opens a File Dialog, allowing the user to select a folder to store the current build's image folder"""

        folder = QFileDialog.getExistingDirectory(self, 'Browse...', '')

        if folder:
            # Display just the folder name on the line box and disable the Build Name from changing the folder name
            self.lineImageFolder.setText(folder)
            self.lineBuildName.blockSignals(True)

    def change_folder(self):
        """Changes the prospective image folder name depending on the entered Build Name"""

        # Use the placeholder text if the user hasn't entered anything into the lineEdit
        if self.lineBuildName.text():
            self.lineImageFolder.setText('%s %s' % (self.image_folder, self.lineBuildName.text()))
        else:
            self.lineImageFolder.setText('%s %s' % (self.image_folder, self.lineBuildName.placeholderText()))

    def send_test_email(self):
        """Sends a test notification email to the entered email address"""

        # Open a message box with a send test email confirmation message so accidental emails don't get sent
        send_confirmation = QMessageBox(self)
        send_confirmation.setWindowTitle('Send Test Email')
        send_confirmation.setIcon(QMessageBox.Question)
        send_confirmation.setText('Are you sure you want to send a test email notification to %s?\n\n'
                                  'Note: This will save your entered Username and Email Address to the config file.' %
                                  self.lineEmailAddress.text())
        send_confirmation.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        retval = send_confirmation.exec_()

        # If the user clicked Yes
        if retval == 16384:
            if validate_email(self.lineEmailAddress.text()):
                # Disable the Send Test Email button to prevent SPAM and other buttons until the thread is finished
                self.pushSendTestEmail.setEnabled(False)
                self.pushCreate.setEnabled(False)
                self.pushCancel.setEnabled(False)

                # Save pertinent information that is required to send a notification email
                self.build['BuildInfo']['Username'] = self.lineUsername.text()
                self.build['BuildInfo']['EmailAddress'] = self.lineEmailAddress.text()
                if self.checkAddAttachment.isChecked():
                    self.build['Notifications']['Attachment'] = 'test_image.jpg'
                else:
                    self.build['Notifications']['Attachment'] = ''

                with open('build.json', 'w+') as build:
                    json.dump(self.build, build, indent=4, sort_keys=True)

                worker = qt_multithreading.Worker(extra_functions.Notifications().test_message)
                worker.signals.finished.connect(self.send_test_finished)
                self.threadpool.start(worker)
            else:
                # Opens a message box indicating that the entered email address is invalid
                invalid_email_error = QMessageBox(self)
                invalid_email_error.setWindowTitle('Error')
                invalid_email_error.setIcon(QMessageBox.Critical)
                invalid_email_error.setText('Invalid email address. Please enter a valid email address.')
                invalid_email_error.exec_()

    def send_test_finished(self):
        """Open a message box with a send test confirmation message"""

        self.pushCreate.setEnabled(True)
        self.pushCancel.setEnabled(True)

        send_test_confirmation = QMessageBox(self)
        send_test_confirmation.setWindowTitle('Send Test Email')
        send_test_confirmation.setIcon(QMessageBox.Information)
        send_test_confirmation.setText('An email notification has been sent to %s at %s.' %
                                       (self.lineEmailAddress.text(), self.lineUsername.text()))
        send_test_confirmation.exec_()

    def enable_button(self):
        """(Re-)Enables the Send Test Email button if the email address box is changed and not empty"""

        self.pushSendTestEmail.setEnabled(bool(self.lineEmailAddress.text()))
        self.checkAddAttachment.setEnabled(bool(self.lineEmailAddress.text()))

    def create(self):
        """Executes when the Create button is clicked
        First checks if all the required boxes have been filled, otherwise a MessageBox will be opened
        Saves important selection options to the config.json file and closes the window
        """

        # Save all the entered information to the config.json file
        # If the user didn't enter anything into the following fields, save the placeholder text instead
        if self.lineBuildName.text():
            self.build['BuildInfo']['Name'] = self.lineBuildName.text()
        else:
            self.build['BuildInfo']['Name'] = self.lineBuildName.placeholderText()

        if self.lineUsername.text():
            self.build['BuildInfo']['Username'] = self.lineUsername.text()
        else:
            self.build['BuildInfo']['Username'] = self.lineUsername.placeholderText()

        if self.lineEmailAddress.text():
            self.build['BuildInfo']['EmailAddress'] = self.lineEmailAddress.text()
        else:
            self.build['BuildInfo']['EmailAddress'] = self.lineEmailAddress.placeholderText()

        self.build['BuildInfo']['Machine'] = self.comboMachine.currentIndex()
        self.build['BuildInfo']['Camera'] = self.comboCamera.currentIndex()
        self.build['BuildInfo']['Folder'] = self.lineImageFolder.text()
        self.build['Notifications']['Minor'] = self.checkMinor.isChecked()
        self.build['Notifications']['Major'] = self.checkMajor.isChecked()

        # Save the selected platform dimensions to the config.json file
        if self.comboMachine.currentIndex() == 0:
            self.build['BuildInfo']['PlatformDimensions'] = [636, 406]

        # If a New Build is being created (rather than Open Build or Settings), create folders to store images
        if not self.open_flag and not self.settings_flag:
            # Save the created image folder's name to the build.json file
            self.build['BuildInfo']['Folder'] = self.lineImageFolder.text()

            # Create respective sub-directories for images (and reports)
            os.makedirs('%s/raw/coat' % self.lineImageFolder.text())
            os.makedirs('%s/raw/scan' % self.lineImageFolder.text())
            os.makedirs('%s/raw/snapshot' % self.lineImageFolder.text())
            os.makedirs('%s/fixed/coat' % self.lineImageFolder.text())
            os.makedirs('%s/fixed/scan' % self.lineImageFolder.text())
            os.makedirs('%s/fixed/snapshot' % self.lineImageFolder.text())
            os.makedirs('%s/defects/coat/streaks' % self.lineImageFolder.text())
            os.makedirs('%s/defects/coat/chatter' % self.lineImageFolder.text())
            os.makedirs('%s/defects/coat/patches' % self.lineImageFolder.text())
            os.makedirs('%s/defects/coat/outliers' % self.lineImageFolder.text())
            os.makedirs('%s/defects/scan/streaks' % self.lineImageFolder.text())
            os.makedirs('%s/defects/scan/chatter' % self.lineImageFolder.text())
            os.makedirs('%s/defects/scan/pattern' % self.lineImageFolder.text())
            os.makedirs('%s/contours' % self.lineImageFolder.text())
            os.makedirs('%s/reports' % self.lineImageFolder.text())

            # Create combined and background blank json reports and save them to the build reports folder
            with open('%s/reports/combined_report.json' % self.lineImageFolder.text(), 'w+') as report:
                json.dump(dict(), report)
            with open('%s/reports/background_report.json' % self.lineImageFolder.text(), 'w+') as report:
                json.dump(dict(), report)
        else:
            # Check if the folder containing the images exist if a build was opened
            if not os.path.isdir(self.build['BuildInfo']['Folder']):
                missing_folder_error = QMessageBox(self)
                missing_folder_error.setWindowTitle('Error')
                missing_folder_error.setIcon(QMessageBox.Critical)
                missing_folder_error.setText('Image folder not found.\n\nBuild cancelled.')
                missing_folder_error.exec_()

                # Close the New Build window, return to the Main Window and do nothing
                self.done(0)
                return

        with open('build.json', 'w+') as build:
            json.dump(self.build, build, indent=4, sort_keys=True)

        # Close the dialog window and return True
        self.done(1)


class Preferences(QDialog, dialogPreferences.Ui_dialogPreferences):
    """Opens a Modeless Dialog Window when Settings -> Preferences... is clicked
    Allows the user to change any settings in regard to the main interface"""

    def __init__(self, parent=None):

        # Setup Dialog UI with MainWindow as parent and restore the previous window state
        super(Preferences, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.window_settings = QSettings('MCAM', 'Defect Monitor')

        try:
            self.restoreGeometry(self.window_settings.value('Preferences Geometry', ''))
        except TypeError:
            pass

        with open('config.json') as config:
            self.config = json.load(config)

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        self.pushBrowseBF.clicked.connect(self.browse_folder)
        self.pushModify.clicked.connect(self.modify_gridlines)
        self.pushApply.clicked.connect(self.apply)

        # Set all settings to to previously saved values
        self.lineBuildFolder.setText(self.config['BuildFolder'])
        self.lineBuildName.setText(self.config['Defaults']['BuildName'])
        self.lineUsername.setText(self.config['Defaults']['Username'])
        self.lineEmailAddress.setText(self.config['Defaults']['EmailAddress'])
        self.spinSize.setValue(self.config['Gridlines']['Size'])
        self.spinThickness.setValue(self.config['Gridlines']['Thickness'])

        # Set the maximum range of the grid size spinbox
        self.spinSize.setMaximum(int(self.config['ImageCorrection']['ImageResolution'][0] / 2))
        self.spinSize.setToolTip('5 - %s' % int(self.config['ImageCorrection']['ImageResolution'][0] / 2))

        # Setup event listeners for all the setting boxes to detect a change in an entered value
        self.lineBuildFolder.textChanged.connect(self.apply_enable)
        self.spinSize.valueChanged.connect(self.apply_enable)
        self.spinThickness.valueChanged.connect(self.apply_enable)
        self.lineBuildName.textChanged.connect(self.apply_enable)
        self.lineUsername.textChanged.connect(self.apply_enable)
        self.lineEmailAddress.textChanged.connect(self.apply_enable)

    def browse_folder(self):
        """Opens a File Dialog, allowing the user to select a folder to store all the builds"""

        folder = QFileDialog.getExistingDirectory(self, 'Browse...', '')

        if folder:
            self.lineBuildFolder.setText(folder)

    def modify_gridlines(self):
        """Redraws the gridlines .png image with a new gridlines image using the updated settings"""

        # Grab the image resolution to be used for the gridlines
        width = self.config['ImageCorrection']['ImageResolution'][1]
        height = self.config['ImageCorrection']['ImageResolution'][0]

        size = self.spinSize.value()
        thickness = self.spinThickness.value()

        # Create a black image to draw the gridlines on
        image = np.zeros((height, width, 3), np.uint8)

        # Draw all the horizontal Lines
        for index in range(int(np.ceil(height / 2 / size))):
            cv2.line(image, (0, height // 2 + index * size), (width, height // 2 + index * size),
                     (255, 255, 255), thickness)
            cv2.line(image, (0, height // 2 - index * size), (width, height // 2 - index * size),
                     (255, 255, 255), thickness)

        # Draw all the vertical lines
        for index in range(int(np.ceil(width / 2 / size))):
            cv2.line(image, (width // 2 + index * size, 0), (width // 2 + index * size, height),
                     (255, 255, 255), thickness)
            cv2.line(image, (width // 2 - index * size, 0), (width // 2 - index * size, height),
                     (255, 255, 255), thickness)

        cv2.imwrite('gridlines.png', image)

        self.config['Gridlines']['Size'] = size
        self.config['Gridlines']['Thickness'] = thickness

        with open('config.json', 'w+') as config:
            json.dump(self.config, config, indent=4, sort_keys=True)

        # Open a confirmation message box to notify the user that the image has been modified
        modify_confirmation = QMessageBox(self)
        modify_confirmation.setWindowTitle('Modify Gridlines')
        modify_confirmation.setIcon(QMessageBox.Information)
        modify_confirmation.setText('Gridlines has been successfully modified to a grid size of <b>%s</b> pixels and a'
                                    ' line thickness of <b>%s</b>.' % (size, thickness))
        modify_confirmation.exec_()

    def apply_enable(self):
        """Enable the Apply button on any change of settings"""
        self.pushApply.setEnabled(True)

    def apply(self):
        """Executes when the Apply or OK button is clicked and saves the entered values to the config.json file"""

        with open('config.json') as config:
            self.config = json.load(config)

        # Save the new values from the changed settings to the config dictionary
        self.config['BuildFolder'] = self.lineBuildFolder.text()
        self.config['Defaults']['BuildName'] = self.lineBuildName.text()
        self.config['Defaults']['Username'] = self.lineUsername.text()
        self.config['Defaults']['EmailAddress'] = self.lineEmailAddress.text()

        with open('config.json', 'w+') as config:
            json.dump(self.config, config, indent=4, sort_keys=True)

        # Disable the Apply button until another setting is changed
        self.pushApply.setEnabled(False)

    def accept(self):
        """Executes when the OK button is pressed
        If the settings have changed, the apply function is executed before closing the window"""

        if self.pushApply.isEnabled():
            self.apply()

        self.closeEvent(self.close())

    def closeEvent(self, event):
        """Executes when the window is closed"""
        self.window_settings.setValue('Preferences Geometry', self.saveGeometry())


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

        try:
            self.restoreGeometry(self.window_settings.value('Camera Settings Geometry', ''))
        except TypeError:
            pass

        # Load from the config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        self.pushApply.clicked.connect(self.apply)

        # Set the combo box and settings to the previously saved values
        # Combo box settings are saved as their index values in the config.json file
        self.comboPixelFormat.setCurrentIndex(int(self.config['CameraSettings']['PixelFormat']))
        self.spinGain.setValue(self.config['CameraSettings']['Gain'])
        self.spinBlackLevel.setValue(self.config['CameraSettings']['BlackLevel'])
        self.spinExposureTime.setValue(int(self.config['CameraSettings']['ExposureTime']))
        self.spinPacketSize.setValue(int(self.config['CameraSettings']['PacketSize']))
        self.spinInterPacketDelay.setValue(int(self.config['CameraSettings']['InterPacketDelay']))
        self.spinFrameDelay.setValue(int(self.config['CameraSettings']['FrameDelay']))
        self.spinTriggerTimeout.setValue(int(self.config['CameraSettings']['TriggerTimeout']))

        # Setup event listeners for all the setting boxes to detect a change in an entered value
        self.comboPixelFormat.currentIndexChanged.connect(self.apply_enable)
        self.spinGain.valueChanged.connect(self.apply_enable)
        self.spinBlackLevel.valueChanged.connect(self.apply_enable)
        self.spinExposureTime.valueChanged.connect(self.apply_enable)
        self.spinPacketSize.valueChanged.connect(self.apply_enable)
        self.spinInterPacketDelay.valueChanged.connect(self.apply_enable)
        self.spinFrameDelay.valueChanged.connect(self.apply_enable)
        self.spinTriggerTimeout.valueChanged.connect(self.apply_enable)

    def apply_enable(self):
        """Enable the Apply button on any change of settings"""
        self.pushApply.setEnabled(True)

    def apply(self):
        """Executes when the Apply or OK button is clicked and saves the entered values to the config.json file"""

        with open('config.json') as config:
            self.config = json.load(config)

        # Save the new values from the changed settings to the config dictionary
        self.config['CameraSettings']['PixelFormat'] = self.comboPixelFormat.currentIndex()
        self.config['CameraSettings']['Gain'] = self.spinGain.value()
        self.config['CameraSettings']['BlackLevel'] = self.spinBlackLevel.value()
        self.config['CameraSettings']['ExposureTime'] = self.spinExposureTime.value()
        self.config['CameraSettings']['PacketSize'] = self.spinPacketSize.value()
        self.config['CameraSettings']['InterPacketDelay'] = self.spinInterPacketDelay.value()
        self.config['CameraSettings']['FrameTransmissionDelay'] = self.spinFrameDelay.value()
        self.config['CameraSettings']['TriggerTimeout'] = self.spinTriggerTimeout.value()

        with open('config.json', 'w+') as config:
            json.dump(self.config, config, indent=4, sort_keys=True)

        # Disable the Apply button until another setting is changed
        self.pushApply.setEnabled(False)

    def accept(self):
        """Executes when the OK button is pressed
        If the settings have changed, the apply function is executed before closing the window"""

        if self.pushApply.isEnabled():
            self.apply()

        self.closeEvent(self.close())

    def closeEvent(self, event):
        """Executes when the window is closed or the Cancel button is clicked
        Doesn't save any changed settings at all"""

        self.window_settings.setValue('Camera Settings Geometry', self.saveGeometry())


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

        # Restoring the window state needs to go into a try loop as the first time the program is run on a new system
        # There won't be any stored settings and the function throws a TypeError
        try:
            self.restoreGeometry(self.window_settings.value('Camera Calibration Geometry', ''))
        except TypeError:
            pass

        with open('config.json') as config:
            self.config = json.load(config)

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        self.pushBrowseF.clicked.connect(self.browse_folder)
        self.pushBrowseHI.clicked.connect(self.browse_homography)
        self.pushBrowseTI.clicked.connect(self.browse_test_image)
        self.pushStart.clicked.connect(self.start)
        self.pushResults.clicked.connect(self.view_results)
        self.pushSave.clicked.connect(self.save_results)
        self.lineTestImage.textChanged.connect(self.enable_checkbox)

        # Set the SpinBox settings to the previously saved values
        self.spinWidth.setValue(self.config['CameraCalibration']['Width'])
        self.spinHeight.setValue(self.config['CameraCalibration']['Height'])
        self.spinRatio.setValue(self.config['CameraCalibration']['DownscalingRatio'])

        # Set and display previously saved image path names if they exist, else leave empty strings
        if os.path.isfile(self.config['CameraCalibration']['HomographyImage']):
            self.lineHomographyImage.setText(os.path.basename(self.config['CameraCalibration']['HomographyImage']))
        if os.path.isfile(self.config['CameraCalibration']['TestImage']):
            self.lineTestImage.setText(os.path.basename(self.config['CameraCalibration']['TestImage']))

        self.threadpool = QThreadPool()

    def browse_folder(self):
        """Opens a File Dialog, allowing the user to select a folder containing calibration images"""

        folder = QFileDialog.getExistingDirectory(self, 'Browse...', '')

        # Checks if a folder is actually selected or if the user clicked cancel
        if folder:
            # Save the selected folder to the config dictionary
            self.config['CameraCalibration']['Folder'] = folder

            # Display the folder name on the respective QLineEdit
            self.lineCalibrationFolder.setText(folder)

            # Empty the image QListWidget and the image list
            self.listImages.clear()
            self.image_list = list()

            # Grab the list of images in the selected folder and store them if the name contains 'calibration_image'
            for image_name in os.listdir(folder):
                if 'image_calibration' in image_name:
                    self.image_list.append(image_name)

            # Check if certain conditions are met to enable the Start button
            self.enable_button()

            # Check if the image list contains any valid images
            if self.image_list:
                # Remove previous entries and fill with new entries
                self.listImages.addItems(self.image_list)
            else:
                self.update_status('No calibration images found.')
                self.update_progress(0)

    def browse_homography(self):
        """Opens a File Dialog, allowing the user to select an homography image to calculate the homography matrix"""

        filename = QFileDialog.getOpenFileName(self, 'Browse...', '', 'Image File (*.png)')[0]

        if filename:
            self.config['CameraCalibration']['HomographyImage'] = filename
            self.lineHomographyImage.setText(os.path.basename(self.config['CameraCalibration']['HomographyImage']))

    def browse_test_image(self):
        """Opens a File Dialog, allowing the user to select a test image used to test calibration results"""

        filename = QFileDialog.getOpenFileName(self, 'Browse...', '', 'Image File (*.png)')[0]

        if filename:
            self.config['CameraCalibration']['TestImage'] = filename
            self.lineTestImage.setText(os.path.basename(self.config['CameraCalibration']['TestImage']))

    def start(self):
        """Executes when the Start Calibration button is clicked
        Starts the calibration process after saving the calibration settings to config.json file
        """

        # Enable or disable relevant UI elements to prevent concurrent processes
        self.pushBrowseF.setEnabled(False)
        self.pushBrowseHI.setEnabled(False)
        self.pushBrowseTI.setEnabled(False)
        self.pushStart.setEnabled(False)
        self.pushDone.setEnabled(False)

        # This setting is exempt from the other settings as by default, this setting should be False
        self.config['CameraCalibration']['Apply'] = self.checkApply.isChecked()

        # Save calibration settings
        self.apply_settings()

        # Reset the colours of the items in the list widget
        # Try exception causes this function to be skipped the first time
        try:
            for index in range(self.listImages.count()):
                self.listImages.item(index).setBackground(QColor('white'))
        except AttributeError:
            pass

        worker = qt_multithreading.Worker(camera_calibration.Calibration().calibrate)
        worker.signals.status.connect(self.update_status)
        worker.signals.progress.connect(self.update_progress)
        worker.signals.colour.connect(self.change_colour)
        worker.signals.finished.connect(self.start_finished)
        self.threadpool.start(worker)

    def start_finished(self):
        """Executes when the CameraCalibration instance has finished"""

        # Opens a Dialog Window to view Calibration Results
        self.view_results(True)

        # Save calibration settings to the config.json file
        self.apply_settings()

        # Enable or disable relevant UI elements to prevent concurrent processes
        self.pushBrowseF.setEnabled(True)
        self.pushBrowseHI.setEnabled(True)
        self.pushBrowseTI.setEnabled(True)
        self.pushStart.setEnabled(True)
        self.pushSave.setEnabled(True)
        self.pushDone.setEnabled(True)

    def view_results(self, calibration_flag=False):
        """Opens a Dialog Window when the CameraCalibration instance has finished
        Or when the View Results button is clicked
        Displays the results of the camera calibration to the user
        """

        if calibration_flag:
            with open('calibration_results.json') as file:
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
        """Copies the calibration results from the temporary calibration_results.json file to the config.json file"""

        # Load the results from the temporary calibration_results.json file
        with open('calibration_results.json') as file:
            results = json.load(file)

        # Delete the calibration_results.json file
        os.remove('calibration_results.json')

        # Copy the results dictionary into the config dictionary
        self.config.update(results)

        # Save to the config.json file and disable saving again
        self.apply_settings()
        self.pushSave.setEnabled(False)
        self.update_status('Calibration results saved to the config file.')

    def change_colour(self, index, valid):
        """Changes the background colour of the received item in the listImages box
        Changes to green if image is valid, red if image is invalid for calibration
        """

        if valid:
            self.listImages.item(index).setBackground(QColor('green'))
        else:
            self.listImages.item(index).setBackground(QColor('red'))

    def enable_checkbox(self):
        """(Re-)Enables the Apply to Test Image checkbox if a test image has been selected"""

        if self.lineTestImage.text():
            self.checkApply.setEnabled(True)
        else:
            self.checkApply.setEnabled(False)
            self.checkApply.setChecked(False)

    def enable_button(self):
        """(Re-)Enables the Start button if valid calibration images and an homography image have been selected"""

        if self.image_list and self.lineHomographyImage.text():
            self.update_status('Waiting to start process.')
            self.pushStart.setEnabled(True)
        else:
            self.pushStart.setEnabled(False)

    def apply_settings(self):
        """Grab the spinxBox and checkBox values and save them to the working config and default config file"""

        with open('config.json') as config:
            self.config = json.load(config)

        self.config['CameraCalibration']['Width'] = self.spinWidth.value()
        self.config['CameraCalibration']['Height'] = self.spinHeight.value()
        self.config['CameraCalibration']['DownscalingRatio'] = self.spinRatio.value()
        self.config['CameraCalibration']['Chessboard'] = self.checkSaveC.isChecked()
        self.config['CameraCalibration']['Undistort'] = self.checkSaveU.isChecked()
        self.config['CameraCalibration']['Apply'] = self.checkApply.isChecked()

        with open('config.json', 'w+') as config:
            json.dump(self.config, config, indent=4, sort_keys=True)

    def update_status(self, string):
        self.labelStatus.setText(string)

    def update_progress(self, percentage):
        self.progressBar.setValue(int(percentage))

    def closeEvent(self, event):
        """Executes when the Done button is clicked or when the window is closed"""

        # Save settings so that settings persist across instances
        self.apply_settings()

        # Remove the calibration_results.json file if it exists
        if os.path.isfile('calibration_results.json'):
            os.remove('calibration_results.json')

        # Save the current position of the Dialog Window before the window is closed
        self.window_settings.setValue('Camera Calibration Geometry', self.saveGeometry())


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

        try:
            self.restoreGeometry(self.window_settings.value('Calibration Results Geometry', ''))
        except TypeError:
            pass

        # Split camera parameters into their own respective values to be used in OpenCV functions
        camera_matrix = np.array(results['CameraMatrix'])
        distortion_coefficients = np.array(results['DistortionCoefficients'])
        homography_matrix = np.array(results['HomographyMatrix'])

        # Sets the tables' columns and rows to automatically resize appropriately
        self.tableCM.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableDC.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableHM.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableCM.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableDC.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableHM.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Nested for loops to access each of the table boxes in order
        for row in range(3):
            for column in range(3):
                # Setting the item using the corresponding index of the matrix arrays
                self.tableCM.setItem(row, column, QTableWidgetItem(format(camera_matrix[row][column], '.10g')))
                self.tableHM.setItem(row, column, QTableWidgetItem(format(homography_matrix[row][column], '.10g')))

                # Because the distortion coefficients matrix is a 1x5, a slight modification needs to be made
                # Exception used to ignore the 2x3 box and 3rd row of the matrix
                if row >= 1:
                    column += 3
                try:
                    self.tableDC.setItem(row, column % 3, QTableWidgetItem(
                        format(distortion_coefficients[0][column], '.10g')))
                except (ValueError, IndexError):
                    pass

        # Sets the row height to as small as possible to fit the text height
        self.tableCM.resizeRowsToContents()
        self.tableDC.resizeRowsToContents()
        self.tableHM.resizeRowsToContents()

        # Displaying the re-projection error on the appropriate text label
        self.labelRMS.setText('Re-Projection Error: ' + format(results['RMS'], '.10g'))

    def closeEvent(self, event):
        """Executes when the window is closed"""
        self.window_settings.setValue('Calibration Results Geometry', self.saveGeometry())


class SliceConverter(QDialog, dialogSliceConverter.Ui_dialogSliceConverter):

    def __init__(self, parent=None):

        super(SliceConverter, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(Qt.Window)
        self.setupUi(self)
        self.window_settings = QSettings('MCAM', 'Defect Monitor')

        try:
            self.restoreGeometry(self.window_settings.value('Slice Converter Geometry', ''))
        except TypeError:
            pass

        with open('build.json') as build:
            self.build = json.load(build)

        with open('config.json') as config:
            self.config = json.load(config)

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        # Buttons
        self.pushAddSF.clicked.connect(self.add_files)
        self.pushRemoveSF.clicked.connect(self.remove_files)
        self.pushDrawContours.clicked.connect(self.draw_setup)
        self.pushZoomIn.clicked.connect(self.zoom_in)
        self.pushZoomOut.clicked.connect(self.zoom_out)
        self.pushGoSlice.clicked.connect(self.set_slice)
        self.pushGoHeight.clicked.connect(self.set_height)
        self.pushRotate.clicked.connect(self.rotate)
        self.pushResetR.clicked.connect(self.rotate_reset)
        self.pushTranslate.clicked.connect(self.translate)
        self.pushResetT.clicked.connect(self.translate_reset)
        self.pushPause.clicked.connect(self.pause)
        self.pushBrowseCB.clicked.connect(self.browse_background)
        self.pushBrowseOF.clicked.connect(self.browse_output)

        # Checkboxes
        self.checkCentrelines.toggled.connect(self.update_display)
        self.checkFillContours.toggled.connect(self.preview_contours)
        self.checkBackground.toggled.connect(self.set_background)

        self.listSliceFiles.itemSelectionChanged.connect(self.select_parts)
        self.graphicsDisplay.mouse_pos.connect(self.update_position)
        self.graphicsDisplay.zoom_done.connect(self.zoom_in_finished)

        self.contour_dict = dict()
        self.slice_list = list()
        self.current_layer = 1
        self.convert_run_flag = False
        self.draw_run_flag = False

        # This value is used to indicate which process is active, used for the pause button
        # 0 - None / 1 - Convert / 2 - Draw
        self.active_process = 0

        # Check if a build is open by checking for an image folder, otherwise set a 'default' output folder
        if self.build['BuildInfo']['Folder']:
            self.output_folder = self.build['BuildInfo']['Folder'] + '/contours'
            self.slice_list = self.build['SliceConverter']['Files'][:]
        else:
            self.output_folder = os.path.dirname(os.getcwd().replace('\\', '/')) + '/Contours'

        self.lineOutputFolder.setText(self.output_folder)

        # Set up the display with a 'blank' platform
        self.preview_contours()

        self.threadpool = QThreadPool()

    def add_files(self):
        """Adds slice files to the slice file list
        Subsequently converts all not yet converted .cli files into ASCII contours"""

        filenames = QFileDialog.getOpenFileNames(self, 'Add Slice Files...', '', 'Slice Files (*.cli)')[0]

        if filenames:
            # Check if any of the selected files are already in the slice list and only add the ones which aren't
            for file in filenames:
                if file not in self.slice_list:
                    self.slice_list.append(file)

            self.check_files()

    def check_files(self):
        """Checks whether all the selected slice files have been converted from .cli into ASCII contours
        Subsequently converts the files that haven't been converted
        Also adds the slice files to the listWidget and assigns a part colour to each part"""

        # Stop the selecting of files in the list from doing anything
        self.listSliceFiles.blockSignals(True)

        # Sort the slice list and clear the QListWidget
        self.slice_list.sort()
        self.listSliceFiles.clear()

        # Initialize a few lists and values
        # Part names is a dictionary of the names without the directory part and their corresponding preview part colour
        # Part colours is same as above except with the part colours that will be used to draw the respective contours
        self.part_names = dict()
        self.part_colours = dict()
        self.index_list = list()
        self.slice_counter = 0
        self.max_layers = 1

        # Add the slice files to the listWidget while checking if the .cli files have been converted
        for index, item in enumerate(self.slice_list):
            # Set all the preview part colours to black for now
            self.part_names[os.path.basename(item).replace('.cli', '')] = (255, 0, 0)
            # self.part_colours
            self.listSliceFiles.addItem(os.path.basename(item).replace('.cli', ''))
            if os.path.isfile(item.replace('.cli', '_contours.txt')):
                self.listSliceFiles.item(index).setBackground(QColor('yellow'))
            else:
                self.index_list.append(index)
                self.listSliceFiles.item(index).setBackground(QColor('red'))

        # Check if any of the slice files need to be converted at all
        if self.index_list:
            # Disable all the buttons to prevent the user from doing concurrent things
            self.toggle_control(1)
            self.convert_run_flag = True

            self.convert_slice(self.slice_list[self.index_list[self.slice_counter]])
        else:
            self.update_layer_ranges()
            self.preview_contours()
            self.pushDrawContours.setEnabled(True)

    def remove_files(self):
        """Removes slice files from the slice file list"""

        # Stop the selecting of files in the list from doing anything
        self.listSliceFiles.blockSignals(True)

        # Grab the list of selected items in the QListWidget
        for item in self.listSliceFiles.selectedItems():
            # Delete the corresponding file from both slice file lists using the row index of the file
            del self.slice_list[self.listSliceFiles.row(item)]
            self.part_names.pop(item.text(), None)
            self.listSliceFiles.takeItem(self.listSliceFiles.row(item))

        # Check if the list is now empty, if so reset to button state 0
        if not self.slice_list:
            self.contour_dict = dict()
            self.graphicsDisplay.reset_image()
            self.toggle_control(0)

        self.update_layer_ranges()
        self.preview_contours()

    def convert_slice(self, slice_file):

        self.active_process = 1

        worker = qt_multithreading.Worker(slice_converter.SliceConverter().convert_cli, slice_file)
        worker.signals.status.connect(self.update_status)
        worker.signals.progress.connect(self.update_progress)
        worker.signals.finished.connect(self.convert_slice_finished)
        self.threadpool.start(worker)

    def convert_slice_finished(self):

        self.listSliceFiles.item(self.index_list[self.slice_counter]).setBackground(QColor('yellow'))
        self.slice_counter += 1

        if self.convert_run_flag and not self.slice_counter == len(self.index_list):
            self.convert_slice(self.slice_list[self.index_list[self.slice_counter]])
        elif self.slice_counter == len(self.index_list):
            self.pushDrawContours.setEnabled(True)
            self.update_layer_ranges()
            self.preview_contours()

    def preview_contours(self):
        """Draws a 'preview' of the selected layer's contours"""

        self.image_contours = np.zeros(tuple(self.config['ImageCorrection']['ImageResolution'] + [3]), np.uint8)

        # Change whether to draw on a black or white background depending on if the background checkbox is checked
        if not self.checkBackground.isChecked():
            self.image_contours[:] = (255, 255, 255)
            # Draw boundary lines around the rectangle which should represent the platform edges (currently doesn't)
            cv2.rectangle(self.image_contours, (0, 0), (3470, 2410), (0, 0, 0), 5)

        if self.checkFillContours.isChecked():
            thickness = -1
        else:
            thickness = 3

        if self.contour_dict:
            for part_name, contour_list in self.contour_dict.items():
                try:
                    contour_string = contour_list[self.current_layer].split('C,')[1::]
                except IndexError:
                    continue

                contours = list()

                for string in contour_string:
                    vectors = string.split(',')[:-1]
                    contours.append(np.array(vectors).reshape(1, len(vectors) // 2, 2).astype(np.int32))

                cv2.drawContours(self.image_contours, contours, -1, self.part_names[part_name],
                                 offset=tuple(self.config['ImageCorrection']['Offset']), thickness=thickness)

            self.image_contours = cv2.flip(self.image_contours, 0)

        self.update_display()

    def select_parts(self):

        # Reset the colours of all the parts back to blue
        for key in self.part_names.keys():
            self.part_names[key] = (255, 0, 0)

        # Change the selected item colours to green and re-draw the contours
        for item in self.listSliceFiles.selectedItems():
            # Change the part colour of the selected item to green
            self.part_names[item.text()] = (0, 255, 0)

        self.preview_contours()

    def zoom_in(self):
        """Sets the display Graphics Viewer's zoom function on"""
        self.graphicsDisplay.zoom_flag = self.pushZoomIn.isChecked()

    def zoom_in_finished(self):
        """Disables the checked status of the Zoom In action after successfully performing a zoom action"""
        self.pushZoomIn.setChecked(False)
        self.graphicsDisplay.zoom_flag = False

    def zoom_out(self):
        """Resets the zoom state of the display Graphics Viewer"""
        self.graphicsDisplay.reset_image()

    def set_slice(self):
        self.current_layer = self.spinSliceNumber.value()
        self.labelSliceNumber.setText('%s / %s' % (str(self.current_layer).zfill(4), str(self.max_layers).zfill(4)))
        self.preview_contours()

    def set_height(self):
        pass

    def rotate(self):
        pass

    def rotate_reset(self):
        pass

    def translate(self):
        pass

    def translate_reset(self):
        pass

    def draw_setup(self):

        """If the output folder is set to the build's contours folder, show a warning before proceeding"""
        if self.output_folder == self.build['BuildInfo']['Folder']:
            draw_confirmation = QMessageBox(self)
            draw_confirmation.setWindowTitle('Draw Contours')
            draw_confirmation.setIcon(QMessageBox.Warning)
            draw_confirmation.setText('Saving drawn contours to the build folder.\n\n'
                                      'Note that this will completely empty the build\'s contours folder and remove '
                                      'all of the individual part reports. Part by part defect data will need to be '
                                      're-calculated after re-drawing all the contours, but the combined report will '
                                      'remain untouched.\n\n'
                                      'Would you like to proceed to draw contours?')
            draw_confirmation.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            retval = draw_confirmation.exec_()

            # If the user clicked No, the method will end, otherwise it continues
            if retval == 16384:
                # Delete all the files in the build's contours folder
                for filename in os.listdir(self.output_folder):
                    os.remove(self.output_folder + '/' + filename)

                # Check the new slice file list against the old slice file list for files that can be deleted
                for filename in list(set(self.build['SliceConverter']['Files']) - set(self.slice_list)):

                    os.remove('%s/reports/%s_report.json' % (self.build['BuildInfo']['Folder'],
                                                             os.path.splitext(os.path.basename(filename))[0]))
            else:
                return

        # Create the output folder if it doesn't already exist
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        # UI Progress
        self.progress_current = 0.0
        self.progress_previous = None
        self.update_progress(0)
        self.increment = 100 / (self.spinRangeHigh.value() + 1 - self.spinRangeLow.value())

        # Create a dictionary of colours (different shades of teal) for each part's contours and save it
        # These part colours don't affect past reports
        # At the same time, save a bunch of json files containing an empty dictionary to the build reports folder
        # These json files are used to store the defect coordinate and pixel size data for each of the parts
        part_colours = dict()

        for index, part_name in enumerate(self.part_names.keys()):
            # Create the colours for each of the parts
            part_colours[part_name] = ((100 + index) % 255, (100 + index) % 255, 0)

            if self.output_folder == self.build['BuildInfo']['Folder']:
                if not os.path.isfile('%s/reports/%s_report.json' % (self.build['BuildInfo']['Folder'], part_name)):
                    with open('%s/reports/%s_report.json' % (self.build['BuildInfo']['Folder'], part_name), 'w+') as report:
                        json.dump(dict(), report)

        # Set the 'background' part colour to black
        part_colours['background'] = (0, 0, 0)

        # Save the Slice File and Part Colours lists to the build.json file
        self.build['SliceConverter']['Files'] = self.slice_list
        self.build['SliceConverter']['PartColours'] = part_colours

        # Set the starting layer to draw as the entered lower layer range (default is all the contours)
        self.contour_counter = self.spinRangeLow.value()
        self.draw_run_flag = True

        # Start the draw loop
        self.draw_contours(self.contour_counter, True)

    def draw_contours(self, layer, names_flag=False):

        self.active_process = 2
        self.update_status('All | Drawing %s of %s.' % (str(layer).zfill(4), str(self.spinRangeHigh.value()).zfill(4)))

        worker = qt_multithreading.Worker(slice_converter.SliceConverter().draw_contour, self.contour_dict, layer,
                                          self.build['SliceConverter']['PartColours'], 0, self.output_folder,
                                          names_flag)
        worker.signals.finished.connect(self.draw_contours_finished)
        self.threadpool.start(worker)

    def draw_contours_finished(self):

        self.contour_counter += 1

        self.progress_current += self.increment
        if round(self.progress_current) is not self.progress_previous:
            self.update_progress(round(self.progress_current))
            self.progress_previous = round(self.progress_current)

        if self.draw_run_flag and not self.contour_counter == (self.spinRangeHigh.value() + 1):
            self.draw_contours(self.contour_counter)
        elif self.contour_counter == (self.spinRangeHigh.value() + 1):
            pass

    def set_background(self):
        if self.checkBackground.isChecked():
            if not self.lineBackground.text():
                if not self.browse_background():
                    self.checkBackground.setChecked(False)
            else:
                self.preview_contours()
        else:
            self.preview_contours()

    def browse_background(self):
        """Opens a File Dialog, allowing the user to select an image to be used as the background"""

        filename = QFileDialog.getOpenFileName(self, 'Browse...', '', 'Image Files (*.png)')[0]

        if filename:
            self.image_background = cv2.imread(filename)
            self.lineBackground.setText(filename)
            self.preview_contours()
            return True
        else:
            return False

    def pause(self):
        """Executes when the Paused/Resume button is pressed
        Pauses or resumes either the slice conversion or the contour drawing loops"""

        if 'Pause' in self.pushPause.text():
            self.pushPause.setText('Resume')
            if self.active_process == 1:
                self.convert_run_flag = False
            elif self.active_process == 2:
                self.draw_run_flag = False

        elif 'Resume' in self.pushPause.text():
            self.pushResume.setText('Pause')
            if self.active_process == 1:
                self.convert_run_flag = True
                self.convert_slice(self.slice_list[self.index_list[self.slice_counter]])
            elif self.active_process == 2:
                self.draw_run_flag = True
                self.draw_contours(self.contour_counter)

    def browse_output(self):
        """Opens a File Dialog, allowing the user to select a folder to save the drawn contours to"""

        folder = QFileDialog.getExistingDirectory(self, 'Browse...', '')

        if folder:
            self.output_folder = folder
            self.lineFolder.setText(self.output_folder)

    def toggle_control(self, state):
        """Enables or disables the following buttons in one fell swoop depending on the received state"""

        # State 0 - No files added
        if state == 0:
            self.pushAddSF.setEnabled(True)
            self.pushRemoveSF.setEnabled(True)
            self.frameDisplayControl.setEnabled(False)
            self.groupDisplayOptions.setEnabled(False)
            self.groupDrawRange.setEnabled(False)
            self.groupRotation.setEnabled(False)
            self.groupTranslation.setEnabled(False)
            self.pushBrowseOF.setEnabled(True)
            self.pushPause.setEnabled(False)
        # State 1 - Files in the middle of being converted
        elif state == 1:
            self.pushAddSF.setEnabled(False)
            self.pushRemoveSF.setEnabled(False)
            self.frameDisplayControl.setEnabled(False)
            self.groupDisplayOptions.setEnabled(False)
            self.groupDrawRange.setEnabled(False)
            self.groupRotation.setEnabled(False)
            self.groupTranslation.setEnabled(False)
            self.pushBrowseOF.setEnabled(False)
            self.pushPause.setEnabled(True)
        # State 2 - Files added, contour preview successfully displayed
        elif state == 2:
            self.pushAddSF.setEnabled(True)
            self.pushRemoveSF.setEnabled(True)
            self.frameDisplayControl.setEnabled(True)
            self.groupDisplayOptions.setEnabled(True)
            self.groupDrawRange.setEnabled(True)
            self.groupRotation.setEnabled(True)
            self.groupTranslation.setEnabled(True)
            self.pushBrowseOF.setEnabled(True)
            self.pushPause.setEnabled(False)

    def update_display(self):

        # Make a copy of the contour image so that it remains unmodified by the below operations
        image = self.image_contours.copy()

        if self.checkBackground.isChecked():
            image = cv2.add(self.image_background, image)

        if self.checkCentrelines.isChecked():
            cv2.line(image, (0, 1205), (3470, 1205), (0, 0, 0), 3)
            cv2.line(image, (1735, 0), (1735, 2410), (0, 0, 0), 3)

        self.graphicsDisplay.set_image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        self.toggle_control(2)

        # Allow the selection of files in the list from doing things
        self.listSliceFiles.blockSignals(False)

    def update_layer_ranges(self):
        """Updates all parts of the dialog window UI that involves the maximum number of layers"""

        self.update_status('All | Loading contours...')

        self.contour_dict = dict()

        # Load all the contours into memory and save them to a dictionary
        for index, filename in enumerate(self.slice_list):
            with open(filename.replace('.cli', '_contours.txt')) as contour_file:
                self.contour_dict[list(self.part_names.keys())[index]] = contour_file.readlines()

        self.max_layers = 0
        self.slice_height = 0.000

        # Find the max number of layers and the layer thickness from the first and third line in the contours file
        for contours in self.contour_dict.values():
            if int(contours[0]) > self.max_layers:
                self.max_layers = int(contours[0])
            slice_height = float(contours[2].split('C,')[0])

        self.labelSliceNumber.setText('%s / %s' % (str(self.current_layer).zfill(4), str(self.max_layers).zfill(4)))
        self.doubleSliceHeight.setSingleStep(slice_height)
        self.spinRangeHigh.setMaximum(self.max_layers)
        self.spinRangeHigh.setValue(self.max_layers)

        self.update_status('All | Contours loaded.')

    def update_position(self, x, y):
        """Displays the relative position of the mouse cursor over the Layer Preview graphics view"""
        self.labelXPosition.setText('X     ' + str(x).zfill(4) + ' px')
        self.labelYPosition.setText('Y     ' + str(y).zfill(4) + ' px')

    def update_status(self, string):
        string = string.split(' | ')
        self.labelStatus.setText(string[1])
        self.labelStatusPart.setText(string[0])

    def update_progress(self, percentage):
        self.progressBar.setValue(percentage)

    def closeEvent(self, event):
        self.window_settings.setValue('Slice Converter Geometry', self.saveGeometry())


class PartAdjustment(QDialog, dialogPartAdjustment.Ui_dialogPartAdjustment):
    """Opens a Modeless Dialog Window when the Part Adjustment button is clicked
    Or when Tools -> Part Adjustment is clicked
    Allows the user to adjust and transform the part contour overlay image in a variety of ways
    """

    # Signal that will be emitted anytime one of the transformation buttons is pressed
    update_part = pyqtSignal(bool)

    def __init__(self, parent=None):

        # Setup Dialog UI with MainWindow as parent and restore the previous window state
        super(PartAdjustment, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.window_settings = QSettings('MCAM', 'Defect Monitor')

        try:
            self.restoreGeometry(self.window_settings.value('Part Adjustment Geometry', ''))
        except TypeError:
            pass

        with open('config.json') as config:
            self.config = json.load(config)

        # Create two copies of the display transform parameters, one used to reset back to
        self.transform = self.config['ImageCorrection']['TransformDisplay'].copy()
        self.transform_reset = self.config['ImageCorrection']['TransformDisplay'].copy()
        self.states = list()

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        # General
        self.pushReset.clicked.connect(self.reset)
        self.pushUndo.clicked.connect(self.undo)
        self.pushSave.clicked.connect(self.save)

        # Translation
        self.pushTranslateUp.clicked.connect(self.translate_up)
        self.pushTranslateDown.clicked.connect(self.translate_down)
        self.pushTranslateLeft.clicked.connect(self.translate_left)
        self.pushTranslateRight.clicked.connect(self.translate_right)

        # Rotation / Flip
        self.pushRotateACW.clicked.connect(self.rotate_acw)
        self.pushRotateCW.clicked.connect(self.rotate_cw)
        self.pushFlipHorizontal.clicked.connect(self.flip_horizontal)
        self.pushFlipVertical.clicked.connect(self.flip_vertical)

        # Stretch / Pull
        self.pushResetStretch.clicked.connect(self.stretch_reset)
        self.pushStretchN.clicked.connect(self.stretch_n)
        self.pushStretchNE.clicked.connect(self.stretch_ne)
        self.pushStretchE.clicked.connect(self.stretch_e)
        self.pushStretchSE.clicked.connect(self.stretch_se)
        self.pushStretchS.clicked.connect(self.stretch_s)
        self.pushStretchSW.clicked.connect(self.stretch_sw)
        self.pushStretchW.clicked.connect(self.stretch_w)
        self.pushStretchNW.clicked.connect(self.stretch_nw)

        self.pushStretchUpLeft.clicked.connect(self.stretch_ul)
        self.pushStretchLeftUp.clicked.connect(self.stretch_lu)
        self.pushStretchUpRight.clicked.connect(self.stretch_ur)
        self.pushStretchRightUp.clicked.connect(self.stretch_ru)
        self.pushStretchDownLeft.clicked.connect(self.stretch_dl)
        self.pushStretchLeftDown.clicked.connect(self.stretch_ld)
        self.pushStretchDownRight.clicked.connect(self.stretch_dr)
        self.pushStretchRightDown.clicked.connect(self.stretch_rd)

    def reset(self):
        self.transform = self.transform_reset.copy()
        self.apply()

    def undo(self):
        del self.states[-1]
        self.transform = self.states[-1]
        self.apply(True)

    def translate_up(self):
        self.transform[0] -= self.spinPixels.value()
        self.apply()

    def translate_down(self):
        self.transform[0] += self.spinPixels.value()
        self.apply()

    def translate_left(self):
        self.transform[1] -= self.spinPixels.value()
        self.apply()

    def translate_right(self):
        self.transform[1] += self.spinPixels.value()
        self.apply()

    def rotate_acw(self):
        self.transform[2] += self.spinDegrees.value()
        self.apply()

    def rotate_cw(self):
        self.transform[2] -= self.spinDegrees.value()
        self.apply()

    def flip_horizontal(self):
        self.transform[3] ^= 1
        self.apply()

    def flip_vertical(self):
        self.transform[4] ^= 1
        self.apply()

    def stretch_reset(self):
        self.transform[5:] = [0] * (len(self.transform) - 5)
        self.apply()

    def stretch_n(self):
        self.transform[5] -= self.spinPixels.value()
        self.apply()

    def stretch_ne(self):
        self.transform[5] -= self.spinPixels.value()
        self.transform[6] += self.spinPixels.value()
        self.apply()

    def stretch_e(self):
        self.transform[6] += self.spinPixels.value()
        self.apply()

    def stretch_se(self):
        self.transform[7] += self.spinPixels.value()
        self.transform[6] += self.spinPixels.value()
        self.apply()

    def stretch_s(self):
        self.transform[7] += self.spinPixels.value()
        self.apply()

    def stretch_sw(self):
        self.transform[7] += self.spinPixels.value()
        self.transform[8] -= self.spinPixels.value()
        self.apply()

    def stretch_w(self):
        self.transform[8] -= self.spinPixels.value()
        self.apply()

    def stretch_nw(self):
        self.transform[5] -= self.spinPixels.value()
        self.transform[8] -= self.spinPixels.value()
        self.apply()

    def stretch_ul(self):
        self.transform[9] -= self.spinPixels.value()
        self.apply()

    def stretch_lu(self):
        self.transform[10] -= self.spinPixels.value()
        self.apply()

    def stretch_ur(self):
        self.transform[11] += self.spinPixels.value()
        self.apply()

    def stretch_ru(self):
        self.transform[12] -= self.spinPixels.value()
        self.apply()

    def stretch_dl(self):
        self.transform[13] -= self.spinPixels.value()
        self.apply()

    def stretch_ld(self):
        self.transform[14] += self.spinPixels.value()
        self.apply()

    def stretch_dr(self):
        self.transform[15] += self.spinPixels.value()
        self.apply()

    def stretch_rd(self):
        self.transform[16] += self.spinPixels.value()
        self.apply()

    def apply(self, undo_flag=False):
        """Performs the image transformation on the display overlay after saving the new display transform parameters"""

        if not undo_flag:
            self.states.append(self.transform[:])

        if len(self.states) > 10:
            del self.states[0]

        with open('config.json') as config:
            self.config = json.load(config)

        self.config['ImageCorrection']['TransformDisplay'] = self.transform

        with open('config.json', 'w+') as config:
            json.dump(self.config, config, indent=4, sort_keys=True)

        self.update_part.emit(False)

    def save(self):
        """Adds the current display transform parameters to the current contour transform parameters"""

        with open('config.json') as config:
            self.config = json.load(config)

        # Add the two transform parameter lists using list comprehension
        transform_new = [x + y for x, y in zip(self.transform, self.config['ImageCorrection']['TransformContours'])]

        self.config['ImageCorrection']['TransformContours'] = transform_new

        with open('config.json', 'w+') as parameters:
            json.dump(self.config, parameters, indent=4, sort_keys=True)

    def closeEvent(self, event):
        """Executes when the window is closed"""
        self.window_settings.setValue('Part Adjustment Geometry', self.saveGeometry())


class ImageConverter(QDialog, dialogImageConverter.Ui_dialogImageConverter):
    """Opens a Modeless Dialog Window when Tools -> Image Converter or the Image Converter button is clicked
    Allows the user to batch convert a bunch of images to their fixed state"""

    def __init__(self, parent=None):

        # Setup Dialog UI with MainWindow as parent
        super(ImageConverter, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.window_settings = QSettings('MCAM', 'Defect Monitor')

        try:
            self.restoreGeometry(self.window_settings.value('Image Converter Geometry', ''))
        except TypeError:
            pass

        # Setup event listeners for all relevant UI components, and connect them to specific functions
        self.pushBrowse.clicked.connect(self.browse)
        self.checkToggleAll.toggled.connect(self.toggle_all)
        self.checkUndistort.toggled.connect(self.toggle_save)
        self.checkPerspective.toggled.connect(self.toggle_save)
        self.checkCrop.toggled.connect(self.toggle_save)
        self.checkCrop.toggled.connect(self.toggle_alternate)
        self.checkEqualization.toggled.connect(self.toggle_save)
        self.checkSave.toggled.connect(self.reset)
        self.checkAlternate.toggled.connect(self.reset)
        self.pushStart.clicked.connect(self.start)

        # Couple of flags
        self.run_flag = False
        self.naming_flag = True

        self.threadpool = QThreadPool()

    def browse(self):
        """Opens a File Dialog, allowing the user to select one or multiple image files"""

        filenames = QFileDialog.getOpenFileNames(self, 'Browse...', '', 'Image Files (*.png)')[0]

        if filenames:
            self.image_list = filenames
            self.listImages.clear()

            # Add just the filename (without the directory path) to the list widget
            for index, item in enumerate(filenames):
                self.listImages.addItem(os.path.basename(item))

            self.groupImagesSave.setEnabled(True)
            self.image_counter = 0
            self.update_status('Please select images to save.')

    def toggle_all(self):
        """Toggles the checked state of all the options in the Images to Save groupBox"""

        for checkbox in self.groupImagesSave.findChildren(QCheckBox):
            checkbox.blockSignals(True)
            checkbox.setChecked(self.checkToggleAll.isChecked())
            checkbox.blockSignals(False)

        self.checkAlternate.setEnabled(self.checkToggleAll.isChecked())
        self.toggle_save()

    def toggle_save(self):
        """Toggles the enabled state of the Save to Individual Folders checkbox depending on the checked image boxes
        Also toggles the checked state of the Toggle All checkbox"""

        # Count the number of checked checkboxes
        counter = 0

        # Check if any of the checkboxes within the groupBox is checked (ignoring the Toggle All checkbox)
        for checkbox in self.groupImagesSave.findChildren(QCheckBox)[1:]:
            if checkbox.isChecked():
                counter += 1

        if counter > 0:
            # Enable the relevant checkbox and the Start button and exit the method
            self.checkSave.setEnabled(True)
            self.checkToggleAll.blockSignals(True)
            self.checkToggleAll.setChecked(counter == 4)
            self.checkToggleAll.blockSignals(False)
            self.reset()
            return
        else:
            # Disable the checkbox and Start button if none of the Save checkboxes are checked
            self.checkToggleAll.setChecked(False)
            self.checkSave.setEnabled(False)
            self.checkSave.setChecked(False)
            self.pushStart.setEnabled(False)
            self.update_status('Please select images to save.')

    def toggle_alternate(self):
        """Toggles the enabled state of the Alternate Naming Scheme checkbox depending on the Crop checkbox"""

        if not self.checkCrop.isChecked():
            self.checkAlternate.setChecked(False)

    def reset(self):
        """Resets the state of converted images if any of the checkboxes are toggled"""

        self.image_counter = 0
        self.pushStart.setText('Start')
        self.pushStart.setEnabled(True)
        self.update_status('Waiting to start conversion.')
        self.update_progress(0)

        for index in range(self.listImages.count()):
            self.listImages.item(index).setBackground(QColor('white'))

    def start(self):
        """Runs all the selected images in the image list through the Image Converter
        The button also functions as a Stop button which halts the conversion process
        Clicking the Start button again continues converting the remaining images unless the image list has changed"""

        if 'Start' in self.pushStart.text():
            self.run_flag = True

            # Save the isChecked and isEnabled states of the checkboxes as a list
            self.checked = list()
            self.enabled = list()

            # The findChildren function returns a list of all the checkboxes in the dialog window
            for checkbox in self.findChildren(QCheckBox):
                self.checked.append(checkbox.isChecked())
                self.enabled.append(checkbox.isEnabled())

                # Disable all the checkboxes to disallow the user from doing other tasks
                checkbox.setEnabled(False)

            # Disable all buttons to prevent user from doing other tasks
            self.pushBrowse.setEnabled(False)

            # Change the Start button into a Stop button
            self.pushStart.setText('Pause')

            folder_name = os.path.dirname(self.image_list[0])

            # Create the individual folders if the Save to Individual Folders checkbox is checked
            if self.checkSave.isChecked():
                if self.checkUndistort.isChecked():
                    if not os.path.isdir(folder_name + '/undistort'):
                        os.makedirs(folder_name + '/undistort')
                if self.checkPerspective.isChecked():
                    if not os.path.isdir(folder_name + '/perspective'):
                        os.makedirs(folder_name + '/perspective')
                if self.checkCrop.isChecked() and not self.checkAlternate.isChecked():
                    if not os.path.isdir(folder_name + '/crop'):
                        os.makedirs(folder_name + '/crop')
                if self.checkEqualization.isChecked():
                    if not os.path.isdir(folder_name + '/equalization'):
                        os.makedirs(folder_name + '/equalization')

            if self.checkAlternate.isChecked():
                if not os.path.isdir(folder_name + '/fixed'):
                    os.makedirs(folder_name + '/fixed/coat')
                    os.makedirs(folder_name + '/fixed/scan')
                    os.makedirs(folder_name + '/fixed/snapshot')

            # Start the image conversion loop
            self.convert_image(self.image_list[self.image_counter])

        elif 'Pause' in self.pushStart.text():
            self.run_flag = False
            self.pushStart.setText('Resume')
            self.pushStart.setEnabled(False)

        elif 'Resume' in self.pushStart.text():
            self.run_flag = True
            self.pushStart.setText('Pause')

            for checkbox in self.findChildren(QCheckBox):
                checkbox.setEnabled(False)

            self.convert_image(self.image_list[self.image_counter])

    def convert_image(self, image_name):
        """Converts the image by applying the required image processing functions to fix the images using QThreads"""

        self.naming_flag = True

        worker = qt_multithreading.Worker(self.convert_image_function, image_name, self.checked)
        worker.signals.status.connect(self.update_status)
        worker.signals.progress.connect(self.update_progress)
        worker.signals.naming_error.connect(self.naming_error)
        worker.signals.finished.connect(self.convert_image_finished)
        self.threadpool.start(worker)

    @staticmethod
    def convert_image_function(image_name, checkboxes, status, progress, naming_error):
        """Applies the distortion, perspective, crop and CLAHE processes to the received image
        Also subsequently saves each image after every process if the corresponding checkbox is checked"""

        # Load the image into memory
        image = cv2.imread(image_name)

        # Grab the folder names and the image name which will be used to construct the new modified names
        folder_name = os.path.dirname(image_name)
        image_name = os.path.basename(os.path.splitext(image_name)[0])

        # If the Alternate Naming Scheme for Crop Images checkbox is checked
        # Detect the phase and layer number from the image name itself and use those to save to the fixed folder instead
        if checkboxes[0]:
            # Phase check
            if 'coatR_' in image_name:
                phase = 'coat'
            elif 'scanR_' in image_name:
                phase = 'scan'
            elif 'snapshotR_' in image_name:
                phase = 'snapshot'
            else:
                # If the phase can't be determined due to incorrect naming, don't use alternate naming scheme
                checkboxes[0] = False
                naming_error.emit()

            # Layer check
            try:
                int(image_name[-4:])
            except ValueError:
                # If the layer number can't be determined due to incorrect naming, don't use alternate naming scheme
                checkboxes[0] = False
                naming_error.emit()

        # Apply the image processing techniques in order, subsequently saving the image and incrementing progress
        # Images are only saved if the corresponding checkbox is checked

        progress.emit(0)
        status.emit('Undistorting image...')
        image = image_processing.ImageTransform().distortion_fix(image)

        if checkboxes[3]:
            if checkboxes[1]:
                cv2.imwrite('%s/undistort/%s_D.png' % (folder_name, image_name), image)
            else:
                cv2.imwrite('%s/%s_D.png' % (folder_name, image_name), image)

        progress.emit(25)
        status.emit('Fixing perspective warp...')
        image = image_processing.ImageTransform().perspective_fix(image)

        if checkboxes[4]:
            if checkboxes[1]:
                cv2.imwrite('%s/perspective/%s_DP.png' % (folder_name, image_name), image)
            else:
                cv2.imwrite('%s/%s_DP.png' % (folder_name, image_name), image)

        progress.emit(50)
        status.emit('Cropping image to size...')
        image = image_processing.ImageTransform().crop(image)

        if checkboxes[5]:
            if checkboxes[0]:
                cv2.imwrite('%s/fixed/%s/%s.png' % (folder_name, phase, image_name.replace('R_', 'F_')), image)
            elif checkboxes[1]:
                cv2.imwrite('%s/crop/%s_DPC.png' % (folder_name, image_name), image)
            else:
                cv2.imwrite('%s/%s_DPC.png' % (folder_name, image_name), image)

        progress.emit(75)
        status.emit('Applying CLAHE equalization...')
        image = image_processing.ImageTransform().clahe(image)

        if checkboxes[6]:
            if checkboxes[1]:
                cv2.imwrite('%s/equalization/%s_DPCE.png' % (folder_name, image_name), image)
            else:
                cv2.imwrite('%s/%s_DPCE.png' % (folder_name, image_name), image)

        progress.emit(100)
        status.emit('Image conversion successful.')

    def convert_image_finished(self):
        """Continuation function that either continues the image processing loop or finishes the entire run"""

        if self.naming_flag:
            self.listImages.item(self.image_counter).setBackground(QColor('green'))

        self.image_counter += 1

        if self.run_flag and not self.image_counter == len(self.image_list):
            self.convert_image(self.image_list[self.image_counter])
        else:
            self.pushBrowse.setEnabled(True)
            for index, checkbox in enumerate(self.findChildren(QCheckBox)):
                checkbox.setEnabled(self.enabled[index])

            if self.image_counter == len(self.image_list):
                self.run_flag = False
                self.pushStart.setEnabled(False)
                self.pushStart.setText('Start')
                self.update_status('Conversion finished.')
            else:
                self.pushStart.setEnabled(True)
                self.update_status('Conversion paused.')

    def naming_error(self):
        """Sets the colour of the current item to yellow and stops the conversion from turning the item green
        Indicates that the image names are incorrect for the Alternate Naming Scheme"""

        self.naming_flag = False
        self.listImages.item(self.image_counter).setBackground(QColor('yellow'))

    def update_status(self, string):
        self.labelStatus.setText(string)

    def update_progress(self, percentage):
        self.progressBar.setValue(int(percentage))

    def closeEvent(self, event):
        """Executes when the window is closed"""

        # Check if a conversion is in progress, and block the user from closing the window until stopped
        if self.run_flag:
            run_error = QMessageBox(self)
            run_error.setWindowTitle('Error')
            run_error.setIcon(QMessageBox.Critical)
            run_error.setText('Conversion in progress.\n\n'
                              'Please pause or wait for the conversion to finish before exiting.')
            run_error.exec_()
            event.ignore()
        else:
            self.window_settings.setValue('Image Converter Geometry', self.saveGeometry())


class DefectReports(QDialog, dialogDefectReports.Ui_dialogDefectReports):
    """Opens a Modeless Dialog Window when the Defect Reports button is clicked
    Allows user to look at the defect reports in a nice visual way
    """

    tab_focus = pyqtSignal(int, int, bool, int)

    def __init__(self, parent=None):

        # Setup Dialog UI with MainWindow as parent
        super(DefectReports, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.window_settings = QSettings('MCAM', 'Defect Monitor')

        try:
            self.restoreGeometry(self.window_settings.value('Defect Reports Geometry', ''))
        except TypeError:
            pass

        # Load from the build.json file
        with open('build.json') as build:
            self.build = json.load(build)

        # Load from the config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Setup event listeners for all relevant UI components, and connect them to specific functions
        self.comboParts.currentIndexChanged.connect(self.populate_tables)
        self.pushSet.clicked.connect(self.set_thresholds)
        self.tableCoat.cellDoubleClicked.connect(self.cell_click)
        self.tableScan.cellDoubleClicked.connect(self.cell_click)

        # Grab the part name list (with combined and background at the start) by polling the reports folder
        self.part_names = ['combined', 'background']
        for name in os.listdir(self.build['BuildInfo']['Folder'] + '/reports'):
            if 'combined' in name or 'background' in name:
                continue
            else:
                self.part_names.append(name.replace('_report.json', ''))

        # Add the part names to the combo box
        self.comboParts.addItems(self.part_names)

        # Sets the data table's columns to automatically resize appropriately
        # Except the first column, the layer number, which will be as small as possible
        self.tableCoat.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableScan.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableCoat.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tableScan.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        # Set the threshold spinboxes with the values from the config.json file
        self.spinPixelSize.setValue(self.config['Threshold']['PixelSize'])
        self.spinOccurrences.setValue(self.config['Threshold']['Occurrences'])
        self.spinOverlay.setValue(self.config['Threshold']['Overlay'])
        self.spinHistogramCoat.setValue(self.config['Threshold']['HistogramCoat'])
        self.spinHistogramScan.setValue(self.config['Threshold']['HistogramScan'])

    def populate_tables(self, part):
        """Populates both tables with the data from the selected defect report"""

        # Read the appropriate report into memory
        with open('%s/reports/%s_report.json' % (self.build['BuildInfo']['Folder'], self.part_names[part])) as report:
            report = json.load(report)

        # Completely remove all the data from both tables
        self.tableCoat.setRowCount(0)
        self.tableScan.setRowCount(0)

        # Disable sorting while populating the table so the data order doesn't get messed up
        self.tableCoat.setSortingEnabled(False)
        self.tableScan.setSortingEnabled(False)

        # Check if the report dictionary has anything at all
        if report:
            # Calculate the maximum number of layers to set the number of table rows
            max_layer = max([int(number) for number in list(report)])
            self.tableCoat.setRowCount(max_layer)
            self.tableScan.setRowCount(max_layer)

            # Grab the threshold values for both the coat and the scan defects in separate lists
            threshold_coat = [0, self.config['Threshold']['Occurrences'], self.config['Threshold']['Occurrences'],
                              self.config['Threshold']['PixelSize'], self.config['Threshold']['PixelSize'],
                              self.config['Threshold']['HistogramCoat']]
            threshold_scan = [0, self.config['Threshold']['Occurrences'], self.config['Threshold']['Occurrences'],
                              self.config['Threshold']['HistogramScan'], self.config['Threshold']['Overlay']]

            # Display all the relevant data in the table, while also filling out the 'missing' rows with zeroes
            for row in range(max_layer):
                # COAT DATA
                # Grab the Coat data in a try loop in case the index doesn't exist in the dictionary
                try:
                    data = report[str(row + 1).zfill(4)]['coat']
                except (IndexError, KeyError):
                    data = {}

                # Reset a list of colours to colour code each cell
                data_colours = list()
                data_coat = list()

                if data:
                    # Grab the data from the report dictionary, with the first element being the layer number
                    data_coat = [row + 1, data['BS'][1], data['BC'][1], data['SP'][0], data['CO'][0]]

                    # Only append the histogram comparison information if the 'combined' part is being displayed
                    if part == 0:
                        # And if the histogram result is available in the first place
                        try:
                            data_coat.append(round(data['HC'], 2))
                        except (KeyError, IndexError):
                            data_coat.append(0)

                    # Set colours for if the data is over/under the threshold, or there is no data at all
                    # Green is GOOD
                    # Red is BAD
                    # Yellow is NONE
                    # NOTE: Different results have different conditions (over/under) for a good/bad result
                    for index, value in enumerate(data_coat):
                        if value < threshold_coat[index]:
                            data_colours.append(QColor(0, 255, 0))
                        else:
                            data_colours.append(QColor(255, 0, 0))
                else:
                    for number in range(6):
                        data_coat.append(0)
                        data_colours.append(QColor(255, 255, 0))

                    # Set the first element to the layer number
                    data_coat[0] = row + 1

                # Fill the table cells with the corresponding data
                for column in range(len(data_coat)):
                    # The following lines allow the data to be sorted numerically (rather than as strings)
                    item = QTableWidgetItem()
                    item.setData(Qt.EditRole, data_coat[column])
                    self.tableCoat.setItem(row, column, item)

                    # Ignore the first column (layer number) when it comes to setting the background colour
                    if column != 0:
                        self.tableCoat.item(row, column).setBackground(data_colours[column])

                # SCAN DATA
                # Grab the Scan data in a try loop in case the index doesn't exist in the dictionary
                try:
                    data = report[str(row + 1).zfill(4)]['scan']
                except (IndexError, KeyError):
                    data = {}

                # Reset a list of colours to colour code each cell
                data_colours = list()
                data_scan = list()

                if data:
                    # Grab the data from the report dictionary, with the first element being the layer number
                    data_scan = [row + 1, data['BS'][1], data['BC'][1]]

                    # Only append the histogram comparison information if the 'combined' part is being displayed
                    if part == 0:
                        # And if the histogram result is available in the first place
                        try:
                            data_scan.append(round(data['HC'], 2))
                        except (KeyError, IndexError):
                            data_scan.append(0)
                        # Same goes for the overlay comparison information
                        try:
                            data_scan.append(round(data['OC'] * 100, 4))
                        except (KeyError, IndexError):
                            data_scan.append(0)

                    # Set colours for if the data is over/under the threshold, or there is no data at all
                    for index, value in enumerate(data_scan):
                        if value < threshold_scan[index] and index < 3:
                            data_colours.append(QColor(0, 255, 0))
                        elif value > threshold_scan[index] and index == 3:
                            data_colours.append(QColor(0, 255, 0))
                        else:
                            data_colours.append(QColor(255, 0, 0))
                else:
                    for number in range(5):
                        data_scan.append(0)
                        data_colours.append(QColor(255, 255, 0))

                    # Set the first element to the layer number
                    data_scan[0] = row + 1

                # Fill the table cells with the corresponding data
                for column in range(len(data_scan)):
                    # The following lines allow the data to be sorted numerically (rather than as strings)
                    item = QTableWidgetItem()
                    item.setData(Qt.EditRole, data_scan[column])
                    self.tableScan.setItem(row, column, item)

                    # Ignore the first column (layer number) when it comes to setting the background colour
                    if column != 0:
                        self.tableScan.item(row, column).setBackground(data_colours[column])

        # Sets the row height to as small as possible to fit the text height
        self.tableCoat.resizeRowsToContents()
        self.tableScan.resizeRowsToContents()

        # Re-enable sorting
        self.tableCoat.setSortingEnabled(True)
        self.tableScan.setSortingEnabled(True)

    def set_thresholds(self):
        """Save the entered threshold values to the config.json file and reload the data based on the new values"""

        with open('config.json') as config:
            self.config = json.load(config)

        # Save the new values from the changed settings to the config dictionary
        self.config['Threshold']['PixelSize'] = self.spinPixelSize.value()
        self.config['Threshold']['Occurrences'] = self.spinOccurrences.value()
        self.config['Threshold']['Overlay'] = self.spinOverlay.value()
        self.config['Threshold']['HistogramCoat'] = self.spinHistogramCoat.value()
        self.config['Threshold']['HistogramScan'] = self.spinHistogramScan.value()

        with open('config.json', 'w+') as config:
            json.dump(self.config, config, indent=4, sort_keys=True)

        # Reload the data and colour code based on the new threshold values
        self.populate_tables(self.comboParts.currentIndex())

    def cell_click(self, row, column):
        """Send a signal back to the MainWindow to display the corresponding defect image
        When a cell in the report table is clicked"""

        # Grab the layer number from the table as it won't correlate with the row number if the table is sorted
        # Also depends if it's the coat or scan table being clicked
        if self.widgetReports.currentIndex() == 0:
            layer = int(self.tableCoat.item(row, 0).text())
        else:
            layer = int(self.tableScan.item(row, 0).text())
            if column == 4:
                column += 1

        # Emit a signal to change focus to the selected defect layer
        self.tab_focus.emit(self.widgetReports.currentIndex(), layer, True, column - 1)

    def closeEvent(self, event):
        """Executes when the Done button is clicked or when the window is closed"""
        self.window_settings.setValue('Defect Reports Geometry', self.saveGeometry())
