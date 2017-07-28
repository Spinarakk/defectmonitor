# Import external libraries
import os
import sys
import shutil
import math
import json
from datetime import datetime
import cv2
import numpy as np
from PyQt4 import QtGui
from PyQt4.QtCore import SIGNAL, Qt

# Compile and import PyQt GUIs
os.system('build_gui.bat')
from gui import mainWindow

# Import related modules
import dialog_windows
import extra_functions
import slice_converter
import image_capture
import image_processing


class MainWindow(QtGui.QMainWindow, mainWindow.Ui_mainWindow):
    """Main module used to initiate the main GUI window and all of its associated dialogs/widgets
    Only methods that relate directly manipulating any element of the UI are allowed in this module
    All other functions related to image processing etc. are called using QThreads and split into separate modules
    All dialog windows are found and called in the dialog_windows.py
    """

    def __init__(self, parent=None):

        # Setup Main Window UI
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)

        # Set whether this is a simulation or using real camera
        self.simulation_flag = True

        # Get the current working directory
        self.working_directory = os.getcwd()
        self.working_directory = self.working_directory.replace("\\", '/')

        # Load configuration settings from config.json file
        # If config.json is empty or missing, config_backup.json is read and dumped as config.json
        try:
            with open('config.json') as config:
                self.config = json.load(config)
        except:
            with open('config_backup.json') as config:
                self.config = json.load(config)
            with open('config.json', 'w+') as config:
                json.dump(self.config, config)

        # Save the current working directory to the config.json file so later methods can grab it
        self.config['WorkingDirectory'] = self.working_directory
        with open('config.json', 'w+') as config:
            json.dump(self.config, config)

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        # Menubar -> File
        self.actionNewBuild.triggered.connect(self.new_build)
        self.actionOpenBuild.triggered.connect(self.open_build)
        self.actionExportImage.triggered.connect(self.export_image)
        self.actionExit.triggered.connect(self.closeEvent)

        # Menubar -> Setup
        self.actionConfigurationSettings.triggered.connect(self.configuration_settings)
        self.actionCameraSettings.triggered.connect(self.camera_settings)
        self.actionCameraCalibration.triggered.connect(self.camera_calibration)
        self.actionSliceConverter.triggered.connect(self.slice_converter)
        self.actionDefectActions.triggered.connect(self.defect_actions)
        self.actionNotificationSettings.triggered.connect(self.notification_settings)

        # Menubar -> Run
        self.actionInitializeBuild.triggered.connect(self.initialize_1)
        self.actionStartBuild.triggered.connect(self.start)
        self.actionPauseBuild.triggered.connect(self.pause)
        self.actionStopBuild.triggered.connect(self.stop)

        # Buttons
        self.buttonInitialize.clicked.connect(self.initialize_1)
        self.buttonStart.clicked.connect(self.start)
        self.buttonPause.clicked.connect(self.pause)
        self.buttonStop.clicked.connect(self.stop)
        self.buttonSet.clicked.connect(self.set_layer)
        self.buttonDisplayImages.clicked.connect(self.display_images)
        self.buttonNotificationSettings.clicked.connect(self.notification_settings)
        self.buttonImageConverter.clicked.connect(self.image_converter)
        self.buttonDefectProcessing.clicked.connect(self.defect_processing)
        self.buttonImageCapture.clicked.connect(self.image_capture)
        self.buttonSliceConverter.clicked.connect(self.slice_converter)
        self.buttonCameraCalibration.clicked.connect(self.camera_calibration)

        # Toggles
        self.checkSimulation.toggled.connect(self.toggle_simulation)

        # Display Options Group Box
        self.radioRaw.toggled.connect(self.update_display)
        self.radioCorrection.toggled.connect(self.update_display)
        self.radioCrop.toggled.connect(self.update_display)
        self.radioCLAHE.toggled.connect(self.update_display)
        self.checkToggleOverlay.toggled.connect(self.toggle_overlay)

        # OpenCV Processsing Group Box
        self.radioOpenCV1.toggled.connect(self.update_display)
        self.radioOpenCV2.toggled.connect(self.update_display)
        self.radioOpenCV3.toggled.connect(self.update_display)
        self.radioOpenCV4.toggled.connect(self.update_display)
        self.radioOpenCV5.toggled.connect(self.update_display)

        # Position Adjustment Group Box
        self.buttonBoundary.toggled.connect(self.toggle_boundary)
        self.buttonCrop.toggled.connect(self.toggle_crop)
        self.buttonShiftUp.clicked.connect(self.shift_up)
        self.buttonShiftDown.clicked.connect(self.shift_down)
        self.buttonShiftLeft.clicked.connect(self.shift_left)
        self.buttonShiftRight.clicked.connect(self.shift_right)
        self.buttonRotateACW.clicked.connect(self.rotate_acw)
        self.buttonRotateCW.clicked.connect(self.rotate_cw)

        # Display Widget Tabs
        self.widgetDisplay.currentChanged.connect(self.tab_change)

        # ScrollBars
        self.scrollSE.valueChanged.connect(self.scrollbar_change)

        # Generate a timestamp for folder labelling purposes
        current_time = datetime.now()

        # Set the full name of the main storage folder for all acquired images
        self.image_folder = """%s\%s-%s-%s [%s''%s'%s]""" % \
                            (self.working_directory, current_time.year, str(current_time.month).zfill(2),
                             str(current_time.day).zfill(2), str(current_time.hour).zfill(2),
                             str(current_time.minute).zfill(2), str(current_time.second).zfill(2))

        # Create new directories to store camera images and processing outputs
        # Includes error checking in case the folder already exist (shouldn't due to the seconds output)
        try:
            os.mkdir('%s' % self.image_folder)
        except WindowsError:
            self.image_folder = self.image_folder + "_2"
            os.mkdir('%s' % self.image_folder)

        # Create respective sub-directories for images
        os.mkdir('%s\scan' % self.image_folder)
        os.mkdir('%s\coat' % self.image_folder)
        os.mkdir('%s\single' % self.image_folder)
        os.mkdir('%s\processed' % self.image_folder)

        # TODO Temporary Variables (To investigate what they do)
        self.part_contours = dict()
        self.initial_flag = True

        # Instantiate and run a MonitorDirectory instance
        self.MD_instance = extra_functions.MonitorDirectory('%s\scan' % self.image_folder, '%s\coat' % self.image_folder)
        self.connect(self.MD_instance, SIGNAL("update_scrollbar_range(QString, QString)"), self.update_scrollbar_range)
        self.MD_instance.start()

    # MENUBAR

    def new_build(self):
        """Opens a Dialog Window when File > New Build... is clicked
        Allows user to setup a new build and change settings
        Setup as a Modal window, blocking input to other visible windows until this window is closed
        """

        # Create the dialog variable and execute it as a modal window
        new_build_dialog = dialog_windows.NewBuild(self)
        successful = new_build_dialog.exec_()

        # Executes the following if the OK button is clicked
        if successful:
            # Load configuration settings from config.json file
            with open('config.json') as config:
                self.config = json.load(config)

            # Store config settings as respective variables and update appropriate UI elements
            self.build_name = self.config['BuildName']
            self.platform_dimensions = self.config['PlatformDimension']
            self.boundary_offset = self.config['BoundaryOffset']
            self.buttonInitialize.setEnabled(True)
            self.setWindowTitle('Defect Monitor - Build ' + str(self.build_name))
            self.update_status('New build created. Click Initialize to begin processing the images.')

    def open_build(self):
        """Opens a Dialog Window when File > Open Build... is clicked
        Allows user to load a previous build's settings
        Setup as a Modal window, blocking input to other visible windows until this window is closed
        """
        pass

    def export_image(self):
        """Opens a FileDialog Window when File > Export Image... is clicked
        Allows the user to save the currently displayed image to whatever location the user specifies as a .png
        """

        # Open a folder select dialog, allowing the user to choose a location and input a name
        self.export_image_name = None
        self.export_image_name = QtGui.QFileDialog.getSaveFileName(self, 'Export Image As', '',
                                                             'Image (*.png)', selectedFilter='*.png')

        # Checking if user has chosen to save the image or clicked cancel
        if self.export_image_name:
            # Check which tab is currently being displayed on the widgetDisplay
            if self.widgetDisplay.currentIndex() == 0:
                cv2.imwrite(str(self.export_image_name), self.image_display_scan)
            elif self.widgetDisplay.currentIndex() == 1:
                cv2.imwrite(str(self.export_image_name), self.image_display_coat)
            else:
                cv2.imwrite(str(self.export_image_name), self.image_display_defect)

            # Open a message box with a save confirmation message
            self.export_confirmation = QtGui.QMessageBox()
            self.export_confirmation.setIcon(QtGui.QMessageBox.Information)
            self.export_confirmation.setText('Your image has been saved to %s.' % self.export_image_name)
            self.export_confirmation.setWindowTitle('Export Image')
            self.export_confirmation.exec_()

    def configuration_settings(self):
        pass

    def camera_settings(self):
        """Opens a Dialog Window when Setup > Camera Settings is clicked
        Allows the user to change camera settings which will be sent to the camera before images are taken
        Setup as a Modeless window, operating independently of other windows
        """

        # Create the dialog variable and execute it as a modeless window
        camera_settings_dialog = dialog_windows.CameraSettings(self)
        camera_settings_dialog.show()

    def defect_processing(self):
        """Executes when the Analyze for Defects button is clicked
        Takes the currently displayed image and applies a bunch of OpenCV code as defined under DefectDetection
        Displays the processed image on the label in the Defect Analyzer tab on the MainWindow
        """

        self.update_progress('0')

        # Check which tab is currently being displayed on the widgetDisplay
        if self.widgetDisplay.currentIndex() == 0:
            image_raw = self.image_display_scan
        elif self.widgetDisplay.currentIndex() == 1:
            image_raw = self.image_display_coat
        else:
            image_raw = None

        # Instantiate a DefectDetection instance
        self.DD_instance = image_processing.DefectDetection(image_raw)

        # Listen for emitted signals from the created instance, and send them to the corresponding method
        self.connect(self.DD_instance, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.DD_instance, SIGNAL("update_progress(QString)"), self.update_progress)

        # Specific signal that moves on to the next task once the current QThread finishes running
        self.connect(self.DD_instance, SIGNAL("defect_processing_finished(PyQt_PyObject, PyQt_PyObject, "
                                              "PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"),
                     self.defect_processing_finished)

        # Start the DefectDetection instance which performs the contained Run method
        self.DD_instance.start()

    def defect_processing_finished(self, image_1, image_2, image_3, image_4, image_5):
        """Executes when the DefectDetection instance has finished"""

        # Saves the processed images in their respective variables
        self.image_defect_1 = image_1
        self.image_defect_2 = image_2
        self.image_defect_3 = image_3
        self.image_defect_4 = image_4
        self.image_defect_5 = image_5

        # Cleanup UI
        self.groupOpenCV.setEnabled(True)
        self.widgetDisplay.setCurrentIndex(2)
        self.update_status('Displaying images...')

        # Display the defect images on the widgetDisplay tab
        self.update_display()

    def slice_converter(self):
        """Opens a Dialog Window when the Slice Converter button is clicked
        Allows the user to convert any slice files from .cls or .cli format into ASCII format
        Setup as a Modal window, blocking input to other visible windows until this window is closed
        """

        self.update_status('')

        # Create the dialog variable and execute it as a modal window
        slice_converter_dialog = dialog_windows.SliceConverter(self)
        slice_converter_dialog.exec_()

    def camera_calibration(self):
        """Opens a Dialog Window when the Camera Calibration button is clicked
        Allows the user to specify a folder of checkboard images to calibrate the attached camera
        Setup as a Modal window, blocking input to other visible windows until this window is closed
        """

        self.update_status('')

        # Create the dialog variable and execute it as a modal window
        camera_calibration_dialog = dialog_windows.CameraCalibration(self)
        camera_calibration_dialog.exec_()

    def defect_actions(self):
        pass

    def display_images(self):
        """Takes the images from the coat and scan folder of the created image folder and displays them
        On their appropriate tabs
        Reads and loads 11 images, the current image plus the previous and next five images into memory
        Allows the user to scroll through the images and jump to specific ones
        Note: The order of the images will be the order that the images are in the folder itself
        The images will need to have proper numbering to ensure that the layer numbers are accurate
        The names of the images themselves are irrelevant to their order within this program
        However they are important within the folder itself for their order
        """

        image_scan_list = os.listdir('%s/scan' % self.image_folder)

        image_coat_list = os.listdir('%s/coat' % self.image_folder)

        if image_scan_list:
            image_scan = cv2.imread('%s/scan/%s' % (self.image_folder, image_scan_list[self.scrollSE.value() - 1]))
            self.labelDisplaySE.setPixmap(self.convert2pixmap(image_scan))
        else:
            self.update_status('Scan image folder empty.')

        if image_coat_list:
            image_coat = cv2.imread('%s/coat/%s' % (self.image_folder, image_coat_list[self.scrollCE.value() - 1]))
            self.labelDisplayCE.setPixmap(self.convert2pixmap(image_coat))
        else:
            if not image_coat_list:
                self.update_status('Scan and Coat image folders empty.')
            else:
                self.update_status('Coat image folder empty.')

    def change_display_image(self):
        """Changes the image being displayed on the Main Window"""
        pass

    def notification_settings(self):
        """Opens a Dialog Window when Setup > Report Settings > Notification Settings is clicked
        Allows user to enter and change the email address and what notifications to be notified of
        Setup as a Modal window, blocking input to other visible windows until this window is closed
        """

        self.update_status('')

        # Create the dialog variable and execute it as a modal window
        notification_settings_dialog = dialog_windows.NotificationSettings(self)
        notification_settings_dialog.exec_()

    # BUTTONS

    def initialize_1(self):
        """Executes when the Initialize button is clicked
        Does the following modules by calling QThreads so that the main window can still be manipulated
        - Converts the .cls or .cli slice files into ASCII format that can be displayed as contours
        - Calibrate and thus acquire the attached camera's intrinsic values
        - Set up the camera for image capture and then capture those images (unless simulation_flag is checked)
        - Apply OpenCV processes to correct the image for camera related issues
        """

        # Enable or disable relevant UI elements to prevent concurrent processes
        self.buttonInitialize.setEnabled(False)
        self.buttonDefectProcessing.setEnabled(False)
        self.groupDisplayOptions.setEnabled(False)
        self.actionExportImage.setEnabled(False)
        self.update_progress(0)
        self.update_display()

        # Reload configuration settings from config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Get the name of the slice file as specified in the New Build dialog
        self.slice_file_name = self.config['WorkingDirectory'] + '/' + self.config['SliceFile']

        # Instantiate a SliceConverter instance and send the slice file name
        self.SC_instance = slice_converter.SliceConverter(self.slice_file_name)

        # Listen for emitted signals from the created instance, and send them to the corresponding method
        self.connect(self.SC_instance, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.SC_instance, SIGNAL("update_progress(QString)"), self.update_progress)

        # Specific signal that moves on to the next task once the current QThread finishes running
        self.connect(self.SC_instance, SIGNAL("finished()"), self.initialize_2)

        # Start the SliceConverter instance which performs the contained Run method
        self.SC_instance.start()

    def initialize_2(self):
        """Method for setting up the camera itself and subsequently acquiring the images
        Able to change a variety of camera settings within the module itself, to be turned into UI element
        If simulation_flag is checked, images are loaded from the samples folder
        """

        self.update_progress(0)

        # Save a copy of the converted slice array in self
        self.slice_parsed = self.SC_instance.slice_parsed

        # Set the maximum of the Layer spinBox to the length of the parsed slice file
        # self.update_layer_range(self.slice_parsed['Max Layer'])

        # Instantiate an ImageCapture instance
        self.ICA_instance = image_capture.ImageCapture(self.image_folder,
                                                       simulation_flag=self.simulation_flag)

        # Listen for emitted signals from the created instance, and send them to the corresponding method
        self.connect(self.ICA_instance, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.ICA_instance, SIGNAL("update_progress(QString)"), self.update_progress)

        # Specific signal that moves on to the next task once the current QThread finishes running
        self.connect(self.ICA_instance, SIGNAL("initialize_3(PyQt_PyObject, PyQt_PyObject)"), self.initialize_3)

        # Start the ImageCapture instance which performs the contained Run method
        self.ICA_instance.start()

    def initialize_3(self, image_scan, image_coat):
        """Method for the initial image processing of the raw scan and coat images for analysis
        Applies the following OpenCV processes in order
        Distortion Correction (D)
        Perspective Warp (P)
        Crop (C)
        clahe (E)
        Respective capital letters suffixed to the image array indicate which processes have been applied
        """

        # Save the received images as instance variables
        self.image_coat = image_coat
        self.image_scan = image_scan

        self.update_progress(0)

        # Instantiate an ImageCorrection instance
        self.ICO_instance = image_processing.ImageCorrection(self.image_folder, self.image_coat, self.image_scan)

        # Listen for emitted signals from the created instance, and send them to the corresponding method
        self.connect(self.ICO_instance, SIGNAL("assign_images(PyQt_PyObject, QString, QString)"), self.assign_images)
        self.connect(self.ICO_instance, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.ICO_instance, SIGNAL("update_progress(QString)"), self.update_progress)

        # Specific signal that moves on to the next task once the current QThread finishes running
        self.connect(self.ICO_instance, SIGNAL("finished()"), self.initialize_finished)

        # Start the ImageCorrection instance which performs the contained Run method
        self.ICO_instance.start()

    def initialize_finished(self):
        """Method for when the entire initialize_build function has finished
        Mainly used to update relevant UI elements
        """

        # Enable or disable relevant UI elements to prevent concurrent processes
        self.buttonInitialize.setEnabled(True)
        self.buttonDefectProcessing.setEnabled(True)
        self.checkToggleOverlay.setEnabled(True)
        self.groupDisplayOptions.setEnabled(True)
        self.actionExportImage.setEnabled(True)
        self.update_progress(100)
        if not self.simulation_flag:
            self.buttonStart.setEnabled(True)

        # Set flag to indicate no longer the initial process
        self.initial_flag = False

        self.convert2contours(1)

        # Update the widgetDisplay to display the processed images
        self.update_display()
        self.update_status('Displaying processed images.')

    def start(self):
        """Executes when the Start button is clicked

        """
        # TODO Stuff that happens when you press the Start button

        # Disable certain UI elements
        pass

    def pause(self):
        pass

    def stop(self):
        pass

    def image_capture(self):
        """Opens a Dialog Window when the Image Capture button is clicked
        Allows the user to capture images from an attached camera, either a single shot or continuously using a trigger
        Setup as a Modeless window, operating independently of other windows
        """

        self.update_status('')

        # Create the dialog variable and execute it as a modeless window
        image_capture_dialog = dialog_windows.ImageCapture(self, self.image_folder)

        # Receive the image name from the ImageCapture Run instance and send it to be displayed
        self.connect(image_capture_dialog, SIGNAL("update_display_iv(QString)"), self.update_display_iv)
        image_capture_dialog.show()

    def image_converter(self):
        """Opens a FileDialog when Image Converter button is pressed
        Prompts the user to select an image to apply image correction on
        Saves the processed image in the same folder
        """

        # Get the name of the image file to be processed
        image_name = QtGui.QFileDialog.getOpenFileName(self, 'Browse...', '', 'Image Files (*.png)')

        # Checking if user has selected a file or clicked cancel
        if image_name:
            self.update_progress(0)
            self.update_status('Processing image...')

            # Read the image
            image_raw = cv2.imread('%s' % image_name)

            # Apply the image processing techniques in order
            image_undistort = image_processing.ImageCorrection(None, None, None).distortion_fix(image_raw)
            self.update_progress(20)
            image_perspective = image_processing.ImageCorrection(None, None, None).perspective_fix(image_undistort)
            self.update_progress(40)
            image_crop = image_processing.ImageCorrection(None, None, None).crop(image_perspective)
            self.update_progress(60)
            image_clahe = image_processing.ImageCorrection(None, None, None).clahe(image_crop)
            self.update_progress(80)

            # Save the cropped image and CLAHE applied image in the same folder after removing .png from the file name
            image_name.replace('.png', '')
            cv2.imwrite('%s_undistort.png' % image_name, image_undistort)
            cv2.imwrite('%s_perspective.png' % image_name, image_perspective)
            cv2.imwrite('%s_crop.png' % image_name, image_crop)
            cv2.imwrite('%s_clahe.png' % image_name, image_clahe)

            self.update_progress(100)
            self.update_status('Image successfully processed.')

    # POSITION ADJUSTMENT BOX

    def toggle_boundary(self):
        """Switches the Position Adjustment arrows to instead control the crop boundary size"""
        pass

    def toggle_crop(self):
        """Switches the Position Adjustment arrows to instead control the crop position"""
        pass

    def shift_up(self):
        pass

    def shift_down(self):
        pass

    def shift_left(self):
        pass

    def shift_right(self):
        pass

    def rotate_acw(self):
        pass

    def rotate_cw(self):
        pass

    # TOGGLES AND CHECKBOXES

    def toggle_overlay(self):
        """Draws the part contour of the current selected layer and displays it on top of the displayed scan image"""

        if self.checkToggleOverlay.isChecked():
            # Creates an empty array to draw contours on
            self.image_overlay = np.zeros(self.image_display_scan.shape).astype(np.uint8)
            self.image_overlay = cv2.cvtColor(self.image_overlay, cv2.COLOR_BGR2RGB)

            # Draws the contours
            for item in self.part_contours:
                cv2.drawContours(self.image_overlay, self.part_contours['PartData']['Contours'],
                                 -1, (255, 0, 0), int(math.ceil(self.scale_factor)))

            cv2.imwrite('overlay.png', self.image_overlay)

            self.update_status('Displaying slice outlines.')

        else:
            self.update_status('Hiding slice outlines.')

        self.update_display()

    def toggle_simulation(self):
        """Checks if the simulation_flag toggle is checked or not, and sets the appropriate boolean as such"""

        if self.checkSimulation.isChecked():
            self.simulation_flag = True
            self.update_status("Program in Simulation Mode.")
        else:
            self.simulation_flag = False
            self.update_status("Program in Camera Mode.")

    # MISCELLANEOUS METHODS

    def assign_images(self, image, phase, tag):
        """Saves the processed image to a different variable depending on the received name tags"""

        if phase == 'scan':
            if tag == 'DP':
                self.image_scan_DP = image
            elif tag == 'DPC':
                self.image_scan_DPC = image
            elif tag == 'DPCE':
                self.image_scan_DPCE = image

        elif phase == 'coat':
            if tag == 'DP':
                self.image_coat_DP = image
            elif tag == 'DPC':
                self.image_coat_DPC = image
            elif tag == 'DPCE':
                self.image_coat_DPCE = image

    def convert2contours(self, layer):
        """Convert the vectors from the parsed slice file into contours which can then be drawn"""

        # Initialize some variables
        min_x = None
        min_y = None
        part_contours = None
        hierarchy = None

        # Save the contours and polyline-indices of the received layer
        layer = int(layer)
        contours = self.slice_parsed[layer]['Contours']
        polyline = self.slice_parsed[layer]['Polyline-Indices']

        # if negative values exist (part is set up in quadrant other than top-right and buildplate centre is (0,0))
        # translate part to positive

        # Finds minimum x and y values over all contours in given part
        for element in xrange(len(polyline)):
            if min_x is None:
                min_x = np.array(contours[polyline[element][0]:polyline[element][2]:2]).astype(np.int32).min()
            else:
                min_x_temp = np.array(contours[polyline[element][0]:polyline[element][2]:2]).astype(np.int32).min()
                if min_x_temp < min_x:
                    min_x = min_x_temp
            if min_y is None:
                min_y = np.array(contours[polyline[element][0] + 1:polyline[element][2]:2]).astype(np.int32).min()
            else:
                min_y_temp = np.array(contours[polyline[element][0] + 1:polyline[element][2]:2]).astype(np.int32).min()
                if min_y_temp < min_y:
                    min_y = min_y_temp

        slice_parsed = self.slice_parsed

        # Image resizing scale factor relating image pixels and part mm
        # Found by dividing the cropped image height by the known platform height
        self.scale_factor = self.image_scan_DPC.shape[0] / self.platform_dimensions[1]

        # Create a blank image the same size and type as the cropped image
        image_blank = np.zeros(self.image_scan_DPC.shape).astype(np.uint8)
        image_contours = image_blank.copy()

        # For each vector in the set of vectors, find the area enclosed by the resultant contours
        # Find the hierarchy of each contour, subtract area if it is an internal contour (i.e. a hole)
        for element in xrange(len(polyline)):

            # Get contours in scaled coordinates (scale_factor * part mm)
            slice_parsed[layer]['Contours'][polyline[element][0]:polyline[element][2]:2] = [
                np.float32(self.scale_factor * (int(x) / 10000. + self.platform_dimensions[0] / 2) + self.boundary_offset[0])
                for x in slice_parsed[layer]['Contours'][polyline[element][0]:polyline[element][2]:2]]

            slice_parsed[layer]['Contours'][(polyline[element][0] + 1):polyline[element][2]:2] = [
                np.float32(self.scale_factor * (-int(y) / 10000. + self.platform_dimensions[1] / 2) + self.boundary_offset[1])
                for y in slice_parsed[layer]['Contours'][polyline[element][0] + 1:polyline[element][2]:2]]

            current_contours = np.array(slice_parsed[layer]['Contours'][polyline[element][0]:polyline[element][2]])\
                .reshape(1, (polyline[element][1]) / 2, 2)

            # Convert the array to int32
            current_contours = current_contours.astype(np.int32)

            # Draw filled polygons on a blank image
            cv2.fillPoly(image_blank, current_contours, (255, 255, 255))

            cv2.imwrite('poly.png', image_blank)

            # If contour overlaps other poly, it is a hole and is subtracted
            image_contours = cv2.bitwise_xor(image_contours, image_blank)
            image_contours = cv2.cvtColor(image_contours, cv2.COLOR_BGR2GRAY)

            cv2.imwrite('contours.png', image_contours)

            # Find and output vectorized contours and their respective hierarchies
            _, part_contours, hierarchy = cv2.findContours(image_contours.copy(), cv2.RETR_CCOMP,
                                                           cv2.CHAIN_APPROX_SIMPLE)
            
        # Save contours to the dictionary
        self.part_contours = {'PartTopleft': (min_x, min_y), 'PartData': {'Contours': part_contours,
                                                                            'Hierarchy': hierarchy}}

        # Save configuration settings to config.json file
        with open('config.json', 'w+') as config:
            json.dump(self.config, config)

    # MISCELLANEOUS UI ELEMENTS

    def set_layer(self):
        """Choose what layer (and overlay) to display"""
        layer = self.spinLayer.value()

        # Displays the current layer number on the UI
        self.labelLayerNumber.setText('%s' % str(layer).zfill(4))

        self.convert2contours(layer)
        self.toggle_overlay()

    def update_display(self):
        """Updates the MainWindow widgetDisplay to show images on their respective labels as per toggles
        Displays the scan image, coat image, defect image
        Images as captured by the Image Capture window are handled in a separate method (update_display_iv)
        Also enables or disables certain UI elements depending on what is toggled
        """

        # This block updates the Scan Explorer and the Coat Explorer tabs
        if self.groupDisplayOptions.isEnabled():
            if self.radioRaw.isChecked():
                self.image_display_scan = self.image_scan
                self.image_display_coat = self.image_coat
                self.groupPositionAdjustment.setEnabled(False)
                self.checkToggleOverlay.setEnabled(False)
                self.checkToggleOverlay.setChecked(False)
                self.buttonDefectProcessing.setEnabled(False)

            elif self.radioCorrection.isChecked():
                self.image_display_scan = self.image_scan_DP
                self.image_display_coat = self.image_coat_DP
                self.groupPositionAdjustment.setEnabled(False)
                self.checkToggleOverlay.setEnabled(False)
                self.checkToggleOverlay.setChecked(False)
                self.buttonDefectProcessing.setEnabled(False)

            elif self.radioCrop.isChecked():
                self.image_display_scan = self.image_scan_DPC
                self.image_display_coat = self.image_coat_DPC
                self.groupPositionAdjustment.setEnabled(True)
                self.checkToggleOverlay.setEnabled(True)
                self.buttonDefectProcessing.setEnabled(False)

            elif self.radioCLAHE.isChecked():
                self.image_display_scan = self.image_scan_DPCE
                self.image_display_coat = self.image_coat_DPCE
                self.groupPositionAdjustment.setEnabled(True)
                self.checkToggleOverlay.setEnabled(True)
                self.buttonDefectProcessing.setEnabled(True)

            # If Toggle Overlay is checked, add the slice overlay on top of the displayed scan image
            if self.checkToggleOverlay.isChecked():
                try:
                    self.image_display_scan = cv2.add(self.image_display_scan, self.image_overlay)
                except:
                    self.toggle_overlay()
                    self.image_display_scan = cv2.add(self.image_display_scan, self.image_overlay)

            # Display the scan and coat images on their respective labels after converting them to pixmap
            self.labelDisplaySE.setPixmap(self.convert2pixmap(self.image_display_scan))
            self.labelDisplayCE.setPixmap(self.convert2pixmap(self.image_display_coat))

        else:
            self.checkToggleOverlay.setEnabled(False)

            # Changes the display window to reflect current process
            if self.initial_flag:
                self.labelDisplaySE.setText("Loading Display...")
                self.labelDisplayCE.setText("Loading Display...")
            else:
                self.labelDisplaySE.setText("Reloading Display...")
                self.labelDisplayCE.setText("Reloading Display...")

        # This block updates the Defect Analyzer tab
        if self.groupOpenCV.isEnabled():
            if self.radioOpenCV1.isChecked(): self.image_display_defect = self.image_defect_1
            if self.radioOpenCV2.isChecked(): self.image_display_defect = self.image_defect_2
            if self.radioOpenCV3.isChecked(): self.image_display_defect = self.image_defect_3
            if self.radioOpenCV4.isChecked(): self.image_display_defect = self.image_defect_4
            if self.radioOpenCV5.isChecked(): self.image_display_defect = self.image_defect_5

            # Display the defect image on its respective label after converting it to pixmap
            self.labelDisplayDA.setPixmap(self.convert2pixmap(self.image_display_defect))

    def update_display_iv(self, image_name):
        """Updates the MainWindow Image Viewer tab display to show images as they are captured during the Run process
        Also enables or disables certain UI elements depending on what is toggled
        """

        # Read the image as dictated by the received image name
        self.image_display_iv = cv2.imread('%s' % image_name)

        # Sets the Image Viewer tab as main focus whenever an image is captured
        self.widgetDisplay.setCurrentIndex(3)

        # Display the captured image on its respective label after converting it to pixmap
        self.labelDisplayIV.setPixmap(self.convert2pixmap(self.image_display_iv))

        self.update_status('Displaying captured image.')

    def convert2pixmap(self, image):
        """Converts the received image into Pixmap format that can be displayed on the label in Qt"""

        # Acquire the image height, width and channels (unneeded) from the image
        height, width, _ = image.shape

        # Convert to pixmap using in-built Qt functions
        q_image = QtGui.QImage(image.data, width, height, 3 * width, QtGui.QImage.Format_RGB888)
        q_pixmap = QtGui.QPixmap.fromImage(q_image)

        return q_pixmap.scaled(self.labelDisplaySE.frameSize().width(), self.labelDisplaySE.frameSize().height(),
                               aspectRatioMode=Qt.KeepAspectRatio)

    def tab_change(self, tab_index):
        """Executes when the focused tab changes to enable a button and change layer values"""

        if tab_index == 0:
            self.labelLayerNumber.setText(str(self.scrollSE.value()))
        elif tab_index == 1:
            self.labelLayerNumber.setText(str(self.scrollCE.value()))

        if not self.initial_flag:
            if tab_index >= 2:
                self.buttonDefectProcessing.setEnabled(False)
            else:
                self.buttonDefectProcessing.setEnabled(True)

    def scrollbar_change(self, value):
        """Executes when the value of the scrollbar changes to then update the tooltip with the new value
        Also updates the relevant layer numbers of specific UI elements and other internal functions
        """
        self.scrollSE.setToolTip('%s' % value)
        self.labelLayerNumber.setText(str(value).zfill(4))
        self.labelLayerNumber.setText(str(value).zfill(4))

    def update_scrollbar_range(self, value, scrollbar):
        """Updates the scrollbar on the right of each of the tabs with a new maximum value"""

        if value is not '1':
            value = int(value) - 1

        # Scan directory
        if scrollbar == '1':
            self.image_scan_range = value
            self.scrollSE.setMaximum(self.image_scan_range)
            if self.widgetDisplay.currentIndex() == 0:
                self.update_layer_range(self.image_scan_range)

        if scrollbar == '2':
            self.image_coat_range = value
            self.scrollCE.setMaximum(self.image_coat_range)

    def update_layer_range(self, value):
        """Updates the Layer spinBox with new range of acceptable values"""
        self.spinLayer.setMaximum(int(value))
        self.spinLayer.setToolTip('1 - %s' % value)

    def update_status(self, string, duration=0):
        """Updates the status bar at the bottom of the Main Window with the received string argument
        Duration refers to how long the message will be displayed in milliseconds
        """
        self.statusBar.showMessage(string, duration)

    def update_progress(self, percentage):
        """Updates the progress bar at the bottom of the Main Window with the received percentage argument"""
        self.progressBar.setValue(int(percentage))

    # CLEANUP

    def closeEvent(self, event):
        """Executes when Menu -> Exit is clicked or the top-right X is clicked"""

        # For some reason it isn't possible to load and dump within the same open function so they're split
        # Load configuration settings from config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Reset the following values back to 'default' values
        self.config['BuildName'] = 'Default'
        self.config['CurrentLayer'] = 0.5
        self.config['CurrentPhase'] = 1
        self.config['CaptureCount'] = 1

        # Save configuration settings to config.json file
        with open('config.json', 'w+') as config:
            json.dump(self.config, config)

        # Delete the created image folder if the Clean Up checkbox is checked
        if self.checkCleanup.isChecked():
            try:
                shutil.rmtree('%s' % self.image_folder)
            except (WindowsError, AttributeError):
                pass


if __name__ == '__main__':
    def main():
        application = QtGui.QApplication(sys.argv)
        interface = MainWindow()
        interface.show()
        sys.exit(application.exec_())


    main()
