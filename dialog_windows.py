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
import extra_functions
import camera_calibration
import qt_multithreading

# Import PyQt GUIs
from gui import dialogNewBuild, dialogInterfacePreferences, dialogCameraCalibration, dialogCalibrationResults, \
    dialogSliceConverter, dialogCameraSettings, dialogOverlayAdjustment, dialogDefectReports


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

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        # Buttons
        self.pushBrowseSF.clicked.connect(self.browse_slice)
        self.pushBrowseBF.clicked.connect(self.browse_build_folder)
        self.pushSendTestEmail.clicked.connect(self.send_test)
        self.pushCreate.clicked.connect(self.create)
        self.lineEmailAddress.textChanged.connect(self.enable_button)

        # Flag to prevent additional image folders from being created
        self.open_flag = open_flag

        # Set and display the default build image save folder
        self.slice_list = list()
        self.build_folder = self.build['BuildInfo']['Folder']
        self.lineBuildFolder.setText(self.build_folder)

        # If this dialog window was opened as a result of the Open... action, then the following is executed
        # Set and display the relevant names/values of the following text boxes as outlined in the opened config file
        if self.open_flag:
            self.setWindowTitle('Open Build')
            self.pushCreate.setText('Load')
            self.lineBuildName.setText(self.build['BuildInfo']['Name'])
            self.comboPlatform.setCurrentIndex(self.build['BuildInfo']['Platform'])
            self.slice_list = self.build['BuildInfo']['SliceFiles']
            self.set_list(self.slice_list)
            self.lineUsername.setText(self.build['BuildInfo']['Username'])
            self.lineEmailAddress.setText(self.build['BuildInfo']['EmailAddress'])
            self.checkMinor.setChecked(self.build['Notifications']['Minor'])
            self.checkMajor.setChecked(self.build['Notifications']['Major'])

        # If this dialog window was opened as a result of the Build Settings... action, then the following is executed
        # Disable a few of the buttons to disallow changing of the slice files and build folder
        if settings_flag:
            self.pushBrowseSF.setEnabled(False)
            self.pushBrowseBF.setEnabled(False)
            self.setWindowTitle('Build Settings')
            self.pushCreate.setText('OK')

        self.threadpool = QThreadPool()

    def browse_slice(self):
        """Opens a File Dialog, allowing the user to select one or multiple slice files"""

        filenames = QFileDialog.getOpenFileNames(self, 'Browse...', '', 'Slice Files (*.cls *.cli)')[0]

        # Check if a file has been selected as QFileDialog returns an empty string if cancel was pressed
        if filenames:
            self.slice_list = filenames
            self.set_list(filenames)

    def browse_build_folder(self):
        """Opens a File Dialog, allowing the user to select a folder to store the current build's image folder"""

        folder = QFileDialog.getExistingDirectory(self, 'Browse...', '')

        if folder:
            # Display just the file name on the line box
            self.build_folder = folder
            self.lineBuildFolder.setText(folder)

    def send_test(self):
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
                    self.build['Notifications']['Attachment'] = '%s/test_image.jpg' % self.build['WorkingDirectory']
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
            self.pushSendTestEmail.setEnabled(True)
            self.checkAddAttachment.setEnabled(True)
        else:
            self.pushSendTestEmail.setEnabled(False)
            self.checkAddAttachment.setEnabled(False)

    def create(self):
        """Executes when the Create button is clicked
        First checks if all the required boxes have been filled, otherwise a MessageBox will be opened
        Saves important selection options to the config.json file and closes the window
        """

        error_message = str()

        if not self.lineBuildName.text():
            error_message += 'Build Name not entered.\n'
        if not self.slice_list:
            error_message += 'Slice files not selected.\n'
        if not self.lineUsername.text():
            error_message += 'Username not entered.\n'
        if not validate_email(self.lineEmailAddress.text()):
            error_message += 'Email Address not valid.\n'

        if error_message:
            missing_folder_error = QMessageBox(self)
            missing_folder_error.setWindowTitle('Error')
            missing_folder_error.setIcon(QMessageBox.Critical)
            missing_folder_error.setText(error_message.rstrip('\n'))
            missing_folder_error.exec_()
        else:
            # Save all the entered information to the config.json file
            self.build['BuildInfo']['Name'] = str(self.lineBuildName.text())
            self.build['BuildInfo']['Platform'] = self.comboPlatform.currentIndex()
            self.build['BuildInfo']['Username'] = str(self.lineUsername.text())
            self.build['BuildInfo']['EmailAddress'] = str(self.lineEmailAddress.text())
            self.build['BuildInfo']['Convert'] = self.checkConvert.isChecked()
            if self.checkConvert.isChecked():
                self.build['BuildInfo']['Draw'] = self.checkDraw.isChecked()
            self.build['BuildInfo']['Folder'] = self.build_folder
            self.build['BuildInfo']['SliceFiles'] = self.slice_list
            self.build['Notifications']['Minor'] = self.checkMinor.isChecked()
            self.build['Notifications']['Major'] = self.checkMajor.isChecked()

            # Save the selected platform dimensions to the config.json file
            if self.comboPlatform.currentIndex() == 0:
                self.build['BuildInfo']['PlatformDimensions'] = [636, 406]

            # If a New Build is being created (rather than Open Build), create some folders to store images
            if not self.open_flag:
                # Generate a timestamp for folder labelling purposes
                current_time = datetime.now()

                # Set the full name of the main storage folder for all acquired images
                image_folder = """%s/%s-%s-%s [%s''%s'%s] %s""" % \
                               (self.build['BuildInfo']['Folder'], current_time.year, str(current_time.month).zfill(2),
                                str(current_time.day).zfill(2), str(current_time.hour).zfill(2),
                                str(current_time.minute).zfill(2), str(current_time.second).zfill(2),
                                self.build['BuildInfo']['Name'])

                # Save the created image folder's name to the build.json file
                self.build['ImageCapture']['Folder'] = image_folder

                # Create respective sub-directories for images (and reports)
                os.makedirs('%s/raw/coat' % image_folder)
                os.makedirs('%s/raw/scan' % image_folder)
                os.makedirs('%s/raw/single' % image_folder)
                os.makedirs('%s/fixed/coat' % image_folder)
                os.makedirs('%s/fixed/scan' % image_folder)
                os.makedirs('%s/fixed/single' % image_folder)
                os.makedirs('%s/defects/coat/streaks' % image_folder)
                os.makedirs('%s/defects/coat/chatter' % image_folder)
                os.makedirs('%s/defects/coat/patches' % image_folder)
                os.makedirs('%s/defects/coat/outliers' % image_folder)
                os.makedirs('%s/defects/scan/streaks' % image_folder)
                os.makedirs('%s/defects/scan/chatter' % image_folder)
                os.makedirs('%s/defects/scan/pattern' % image_folder)
                os.makedirs('%s/contours' % image_folder)
                os.makedirs('%s/reports' % image_folder)

                # Create a dictionary of colours (different shades of teal) for each part's contours and save it
                # At the same time, create a bunch of json files containing a blank dictionary
                # These json files are used to store the defect coordinate and pixel size data for each of the parts
                part_colours = dict()
                dict_blank = dict()

                # Append additional 'background' and 'combined' parts and create their folders as well
                report_list = self.slice_list.copy()
                report_list.append('background')
                report_list.append('combined')

                for index, part_name in enumerate(report_list):
                    part_name = os.path.splitext(os.path.basename(part_name))[0]
                    part_colours[part_name] = ((100 + 2 * index) % 255, (100 + 2 * index) % 255, 0)

                    with open('%s/reports/%s_report.json' % (image_folder, part_name), 'w+') as report:
                        json.dump(dict_blank, report)

                # Set the 'background' part colour to black and save the dictionary
                part_colours['background'] = (0, 0, 0)
                self.build['BuildInfo']['Colours'] = part_colours
            else:
                # Check if the folder containing the images exist if a build was opened
                if not os.path.isdir(self.build['ImageCapture']['Folder']):
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


class InterfacePreferences(QDialog, dialogInterfacePreferences.Ui_dialogInterfacePreferences):
    """Opens a Modeless Dialog Window when Settings -> Preferences is clicked
    Allows the user to change any settings in regard to the main interface"""

    def __init__(self, parent=None):

        # Setup Dialog UI with MainWindow as parent and restore the previous window state
        super(InterfacePreferences, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.window_settings = QSettings('MCAM', 'Defect Monitor')
        try:
            self.restoreGeometry(self.window_settings.value('Interface Preferences Geometry', ''))
        except TypeError:
            pass

        with open('config.json') as config:
            self.config = json.load(config)

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        self.pushModify.clicked.connect(self.modify_gridlines)

        # Set the combo box and settings to previously saved values
        self.spinSize.setValue(self.config['Gridlines']['Size'])
        self.spinThickness.setValue(self.config['Gridlines']['Thickness'])

        # Set the maximum range of the grid size spinbox
        self.spinSize.setMaximum(int(self.config['ImageCorrection']['ImageResolution'][0] / 2))
        self.spinSize.setToolTip('5 - %s' % int(self.config['ImageCorrection']['ImageResolution'][0] / 2))

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

    def closeEvent(self, event):
        """Executes when the window is closed"""
        self.window_settings.setValue('Calibration Results Geometry', self.saveGeometry())


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

        # Setup event listeners for all the setting boxes to detect a change in an entered value
        self.comboPixelFormat.currentIndexChanged.connect(self.apply_enable)
        self.spinGain.valueChanged.connect(self.apply_enable)
        self.spinBlackLevel.valueChanged.connect(self.apply_enable)
        self.spinExposureTime.valueChanged.connect(self.apply_enable)
        self.spinPacketSize.valueChanged.connect(self.apply_enable)
        self.spinInterPacketDelay.valueChanged.connect(self.apply_enable)
        self.spinFrameDelay.valueChanged.connect(self.apply_enable)
        self.spinTriggerTimeout.valueChanged.connect(self.apply_enable)

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

        self.pushApply.setEnabled(False)

    def apply_enable(self):
        """Enable the Apply button on any change of settings"""
        self.pushApply.setEnabled(True)

    def apply(self):
        """Executes when the Apply button is clicked and saves the entered values to the config.json file"""

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

        try:
            self.restoreGeometry(self.window_settings.value('Slice Converter Geometry', ''))
        except TypeError:
            pass

        with open('build.json') as build:
            self.build = json.load(build)

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        self.buttonBrowseSF.clicked.connect(self.browse_slice)
        self.buttonBrowseF.clicked.connect(self.browse_folder)
        self.buttonStart.clicked.connect(self.start)
        self.buttonStop.clicked.connect(self.start_finished)
        self.checkDraw.toggled.connect(self.toggle_range)
        self.spinRangeLow.valueChanged.connect(self.set_range)

        # Create and display a 'default' contours folder to store the drawn part contours
        self.contours_folder = os.path.dirname(self.build['WorkingDirectory']) + '/contours'
        self.lineFolder.setText(self.contours_folder)

        self.threadpool = QThreadPool()

    def browse_slice(self):
        """Opens a File Dialog, allowing the user to select one or multiple slice files"""

        filenames = QFileDialog.getOpenFileNames(self, 'Browse...', '', 'Slice Files (*.cli)')[0]

        if filenames:
            self.slice_list = filenames
            self.listSliceFiles.clear()
            self.buttonStart.setEnabled(True)
            self.update_status('Current Part: None | Waiting to start conversion.')
            for item in self.slice_list:
                self.listSliceFiles.addItem(os.path.basename(item))

    def browse_folder(self):
        """Opens a File Dialog, allowing the user to select a folder to save the drawn contours to"""

        folder = QFileDialog.getExistingDirectory(self, 'Browse...', '')

        if folder:
            self.contours_folder = folder
            self.lineFolder.setText(self.contours_folder)

    def start(self):
        """Executes when the Start/Pause/Resume button is clicked and does one of the following depending on the text"""

        with open('build.json') as build:
            self.build = json.load(build)

        if 'Start' in self.buttonStart.text():
            # Disable all buttons to prevent user from doing other tasks
            self.buttonStop.setEnabled(True)
            self.buttonBrowseSF.setEnabled(False)
            self.buttonBrowseF.setEnabled(False)
            self.buttonDone.setEnabled(False)
            self.checkDraw.setEnabled(False)
            self.checkRange.setEnabled(False)
            self.spinRangeLow.setEnabled(False)
            self.spinRangeHigh.setEnabled(False)
            self.update_progress(0)

            # Change the Start button into a Pause/Resume button
            self.buttonStart.setText('Pause')

            # Create a dictionary of colours (different shades of teal) for each part's contours and save it
            part_colours = dict()
            for index, part_name in enumerate(self.slice_list):
                part_colours[os.path.splitext(os.path.basename(part_name))[0]] = \
                    ((100 + 2 * index) % 255, (100 + 2 * index) % 255, 0)

            # Save the slice file list and the draw state to the config.json file
            self.build['SliceConverter']['Draw'] = self.checkDraw.isChecked()
            self.build['SliceConverter']['Folder'] = self.contours_folder
            self.build['SliceConverter']['Files'] = self.slice_list
            self.build['SliceConverter']['Run'] = True
            self.build['SliceConverter']['Pause'] = False
            self.build['SliceConverter']['Build'] = False
            self.build['SliceConverter']['Colours'] = part_colours
            self.build['SliceConverter']['Range'] = self.checkRange.isChecked()
            self.build['SliceConverter']['RangeLow'] = self.spinRangeLow.value()
            self.build['SliceConverter']['RangeHigh'] = self.spinRangeHigh.value()

            with open('build.json', 'w+') as build:
                json.dump(self.build, build, indent=4, sort_keys=True)

            worker = qt_multithreading.Worker(slice_converter.SliceConverter().run_converter)
            worker.signals.status.connect(self.update_status)
            worker.signals.progress.connect(self.update_progress)
            worker.signals.finished.connect(self.start_finished)
            self.threadpool.start(worker)

        elif 'Pause' in self.buttonStart.text():
            self.build['SliceConverter']['Pause'] = True
            self.buttonStart.setText('Resume')
        elif 'Resume' in self.buttonStart.text():
            self.build['SliceConverter']['Pause'] = False
            self.buttonStart.setText('Pause')

        with open('build.json', 'w+') as build:
            json.dump(self.build, build, indent=4, sort_keys=True)

    def start_finished(self):
        """Executes when the SliceConverter instance has finished"""

        with open('build.json') as build:
            self.build = json.load(build)

        # Stop the conversion thread
        self.build['SliceConverter']['Pause'] = False
        self.build['SliceConverter']['Run'] = False

        with open('build.json', 'w+') as build:
            json.dump(self.build, build, indent=4, sort_keys=True)

        # Enable/disable respective buttons
        self.buttonStart.setText('Start')
        self.buttonStop.setEnabled(False)
        self.buttonBrowseSF.setEnabled(True)
        self.buttonBrowseF.setEnabled(True)
        self.buttonDone.setEnabled(True)
        self.checkDraw.setEnabled(True)
        if self.checkDraw.isChecked():
            self.checkRange.setEnabled(True)
            self.spinRangeLow.setEnabled(True)
            self.spinRangeHigh.setEnabled(True)

    def toggle_range(self):
        """Toggles the state of the Draw Range checkbox if the Draw Contours checkbox is unchecked"""

        if not self.checkDraw.isChecked():
            self.checkRange.setChecked(False)

    def set_range(self, value):
        """Sets the minimum value of the high spinbox to the current value of the low spinbox"""

        self.spinRangeHigh.setMinimum(value)

    def update_status(self, string):
        string = string.split(' | ')
        self.labelStatus.setText(string[1])
        self.labelStatusSlice.setText(string[0])

    def update_progress(self, percentage):
        self.progressBar.setValue(percentage)

    def closeEvent(self, event):
        """Executes when the window is closed"""

        with open('build.json') as build:
            self.build = json.load(build)

        # Check if a conversion is in progress or paused, and block the user from closing the window until stopped
        if not self.buttonDone.isEnabled():
            run_error = QMessageBox(self)
            run_error.setWindowTitle('Error')
            run_error.setIcon(QMessageBox.Critical)
            run_error.setText('Conversion in progress or paused.\n\n'
                              'Please stop or wait for the conversion to finish before exiting.')
            run_error.exec_()
            event.ignore()
        else:
            self.build['SliceConverter']['Folder'] = ''
            self.build['SliceConverter']['Files'] = []

            with open('build.json', 'w+') as build:
                json.dump(self.build, build, indent=4, sort_keys=True)

            self.window_settings.setValue('Slice Converter Geometry', self.saveGeometry())


class OverlayAdjustment(QDialog, dialogOverlayAdjustment.Ui_dialogOverlayAdjustment):
    """Opens a Modeless Dialog Window when the Overlay Adjustment button is clicked
    Or when Tools -> Overlay Adjustment is clicked
    Allows the user to adjust and transform the overlay image in a variety of ways
    """

    # Signal that will be emitted anytime one of the transformation buttons is pressed
    update_overlay = pyqtSignal(bool)

    def __init__(self, parent=None):

        # Setup Dialog UI with MainWindow as parent and restore the previous window state
        super(OverlayAdjustment, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.window_settings = QSettings('MCAM', 'Defect Monitor')

        try:
            self.restoreGeometry(self.window_settings.value('Overlay Adjustment Geometry', ''))
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

        self.update_overlay.emit(False)

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
        self.window_settings.setValue('Overlay Adjustment Geometry', self.saveGeometry())


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
        self.comboParts.currentIndexChanged.connect(self.display_report)
        self.pushSet.clicked.connect(self.set_thresholds)
        self.tableCoat.cellDoubleClicked.connect(self.cell_click)
        self.tableScan.cellDoubleClicked.connect(self.cell_click)

        # Save the part name list (with combined and background at the start)
        self.part_names = ['combined', 'background'] + list(self.build['BuildInfo']['Colours'])[:-2]

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

    def display_report(self, part):

        # Read the appropriate report into memory
        with open('%s/reports/%s_report.json' % (self.build['ImageCapture']['Folder'],
                                                 self.part_names[part])) as report:
            report = json.load(report)

        # Disable sorting while populating the table so things don't get messed up
        self.tableCoat.setSortingEnabled(False)
        self.tableScan.setSortingEnabled(False)

        # First of all, check if the report dictionary has anything at all
        if report:
            # Find out the maximum number of layers to set the number of table rows
            max_layer = max([int(number) for number in list(report)])
            self.tableCoat.setRowCount(max_layer)
            self.tableScan.setRowCount(max_layer)

            # Grab the threshold values for the coat and the scan in separate lists
            threshold_coat = [0, self.config['Threshold']['Occurrences'], self.config['Threshold']['Occurrences'],
                              self.config['Threshold']['PixelSize'], self.config['Threshold']['PixelSize'],
                              self.config['Threshold']['HistogramCoat']]
            threshold_scan = [0, self.config['Threshold']['Occurrences'], self.config['Threshold']['Occurrences'],
                              self.config['Threshold']['HistogramScan'], self.config['Threshold']['Overlay']]

            # Display all the relevant data in the table, while also filling out the 'missing' rows with blanks
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
                    # Green for value is GOOD
                    # Red for value is BAD
                    # Yellow for value is NONE
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
        self.display_report(self.comboParts.currentIndex())

    def cell_click(self, row, column):
        """Send a signal back to the Main Window to display the corresponding defect image
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
