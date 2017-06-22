"""
main.py
Primary module used to initiate the main GUI window and all its associated dialog/widgets
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
import image_processing
import image_capture
import slice_converter

# Compile and import PyQt GUIs
os.system('build_gui.bat')
from gui import mainWindow, dialogNewBuild


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

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        # Menubar -> File
        self.actionNewBuild.triggered.connect(self.new_build)
        self.actionOpenBuild.triggered.connect(self.open_build)
        self.actionExportImage.triggered.connect(self.export_image)
        self.actionExit.triggered.connect(self.closeEvent)

        # Menubar -> Setup
        self.actionConfigurationSettings.triggered.connect(self.configuration_settings)
        self.actionCLS.triggered.connect(self.select_CLS)
        self.actionCLI.triggered.connect(self.select_CLI)
        self.actionAdjustCrop.triggered.connect(self.crop_adjustment)
        self.actionAdjustRotation.triggered.connect(self.rotation_adjustment)
        self.actionDefectActions.triggered.connect(self.defect_actions)
        self.actionNotificationSetup.triggered.connect(self.notification_setup)

        # Menubar -> Run
        self.actionInitializeBuild.triggered.connect(self.convert_slice)
        self.actionStartBuild.triggered.connect(self.start_setup)
        self.actionPauseBuild.triggered.connect(self.pause_build)
        self.actionStopBuild.triggered.connect(self.stop_build)

        # Buttons
        self.buttonInitialize.clicked.connect(self.convert_slice)
        self.buttonStart.clicked.connect(self.start_setup)
        self.buttonPause.clicked.connect(self.pause_build)
        self.buttonStop.clicked.connect(self.stop_build)
        self.buttonPhase.clicked.connect(self.toggle_phase)

        # Toggles
        self.checkSimulation.toggled.connect(self.toggle_simulation)

        # Load configuration settings from respective .json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Store config settings as respective variables
        self.build_name = self.config['BuildName']
        self.platform_dimensions = self.config['PlatformDimension']
        self.boundary_offset = self.config['BoundaryOffset']

        # Initialize multithreading queues
        self.queue1 = Queue()
        self.queue2 = Queue()

        # Generate a timestamp for folder labelling purposes
        current_time = datetime.now()
        self.folder_name = """%s-%s-%s [%s''%s'%s]""" % (
            current_time.year, str(current_time.month).zfill(2), str(current_time.day).zfill(2),
            str(current_time.hour).zfill(2), str(current_time.minute).zfill(2), str(current_time.second).zfill(2)
        )

        # Create new directories to store camera images and processing outputs
        # Error checking in case the folder already exist (shouldn't due to the seconds output)
        try:
            os.mkdir('%s' % (self.folder_name))
        except WindowsError:
            self.folder_name = self.folder_name + "_2"
            os.mkdir('%s' % (self.folder_name))

        os.mkdir('%s/scan' % (self.folder_name))
        os.mkdir('%s/coat' % (self.folder_name))
        self.storage_folder = {'scan': '%s/scan' % (self.folder_name),
                               'coat': '%s/coat' % (self.folder_name)}

        # Create a temporary folder to store processed images
        try:
            os.mkdir('images')
        except WindowsError:
            os.mkdir('images' + str(current_time.second).zfill(2))

        # Setup input and output slice directories
        self.slice_raw_folder = 'slice_raw'
        self.slice_parsed_folder = 'slice_parsed'

        # Initial current layer
        self.current_layer = 1

        #TODO Temporary Variables (To investigate what they do)
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
        pass

    def configuration_settings(self):
        pass

    def select_CLS(self):
        pass

    def select_CLI(self):
        pass

    def crop_adjustment(self):
        pass

    def rotation_adjustment(self):
        pass

    def defect_actions(self):
        pass

    def notification_setup(self):
        pass


    def convert_slice(self):
        """Process that happens when the button "Initialize" is clicked
        Converts the .cls or .cli file into ASCII format that can be read by OpenCV
        setup_parts
        """

        # Enables or disables UI elements to prevent concurrent processes, almost clears progress bar and the display
        self.buttonInitialize.setEnabled(False)
        self.groupDisplayOptions.setEnabled(False)
        self.update_progress(0)
        self.update_display()

        # Instantiate a SliceConverter class
        self.slice_conversion = slice_converter.SliceConverter(self.slice_raw_folder, self.slice_parsed_folder)

        # Listen for emitted signals from the linked function, and send them to the corresponding methods
        self.connect(self.slice_conversion, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.slice_conversion, SIGNAL("update_progress(QString)"), self.update_progress)

        # This specific signal moves on to the next task
        self.connect(self.slice_conversion, SIGNAL("finished()"), self.initial_setup)

        # Run the SliceConverter QThread
        self.slice_conversion.start()

    def initial_setup(self):
        """Setup necessary QThreads and UI elements, subsequently calling them
        setup_cascade
        """

        # Saves a copy of the converted slice array in self
        self.slice_file_dictionary = self.slice_conversion.slice_file_dictionary

        # Instantiate a ImageCapture class
        self.capture_images = image_capture.ImageCapture(self.queue1, self.storage_folder, self.simulation)

        # Listen for emitted signals from the linked function, and send them to the corresponding methods
        self.connect(self.capture_images, SIGNAL("update_status(QString)"), self.update_status)
        self.connect(self.capture_images, SIGNAL("initial_processing(PyQt_PyObject, PyQt_PyObject)"), self.initial_processing)
        self.connect(self.capture_images, SIGNAL("update_layer(QString, QString)"), self.update_layer)

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        self.radioRaw.toggled.connect(self.update_display)
        self.radioCorrection.toggled.connect(self.update_display)
        self.radioCrop.toggled.connect(self.update_display)
        self.radioCLAHE.toggled.connect(self.update_display)
        self.checkToggleOverlay.toggled.connect(self.toggle_overlay)
        self.buttonBoundary.toggled.connect(self.toggle_boundary)
        self.buttonCrop.toggled.connect(self.toggle_crop)
        self.buttonShiftUp.clicked.connect(self.shift_up)
        self.buttonShiftDown.clicked.connect(self.shift_down)
        self.buttonShiftLeft.clicked.connect(self.shift_left)
        self.buttonShiftRight.clicked.connect(self.shift_right)
        self.buttonRotateACW.clicked.connect(self.rotate_acw)
        self.buttonRotateCW.clicked.connect(self.rotate_cw)
        self.buttonSet.clicked.connect(self.set_layer)

        # Run the Capture thread

        self.capture_images.start()

        if not self.simulation:
            self.buttonStart.setEnabled(True)

    def initial_processing(self, image_scan, image_coat):
        """Method for the initial image processing of the raw scan and coat images for analysis
        Applies the following OpenCV processes in order
        Distortion Correction (D)
        Perspective Warp (P)
        Crop (C)
        CLAHE (E)
        Respective capital letters suffixed to the image array indicate which processes have been applied
        display_image
        """
        self.image_scan = image_scan
        self.image_coat = image_coat

        self.update_progress(0)

        self.update_progress(12.5)
        self.update_status('Fixing Distortion & Perspective...')
        self.image_scan_D = image_processing.ImageCorrection(None, None, self.capture_images.new_parameters).distortion_fix(self.image_scan)
        self.image_scan_DP = image_processing.ImageCorrection(None, None, self.capture_images.new_parameters).perspective_fix(self.image_scan_D)

        cv2.imwrite('images/sample_scan_DP.png', self.image_scan_DP)

        self.update_progress(25)
        self.update_status('Cropping image...')
        self.image_scan_DPC = image_processing.ImageCorrection(None, None, self.capture_images.new_parameters).crop(self.image_scan_DP)
        self.scale_shape = self.image_scan_DPC.shape

        cv2.imwrite('images/sample_scan_DPC.png', self.image_scan_DPC)

        self.update_progress(37)
        self.update_status('Applying CLAHE algorithm...')
        self.image_scan_DPCE = image_processing.ImageCorrection(None, None, self.capture_images.new_parameters).CLAHE(self.image_scan_DPC)

        cv2.imwrite('images/sample_scan_DPCE.png', self.image_scan_DPCE)

        self.update_progress(50)

        self.update_progress(62)
        self.update_status('Fixing Distortion & Perspective...')
        self.image_coat_D = image_processing.ImageCorrection(None, None, self.capture_images.new_parameters).distortion_fix(self.image_coat)
        self.image_coat_DP = image_processing.ImageCorrection(None, None, self.capture_images.new_parameters).perspective_fix(self.image_coat_D)

        cv2.imwrite('images/scample_coat_DP.png', self.image_coat_DP)

        self.update_progress(75)
        self.update_status('Cropping image...')
        self.image_coat_DPC = image_processing.ImageCorrection(None, None, self.capture_images.new_parameters).crop(self.image_coat_DP)
        self.scale_shape = self.image_coat_DPC.shape

        cv2.imwrite('images/scample_coat_DPC.png', self.image_coat_DPC)

        self.update_progress(87)
        self.update_status('Applying CLAHE algorithm...')
        self.image_coat_DPCE = image_processing.ImageCorrection(None, None, self.capture_images.new_parameters).CLAHE(self.image_coat_DPC)

        cv2.imwrite('images/scample_coat_DPCE.png', self.image_coat_DPCE)

        self.update_progress(100)

        # Activate relevant UI elements
        self.checkToggleOverlay.setEnabled(True)
        self.buttonInitialize.setEnabled(True)
        self.groupDisplayOptions.setEnabled(True)

        self.initial_flag = False

        # Update the main display widget
        self.update_display()
        self.update_status('Displaying processed image.')


    def update_display(self):
        """Update the MainWindow display to show images as per toggles
        Displays the scan image and the coat image in their respective tabs
        Asso enables or disables certain UI elements depending on what is toggled
        change_disp
        """
        if self.groupDisplayOptions.isEnabled():
            if self.radioRaw.isChecked():
                self.display_image_scan = self.image_scan
                self.display_image_coat = self.image_coat
                self.groupPositionAdjustment.setEnabled(False)
                self.checkToggleOverlay.setEnabled(False)
                self.checkToggleOverlay.setChecked(False)

            elif self.radioCorrection.isChecked():
                self.display_image_scan = self.image_scan_DP
                self.display_image_coat = self.image_coat_DP
                self.groupPositionAdjustment.setEnabled(False)
                self.checkToggleOverlay.setEnabled(False)
                self.checkToggleOverlay.setChecked(False)

            elif self.radioCrop.isChecked():
                self.display_image_scan = self.image_scan_DPC
                self.display_image_coat = self.image_coat_DPC
                self.groupPositionAdjustment.setEnabled(True)
                self.checkToggleOverlay.setEnabled(True)

            elif self.radioCLAHE.isChecked():
                self.display_image_scan = self.image_scan_DPCE
                self.display_image_coat = self.image_coat_DPCE
                self.groupPositionAdjustment.setEnabled(True)
                self.checkToggleOverlay.setEnabled(True)

            if self.checkToggleOverlay.isChecked():
                try:
                    self.display_image_scan = cv2.add(self.display_image_scan, self.overlay_image)
                    self.display_image_coat = cv2.add(self.display_image_coat, self.overlay_image)
                except:
                    self.toggle_overlay()
                    self.display_image_scan = cv2.add(self.display_image_scan, self.overlay_image)
                    self.display_image_coat = cv2.add(self.display_image_coat, self.overlay_image)

            height, width, channel = self.display_image_scan.shape
            bytesPerLine = 3 * width

            self.qImg_scan = QtGui.QImage(self.display_image_scan.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
            self.qPxm_scan = QtGui.QPixmap.fromImage(self.qImg_scan)
            self.qPxm_scan = self.qPxm_scan.scaled(1052, 592, aspectRatioMode=Qt.KeepAspectRatio)

            self.qImg_coat = QtGui.QImage(self.display_image_coat.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
            self.qPxm_coat = QtGui.QPixmap.fromImage(self.qImg_coat)
            self.qPxm_coat = self.qPxm_coat.scaled(1052, 592, aspectRatioMode=Qt.KeepAspectRatio)

            self.labelDisplaySE.setPixmap(self.qPxm_scan)
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

    def start_setup(self):
        """Process that happens when you press the "Start" button

        """
        #TODO Stuff that happens when you press the Start button

        # Disable certain UI elements
        pass

    def pause_build(self):
        pass

    def stop_build(self):
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
                shutil.rmtree('%s' % (self.folder_name))
                shutil.rmtree('images')
            except WindowsError:
                pass




class NewBuild(QtGui.QDialog, dialogNewBuild.Ui_dialogNewBuild):
    """
    Opens a Dialog Window:
    When File > New Build... is clicked.
    """

    def __init__(self, parent=None):

        #
        super(NewBuild, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)

        #QtGui.QDialog.__init__(self)
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
