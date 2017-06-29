"""
main_window.py
Primary module used to initiate the main GUI window and all its associated dialog/widgets
Only functions that relate to directly manipulating any element of the UI are allowed in this module
All other functions related to image processing etc. are called using QThreads and split into separate modules
List of separate modules:
image_capture.py
image_processing.py
camera_calibration.py
slice_converter.py
"""

# Import built-ins
import os
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
from PyQt4 import QtGui
from PyQt4.QtCore import SIGNAL, Qt

# Import related modules
import slice_converter
import image_capture
import camera_calibration
import image_processing

# Compile and import PyQt GUIs
os.system('build_gui.bat')
from gui import mainWindow, dialogNewBuild, dialogCameraCalibration, dialogSliceConverter


class MainWindow(QtGui.QMainWindow, mainWindow.Ui_mainWindow):
    """Main Window:
    Assigns the following methods to the interactable elements of the UI
    Emcompasses the main window when you open the application
    """

    def __init__(self, parent=None):

        # Setup Main Window UI
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)

        # Set whether this is a simulation or using real camera
        self.simulation = True

        # Get the current working directory
        self.working_directory = os.getcwd()

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        # Menubar -> File
        self.actionNewBuild.triggered.connect(self.new_build)
        self.actionOpenBuild.triggered.connect(self.open_build)
        self.actionExportImage.triggered.connect(self.export_image)
        self.actionExit.triggered.connect(self.closeEvent)

        # Menubar -> Setup
        self.actionConfigurationSettings.triggered.connect(self.configuration_settings)
        self.actionCameraCalibration.triggered.connect(self.camera_calibration)
        self.actionSliceConverter.triggered.connect(self.slice_converter)
        self.actionDefectActions.triggered.connect(self.defect_actions)
        self.actionNotificationSetup.triggered.connect(self.notification_setup)

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
        self.buttonPhase.clicked.connect(self.toggle_phase)
        self.buttonDefectProcessing.clicked.connect(self.defect_processing)
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
        self.buttonSet.clicked.connect(self.set_layer)

        # Display Widget Tabs
        self.widgetDisplay.blockSignals(True)
        self.widgetDisplay.currentChanged.connect(self.tab_change)

        # Load configuration settings from respective .json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Store config settings as respective variables
        self.build_name = self.config['BuildName']
        self.platform_dimensions = self.config['PlatformDimension']
        self.boundary_offset = self.config['BoundaryOffset']

        # Initialize multithreading queues
        # TODO Probably not needed?
        self.queue1 = Queue()
        self.queue2 = Queue()

        # Generate a timestamp for folder labelling purposes
        current_time = datetime.now()
        self.storage_folder_name = """%s-%s-%s [%s''%s'%s]""" % (
            current_time.year, str(current_time.month).zfill(2), str(current_time.day).zfill(2),
            str(current_time.hour).zfill(2), str(current_time.minute).zfill(2), str(current_time.second).zfill(2))

        # Create new directories to store camera images and processing outputs
        # Error checking in case the folder already exist (shouldn't due to the seconds output)
        try:
            os.mkdir('%s' % self.storage_folder_name)
        except WindowsError:
            self.storage_folder_name = self.storage_folder_name + "_2"
            os.mkdir('%s' % self.storage_folder_name)

        os.mkdir('%s/scan' % self.storage_folder_name)
        os.mkdir('%s/coat' % self.storage_folder_name)
        self.storage_folder = {'scan': '%s/scan' % self.storage_folder_name,
                               'coat': '%s/coat' % self.storage_folder_name}

        # Create a temporary folder to store processed images
        try:
            self.image_folder_name = 'images'
            os.mkdir('%s' % self.image_folder_name)
        except WindowsError:
            self.image_folder_name = 'images'

        # Setup input and output slice directories
        self.slice_raw_folder = 'slice_raw'
        self.slice_parsed_folder = 'slice_parsed'

        # Initial current layer
        self.current_layer = 1

        # TODO Temporary Variables (To investigate what they do)
        self.item_dictionary = dict()
        self.initial_flag = True

        # Check if resuming from scan or coat phase
        self.phase_flag = False
        self.current_phase = self.toggle_phase()

    def new_build(self):
        """Opens the New Build Dialog box
        If the OK button is clicked (success), the following processes are executed
        """
        new_build_dialog = NewBuild()
        success = new_build_dialog.exec_()

        if success:
            with open('config.json') as config:
                self.config = json.load(config)

            # Store config settings as respective variables and update appropriate UI elements
            self.build_name = self.config['BuildName']
            self.platform_dimensions = self.config['PlatformDimension']
            self.buttonInitialize.setEnabled(True)
            self.setWindowTitle('Defect Monitor - Build ' + str(self.build_name))
            self.update_status('New build created. Click Initialize to begin processing the images.')

    def open_build(self):
        """Opens the Open Build Dialog box
        If the OK button is clicked (success), the following processes are executed.
        """
        pass

    def export_image(self):
        """Saves the currently displayed image to whatever location the user specifies as a .png"""

        # Opens a folder select dialog, allowing the user to choose a folder
        self.export_filename = None
        self.export_filename = QtGui.QFileDialog.getSaveFileName(self, 'Export Image As', '',
                                                               'Image (*.png)', selectedFilter='*.png')
        if self.export_filename:
            if self.widgetDisplay.currentIndex() == 0:
                cv2.imwrite(str(self.export_filename), self.display_image_scan)
            elif self.widgetDisplay.currentIndex() == 1:
                cv2.imwrite(str(self.export_filename), self.display_image_coat)
            else:
                cv2.imwrite(str(self.export_filename), self.display_image_defect)

            self.export_confirmation = QtGui.QMessageBox()
            self.export_confirmation.setIcon(QtGui.QMessageBox.Information)
            self.export_confirmation.setText('Your image has been saved to %s.' % self.export_filename)
            self.export_confirmation.setWindowTitle('Export Image')
            self.export_confirmation.exec_()

    def configuration_settings(self):

        pass

    def slice_converter(self):
        """Opens the Slice Converter Dialog box
        If the OK button is clicked (success), the following processes are executed
        """

        self.update_status('')
        slice_converter_dialog = SliceConverter()
        slice_converter_dialog.exec_()

    def defect_processing(self):
        """Takes the currently displayed image and applies a bunch of OpenCV code as defined under DefectDetection
        in image_processing.py
        """

        self.update_progress('0')

        if self.widgetDisplay.currentIndex() == 0:
            self.original_image = self.display_image_scan
        elif self.widgetDisplay.currentIndex() == 1:
            self.original_image = self.display_image_coat

        self.defect_detection_instance = image_processing.DefectDetection(self.original_image)
        self.connect(self.defect_detection_instance, SIGNAL("defect_processing_done(PyQt_PyObject, PyQt_PyObject, "
                                                            "PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"),
                                                            self.defect_processing_done)
        self.connect(self.defect_detection_instance, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.defect_detection_instance, SIGNAL("update_progress(QString)"), self.update_progress)
        self.defect_detection_instance.start()

    def defect_processing_done(self, image_1, image_2, image_3, image_4, image_5):

        # Saves the processed images in their respective variables
        self.defect_image_1 = image_1
        self.defect_image_2 = image_2
        self.defect_image_3 = image_3
        self.defect_image_4 = image_4
        self.defect_image_5 = image_5

        # Cleanup UI
        self.groupOpenCV.setEnabled(True)
        self.update_display()
        self.update_status('Displaying images...')
        self.widgetDisplay.setCurrentIndex(2)


    def defect_actions(self):
        pass

    def notification_setup(self):
        pass


    def initialize_1(self):
        """Method that happens when the button "Initialize" is clicked
        Does the following modules by calling QThreads so that the main window can still be manipulated
        - Converts the .cls or .cli slice files into ASCII format that can be displayed as contours
        - Calibrate and thus acquire the attached camera's intrinsic values
        - Set up the camera for image capture and then capture those images (unless simulation is checked)
        - Apply OpenCV processes to correct the image for camera related issues
        """

        # Enables or disables UI elements to prevent concurrent processes
        self.buttonInitialize.setEnabled(False)
        self.groupDisplayOptions.setEnabled(False)
        self.buttonDefectProcessing.setEnabled(False)
        self.widgetDisplay.blockSignals(True)
        self.actionExportImage.setEnabled(False)
        self.update_progress(0)
        self.update_display()

        # Instantiate a SliceConverter instance
        self.slice_converter_instance = slice_converter.SliceConverter(self.slice_raw_folder, self.slice_parsed_folder)

        # Listen for emitted signals from the linked function, and send them to the corresponding methods
        self.connect(self.slice_converter_instance, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.slice_converter_instance, SIGNAL("update_progress(QString)"), self.update_progress)

        # Signal that moves on to the next task
        self.connect(self.slice_converter_instance, SIGNAL("finished()"), self.initialize_2)

        # Run the SliceConverter instance
        self.slice_converter_instance.start()

    def initialize_2(self):
        """Method for setting up the camera itself and subsequently acquiring the images
        Able to change a variety of camera settings within the module itself, to be turned into UI element
        If simulation is checked, images are loaded from the samples folder
        """

        self.update_progress(0)

        # Saves a copy of the converted slice array in self
        self.slice_file_dictionary = self.slice_converter_instance.slice_file_dictionary

        self.image_capture_instance = image_capture.ImageCapture(self.queue1, self.storage_folder, self.simulation)
        self.connect(self.image_capture_instance, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.image_capture_instance, SIGNAL("update_progress(QString)"), self.update_progress)
        self.connect(self.image_capture_instance, SIGNAL("initialize_3(PyQt_PyObject, PyQt_PyObject)"), self.initialize_3)
        #self.connect(self.capture_images, SIGNAL("update_layer(QString, QString)"), self.update_layer)
        self.image_capture_instance.start()

    def initialize_3(self, image_scan, image_coat):
        """Method for the initial image processing of the raw scan and coat images for analysis
        Applies the following OpenCV processes in order
        Distortion Correction (D)
        Perspective Warp (P)
        Crop (C)
        CLAHE (E)
        Respective capital letters suffixed to the image array indicate which processes have been applied
        """

        self.image_scan = image_scan
        self.image_coat = image_coat
        self.update_progress(0)

        self.image_correction_instance = image_processing.ImageCorrection(self.image_folder_name, self.image_scan,
                                                                          self.image_coat)
        self.connect(self.image_correction_instance, SIGNAL("assign_image(PyQt_PyObject, QString, QString)"),
                     self.assign_image)
        self.connect(self.image_correction_instance, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.image_correction_instance, SIGNAL("update_progress(QString)"), self.update_progress)
        self.connect(self.image_correction_instance, SIGNAL("finished()"), self.initialize_done)
        self.image_correction_instance.start()

    def initialize_done(self):
        """Method for when the entire initialize_build function is done
        Mainly used to update relavant UI elements
        """

        # Activate relevant UI elements
        self.checkToggleOverlay.setEnabled(True)
        self.buttonInitialize.setEnabled(True)
        self.buttonDefectProcessing.setEnabled(True)
        self.groupDisplayOptions.setEnabled(True)
        self.widgetDisplay.blockSignals(False)
        self.actionExportImage.setEnabled(True)
        self.update_progress(100)

        self.initial_flag = False

        # Update the main display widget
        self.update_display()
        self.update_status('Displaying processed images.')

        if not self.simulation:
            self.buttonStart.setEnabled(True)

    def toggle_overlay(self):
        """Draws the part contour of the current layer and displays it on top of the current displayed image"""

        if self.checkToggleOverlay.isChecked():
            # Creates an empty array to draw contours on
            self.overlay_image = np.zeros(self.display_image.shape).astype(np.uint8)
            self.overlay_image = cv2.cvtColor(self.overlay_image, cv2.COLOR_BGR2RGB)

            # Draws the contours
            for item in self.item_dictionary:
                cv2.drawContours(self.overlay_image, self.item_dictionary[item]['PartData']['Contours'],
                                 -1, (255, 0, 0), int(math.ceil(self.scale_factor)))
            self.update_status('Displaying slice outlines.')

        else:
            self.update_status('Hiding slice outlines.')

        self.update_display()

    def update_layer(self, layer, phase):
        """Updates the layer number"""

        min_x = None
        min_y = None

        part_contours = None
        hierachy = None

        self.current_layer = int(layer)
        self.current_phase = str(phase)
        
        # Displays the current layer on the UI
        self.labelLayerNumber.setText(str(self.current_layer).zfill(5))
        
        self.config['StartLayer'] = self.current_layer
        self.config['StartPhase'] = self.current_phase
        
        for itemidx, item in enumerate(self.slice_file_dictionary):
            item_contours = self.slice_file_dictionary[item][self.current_layer]['Contours']
            poly_idx = self.slice_file_dictionary[item][self.current_layer]['Polyline-Indices']
            # if negative values exist (part is set up in quadrant other than top-right and buildplate centre is (0,0))
            # translate part to positive

            # finds minimum x and y values over all contours in given part
            for p in xrange(len(poly_idx)):
                if min_x is None:
                    min_x = np.array(item_contours[poly_idx[p][0]:poly_idx[p][2]:2]).astype(np.int32).min()
                else:
                    pot_min_x = np.array(item_contours[poly_idx[p][0]:poly_idx[p][2]:2]).astype(np.int32).min()
                    if pot_min_x < min_x:
                        min_x = pot_min_x
                if min_y is None:
                    min_y = np.array(item_contours[poly_idx[p][0] + 1:poly_idx[p][2]:2]).astype(np.int32).min()
                else:
                    pot_min_y = np.array(item_contours[poly_idx[p][0] + 1:poly_idx[p][2]:2]).astype(np.int32).min()
                    if pot_min_y < min_y:
                        min_y = pot_min_y

            self.adj_dict = self.slice_file_dictionary

            # image resizing factor - relates image pixels and part mm
            # (assumes image is cropped exactly at top and bottom edge of platform)
            scale_height = self.scale_shape[0]
            platform_height = self.platform_dimensions[1]
            self.scale_factor = scale_height / platform_height

            self.boundary_offset = self.config['BoundaryOffset']

            blank_image = np.zeros(self.scale_shape).astype(np.uint8)
            output_image = blank_image.copy()
            # for each vector in the set of vectors, find the area enclosed by the resultant contours
            # find the hierarchy of each contour, subtract area if it is an internal contour (i.e. a hole)
            for p in xrange(len(poly_idx)):
                # gets contours in scaled coordinates (scale_factor * part mm)
                self.adj_dict[item][self.current_layer]['Contours'][poly_idx[p][0]:poly_idx[p][2]:2] = [
                    np.float32(self.scale_factor * (int(x) / 10000. + self.platform_dimensions[0] / 2) + self.boundary_offset[0])
                    for x
                    in
                    self.adj_dict[item][self.current_layer]['Contours'][poly_idx[p][0]:poly_idx[p][2]:2]]
                self.adj_dict[item][self.current_layer]['Contours'][(poly_idx[p][0] + 1):poly_idx[p][2]:2] = [
                    np.float32(self.scale_factor * (-int(y) / 10000. + self.platform_dimensions[1] / 2) + self.boundary_offset[1])
                    for
                    y in
                    self.adj_dict[item][self.current_layer]['Contours'][poly_idx[p][0] + 1:poly_idx[p][2]:2]]

                this_contour = np.array(
                    self.adj_dict[item][self.current_layer]['Contours'][poly_idx[p][0]:poly_idx[p][2]]).reshape(1, (
                    poly_idx[p][1]) / 2, 2)
                this_contour = this_contour.astype(np.int32)
                poly_image = blank_image.copy()
                cv2.fillPoly(poly_image, this_contour, (255, 255, 255))  # draw filled poly on blank image
                # if contour overlaps other poly, it is a hole and is subtracted
                output_image = cv2.bitwise_xor(output_image, poly_image)
                # find vectorised contours and put into 2 level hierarchy (-1 for ext, parent-id for int)
                output_image = cv2.cvtColor(output_image, cv2.COLOR_BGR2GRAY)
                _, part_contours, hierarchy = cv2.findContours(output_image.copy(), cv2.RETR_CCOMP,
                                                               cv2.CHAIN_APPROX_SIMPLE)
            self.item_dictionary[item] = {'PartIdx': itemidx, 'PartTopleft': (min_x, min_y),
                                    'PartData': {'Contours': part_contours, 'Hierarchy': hierarchy}}
        
        with open('config.json','w+') as config:
            json.dump(self.config,config)

    def start(self):
        """Method that happens when you press the "Start" button

        """
        #TODO Stuff that happens when you press the Start button

        # Disable certain UI elements
        pass

    def pause(self):
        pass

    def stop(self):
        pass

    def toggle_simulation(self):
        """Checks if the simulation toggle is checked or not, and sets the appropriate boolean as such"""
        if self.checkSimulation.isChecked():
            self.simulation = True
            self.update_status("Program in Simulation Mode.")
        else:
            self.simulation = False
            self.update_status("Program in Camera Mode.")

    def toggle_phase(self):
        """Toggles the current 3D printing machine phase to either:
        Scan: Analyzed image will be after the scanning phase.
        Coat: Analyzed image will be after the coating phase.
        """

        # Toggles the phase flag, and does the appropriate actions
        self.phase_flag = not self.phase_flag

        if self.phase_flag:
            self.buttonPhase.setText('SCAN')
            current_phase = 'scan'
        else:
            self.buttonPhase.setText('COAT')
            current_phase = 'coat'
        return current_phase

    def tab_change(self, tab_index):
        if tab_index == 2:
            self.buttonDefectProcessing.setEnabled(False)
        else:
            self.buttonDefectProcessing.setEnabled(True)

    def camera_calibration(self):
        """Opens the Camera Calibration Dialog box
        If the OK button is clicked (success), the following processes are executed
        """
        self.update_status('')
        camera_calibration_dialog = CameraCalibration()
        camera_calibration_dialog.exec_()

    # Position Adjustment Box

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

    def set_layer(self):
        pass


    # Miscellaneous Methods

    def assign_image(self, image, phase, tag):
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

    # Miscellaneous UI Elements

    def update_display(self):
        """Update the MainWindow display to show images as per toggles
        Displays the scan image and the coat image in their respective tabs
        Also enables or disables certain UI elements depending on what is toggled
        """

        # This if block updates the Scan Explorer and the Coat Explorer tabs
        if self.groupDisplayOptions.isEnabled():
            if self.radioRaw.isChecked():
                self.display_image_scan = self.image_scan
                self.display_image_coat = self.image_coat
                self.groupPositionAdjustment.setEnabled(False)
                self.checkToggleOverlay.setEnabled(False)
                self.checkToggleOverlay.setChecked(False)
                self.buttonDefectProcessing.setEnabled(False)

            elif self.radioCorrection.isChecked():
                self.display_image_scan = self.image_scan_DP
                self.display_image_coat = self.image_coat_DP
                self.groupPositionAdjustment.setEnabled(False)
                self.checkToggleOverlay.setEnabled(False)
                self.checkToggleOverlay.setChecked(False)
                self.buttonDefectProcessing.setEnabled(False)

            elif self.radioCrop.isChecked():
                self.display_image_scan = self.image_scan_DPC
                self.display_image_coat = self.image_coat_DPC
                self.groupPositionAdjustment.setEnabled(True)
                self.checkToggleOverlay.setEnabled(True)
                self.buttonDefectProcessing.setEnabled(False)

            elif self.radioCLAHE.isChecked():
                self.display_image_scan = self.image_scan_DPCE
                self.display_image_coat = self.image_coat_DPCE
                self.groupPositionAdjustment.setEnabled(True)
                self.checkToggleOverlay.setEnabled(True)
                self.buttonDefectProcessing.setEnabled(True)

            if self.checkToggleOverlay.isChecked():
                try:
                    self.display_image_scan = cv2.add(self.display_image_scan, self.overlay_image)
                    self.display_image_coat = cv2.add(self.display_image_coat, self.overlay_image)
                except:
                    self.toggle_overlay()
                    self.display_image_scan = cv2.add(self.display_image_scan, self.overlay_image)
                    self.display_image_coat = cv2.add(self.display_image_coat, self.overlay_image)

            height, width, _ = self.display_image_scan.shape
            bytesPerLine = 3 * width

            # Convert the scan and coat images into pixmap format so that they can be displayed using QLabels
            self.qImg_scan = QtGui.QImage(self.display_image_scan.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
            self.qPxm_scan = QtGui.QPixmap.fromImage(self.qImg_scan)
            self.qPxm_scan = self.qPxm_scan.scaled(987, 605, aspectRatioMode=Qt.KeepAspectRatio)
            self.labelDisplaySE.setPixmap(self.qPxm_scan)

            self.qImg_coat = QtGui.QImage(self.display_image_coat.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
            self.qPxm_coat = QtGui.QPixmap.fromImage(self.qImg_coat)
            self.qPxm_coat = self.qPxm_coat.scaled(987, 605, aspectRatioMode=Qt.KeepAspectRatio)
            self.labelDisplayCE.setPixmap(self.qPxm_coat)

        else:
            self.checkToggleOverlay.setEnabled(False)

            # Changes the display window to reflect current process
            if self.initial_flag:
                self.labelDisplaySE.setText("Loading Display...")
                self.labelDisplayCE.setText("Loading Display...")
            else:
                self.labelDisplaySE.setText("Reloading Display...")
                self.labelDisplayCE.setText("Reloading Display...")

        # This if block updates the Defect Analyzer tab
        if self.groupOpenCV.isEnabled():
            if self.radioOpenCV1.isChecked():
                self.display_image_defect = self.defect_image_1
            if self.radioOpenCV2.isChecked():
                self.display_image_defect = self.defect_image_2
            if self.radioOpenCV3.isChecked():
                self.display_image_defect = self.defect_image_3
            if self.radioOpenCV4.isChecked():
                self.display_image_defect = self.defect_image_4
            if self.radioOpenCV5.isChecked():
                self.display_image_defect = self.defect_image_5

            height, width, _ = self.display_image_defect.shape
            bytesPerLine = 3 * width

            self.qImg_defect = QtGui.QImage(self.display_image_defect.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
            self.qPxm_defect = QtGui.QPixmap.fromImage(self.qImg_defect)
            self.qPxm_defect = self.qPxm_defect.scaled(987, 605, aspectRatioMode=Qt.KeepAspectRatio)
            self.labelDisplayDA.setPixmap(self.qPxm_defect)

    def update_status(self, string):
        """Updates the status bar at the bottom of the Main Window with the sent string argument"""
        self.statusBar.showMessage(string)
        return

    def update_progress(self, percentage):
        """Updates the progress bar at the bottom of the Main Window with the sent percentage argument"""
        self.progressBar.setValue(int(percentage))
        return

    def closeEvent(self, event):
        """When either the Exit button or the top-right X is pressed, these processes happen:
        Erase the current build name.
        Delete any created folders.
        """
        with open('config.json', 'w+') as config:
            self.config['BuildName'] = ""
            json.dump(self.config, config)

        # Deleting the created folders (for simulation purposes)
        if self.simulation:
            try:
                shutil.rmtree('%s' % self.storage_folder_name)
                shutil.rmtree('images')
                try:
                    shutil.rmtree('%s' % self.image_folder_name)
                except AttributeError:
                    pass
            except WindowsError:
                pass


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
        self.buttonBrowse.setEnabled(False)

    def update_status(self, string):
        self.labelProgress.setText(string)
        return

    def update_progress(self, percentage):
        self.progressBar.setValue(int(percentage))
        return

    def accept(self):
        """If you press the 'done' button, this just closes the dialog window without doing anything"""
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

    def conversion_done(self):
        pass

    def update_status(self, string):
        self.labelProgress.setText(string)
        return

    def update_progress(self, percentage):
        self.progressBar.setValue(int(percentage))
        return

    def accept(self):
        """If you press the 'done' button, this just closes the dialog window without doing anything"""
        self.done(1)

if __name__ == '__main__':
    def main():
        application = QtGui.QApplication(sys.argv)
        interface = MainWindow()
        interface.show()
        sys.exit(application.exec_())

    main()