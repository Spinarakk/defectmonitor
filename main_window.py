# Import libraries and modules
import os
import sys
import subprocess
import json
import cv2
import serial
import bisect
import math
import time

# Import PyQt modules
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

# Compile UI files, can be disabled if UIs have been finalized to reduce startup time
uic.compileUiDir('gui')

# # Import related modules
import dialog_windows
import image_capture
import image_processing
import slice_converter
import extra_functions
import qt_multithreading

# Import PyQt GUIs
from gui import mainWindow


class MainWindow(QMainWindow, mainWindow.Ui_mainWindow):
    """Main module used to initiate the main GUI window and all of its associated dialogs/widgets
    Only methods that relate directly manipulating any element of the MainWindow UI are allowed in this module
    All other functions related to image processing etc. are called using QThreads and split into separate modules
    All dialog windows are found and called in the dialog_windows.py
    Note: All QSomeName namespaces are from either the PyQt4.QtGui or PyQt4.QtCore module, including pyqtSignal
    """

    def __init__(self, parent=None):

        # Setup Main Window UI
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)

        # Load default build settings from the hidden non-user accessible build_default.json file
        with open('build_default.json') as build:
            self.build = json.load(build)

        # Load config settings from the hidden non-user accessible config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Get the current working directory and save it to the config.json file so later methods can grab it
        # Additionally, create a default builds folder (if it doesn't exist) using the cwd to store images
        self.build['WorkingDirectory'] = os.getcwd().replace('\\', '/')
        self.build['BuildInfo']['Folder'] = os.path.dirname(self.build['WorkingDirectory']) + '/Builds'
        if not os.path.isdir(self.build['BuildInfo']['Folder']):
            os.makedirs(self.build['BuildInfo']['Folder'])

        # Save the default build to the current working build.json file (using w+ in case file doesn't exist)
        with open('build.json', 'w+') as build:
            json.dump(self.build, build, indent=4, sort_keys=True)

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        # Menubar -> File
        self.actionNew.triggered.connect(self.new_build)
        self.actionOpen.triggered.connect(self.open_build)
        self.actionClearMenu.triggered.connect(self.clear_menu)
        self.actionSave.triggered.connect(self.save_build)
        self.actionSaveAs.triggered.connect(self.save_as_build)
        self.actionExportImage.triggered.connect(self.export_image)
        self.actionQuit.triggered.connect(self.closeEvent)

        # Menubar -> View
        self.actionZoomIn.triggered.connect(self.zoom_in)
        self.actionZoomOut.triggered.connect(self.zoom_out)
        self.actionCalibrationResults.triggered.connect(self.calibration_results)
        self.actionDefectReports.triggered.connect(self.defect_reports)
        self.actionHistogramComparison.triggered.connect(self.histogram_comparison)

        # Menubar -> Tools
        self.actionCameraCalibration.triggered.connect(self.camera_calibration)
        self.actionOverlayAdjustment.triggered.connect(self.overlay_adjustment)
        self.actionSliceConverter.triggered.connect(self.slice_converter)
        self.actionImageConverter.triggered.connect(self.image_converter)
        self.actionUpdateFolders.triggered.connect(self.update_folders)
        self.actionUpdateFolders.triggered.connect(lambda: self.update_status('Image folders updated.', 3000))
        self.actionProcessCurrent.triggered.connect(self.process_current)
        self.actionProcessAll.triggered.connect(self.process_all)
        self.actionProcessSelected.triggered.connect(self.process_selected)

        # Menubar -> Settings
        self.actionCameraSettings.triggered.connect(self.camera_settings)
        self.actionBuildSettings.triggered.connect(self.build_settings)
        self.actionAdvancedMode.triggered.connect(self.advanced_mode)

        # Menubar -> Help
        self.actionViewHelp.triggered.connect(self.view_help)
        self.actionAbout.triggered.connect(self.view_about)

        # Display Options Group Box
        self.radioOriginal.clicked.connect(self.update_display)
        self.radioDefects.clicked.connect(self.update_display)
        self.checkCLAHE.toggled.connect(self.update_display)
        self.checkOverlay.toggled.connect(self.toggle_overlay)
        self.checkPartNames.toggled.connect(self.toggle_part_names)

        # Sidebar Toolbox Assorted Tools
        self.pushCameraCalibration.clicked.connect(self.camera_calibration)
        self.pushOverlayAdjustment.clicked.connect(self.overlay_adjustment)
        self.pushImageConverter.clicked.connect(self.image_converter)

        # Sidebar Toolbox Slice Conversion
        self.pushPauseConversion.clicked.connect(self.pause_conversion)
        self.pushStopConversion.clicked.connect(self.setup_build_finished)
        self.pushSliceConverter.clicked.connect(self.slice_converter)

        # Sidebar Toolbox Defect Processor
        self.pushProcessCurrent.clicked.connect(self.process_current)
        self.pushProcessAll.clicked.connect(self.process_all)
        self.pushProcessSelected.clicked.connect(self.process_selected)

        # Sidebar Toolbox Reports / Results
        self.pushCalibrationResults.clicked.connect(self.calibration_results)
        self.pushDefectReports.clicked.connect(self.defect_reports)
        self.pushHistogramComparison.clicked.connect(self.histogram_comparison)

        # Layer Selection
        self.pushGo.clicked.connect(self.set_layer)

        # Image Capture
        self.pushAcquireCT.clicked.connect(self.acquire_ct)
        self.pushCapture.clicked.connect(self.capture_single)
        self.pushFauxTrigger.clicked.connect(lambda: self.capture_run('TRIG'))
        self.pushRun.clicked.connect(self.run_build)
        self.pushPauseResume.clicked.connect(self.pause_build)
        self.pushStop.clicked.connect(self.stop_build)

        # Display Widget
        self.widgetDisplay.currentChanged.connect(self.tab_change)
        self.graphicsCE.zoom_done.connect(self.zoom_in_reset)
        self.graphicsSE.zoom_done.connect(self.zoom_in_reset)
        self.graphicsPC.zoom_done.connect(self.zoom_in_reset)
        self.graphicsIC.zoom_done.connect(self.zoom_in_reset)
        self.graphicsCE.customContextMenuRequested.connect(self.context_menu_display)
        self.graphicsSE.customContextMenuRequested.connect(self.context_menu_display)
        self.graphicsPC.customContextMenuRequested.connect(self.context_menu_display)
        self.graphicsIC.customContextMenuRequested.connect(self.context_menu_display)

        # Sliders
        self.sliderDisplay.valueChanged.connect(self.slider_change)
        self.pushDisplayUp.clicked.connect(self.slider_up)
        self.pushDisplayUpSeek.clicked.connect(self.slider_up_seek)
        self.pushDisplayDown.clicked.connect(self.slider_down)
        self.pushDisplayDownSeek.clicked.connect(self.slider_down_seek)

        # Flags for various conditions
        self.display_flag = False
        self.processing_flag = False
        self.all_flag = False

        # Instantiate any instances that cannot be run simultaneously
        self.FM_instance = None

        # Instantiate dialog variables that cannot have multiple windows for existence validation purposes
        self.DR_dialog = None
        self.CC_dialog = None
        self.OA_dialog = None
        self.SC_dialog = None
        self.CS_dialog = None

        # Initiate an empty config file name to be used for saving purposes
        self.build_name = None

        # Initialize the counter for the defect processing method
        self.defect_counter = 0

        # Create a context menu that will appear when the user right-clicks on any of the display labels
        self.menu_display = QMenu()

        # Disable the Image Viewer tab permanently
        self.widgetDisplay.setTabEnabled(3, False)

        # Because each tab on the widgetDisplay has its own set of associated images, display labels and sliders
        # And because they all do essentially the same functions
        # Easier to store each of these in a dictionary under a specific key to call on one of the four sets
        # The current tab's index will be used to grab the corresponding image, list or name
        self.display = {'ImageList': [list(), list(), list(), list(), list(), list(), list(), list()], 'MaxLayers': 1,
                        'FolderNames': ['Coat/', 'Scan/', 'Contour/', 'Single/'], 'CurrentLayer': [1, 1, 1, 1],
                        'LayerNumbers': [list(), list(), list(), list(), list(), list(), list(), list()],
                        'StackNames': [self.stackedCE, self.stackedSE, self.stackedPC, self.stackedIC],
                        'LabelNames': [self.labelCE, self.labelSE, self.labelPC, self.labelIC],
                        'GraphicsNames': [self.graphicsCE, self.graphicsSE, self.graphicsPC, self.graphicsIC],
                        'DisplayImage': [0, 0, 0, 0]}

        # Create a QThreadPool which contains an amount of threads that can be used to simultaneously run functions
        self.threadpool = QThreadPool()

    # MENUBAR -> FILE

    def new_build(self):
        """Opens a Modal Dialog Window when File -> New... is clicked
        Allows the user to setup a new build and change settings
        """

        # Create a new build dialog variable and execute it as a modal window
        NB_dialog = dialog_windows.NewBuild(self)

        # Executes the following if the OK button is clicked, otherwise nothing happens
        if NB_dialog.exec_():
            self.setup_build()

    def open_build(self):
        """Opens a File Dialog when File -> Open... is clicked
        Allows the user to select a previous build's settings
        Subsequently opens the New Build Dialog Window with all the boxes filled in, allowing the user to make changes
        """

        # Acquire the name of the config file to be opened and read
        filename = QFileDialog.getOpenFileName(self, 'Browse...', self.build['BuildInfo']['Folder'],
                                               'JSON File (*.json)')[0]

        # Check if a file has been selected as QFileDialog returns an empty string if cancel was pressed
        if filename:
            # Load from the selected build file and overwrite the contents of the working build dictionary
            with open(filename) as build:
                self.build = json.load(build)

            # Save to the build.json file
            with open('build.json', 'w+') as build:
                json.dump(self.build, build, indent=4, sort_keys=True)

            self.build_name = filename

            OB_dialog = dialog_windows.NewBuild(self, open_flag=True)

            if OB_dialog.exec_():
                self.setup_build()

    def setup_build(self, settings_flag=False):
        """Sets up the widgetDisplay and any background processes for the current build"""

        # Reload any modified build settings that the New Build dialog has changed
        with open('build.json') as build:
            self.build = json.load(build)

        # Store config settings as respective variables and update appropriate UI elements
        self.setWindowTitle('Defect Monitor - Build ' + self.build['BuildInfo']['Name'])

        # Don't do the following if this method was triggered by changing the build settings
        if not settings_flag:
            # Enable certain UI elements
            self.actionSave.setEnabled(True)
            self.actionSaveAs.setEnabled(True)
            self.actionBuildSettings.setEnabled(True)
            self.pushAcquireCT.setEnabled(True)
            self.pushDefectReports.setEnabled(True)
            self.actionDefectReports.setEnabled(True)

            # Store the names of the seven folders (one is a spacer) to be monitored in the display dictionary
            self.display['ImageFolder'] = ['%s/processed/coat' % self.build['ImageCapture']['Folder'],
                                           '%s/processed/scan' % self.build['ImageCapture']['Folder'],
                                           '%s/contours' % self.build['ImageCapture']['Folder'],
                                           '%s/processed/single' % self.build['ImageCapture']['Folder'],
                                           '%s/defects/coat' % self.build['ImageCapture']['Folder'],
                                           '%s/defects/scan' % self.build['ImageCapture']['Folder'],
                                           '%s/defects' % self.build['ImageCapture']['Folder'],
                                           '%s/defects/single' % self.build['ImageCapture']['Folder']]

            # Start the image viewer to begin displaying images
            self.start_display()

        # Converts and draws the contours if set to do so in the build settings
        if self.build['BuildInfo']['Convert']:
            # Set the appropriate flags in the config.json file to run the slice conversion
            self.build['BuildInfo']['Pause'] = False
            self.build['BuildInfo']['Run'] = True
            self.build['SliceConverter']['Build'] = True

            # Save to the build.json file
            with open('build.json', 'w+') as build:
                json.dump(self.build, build, indent=4, sort_keys=True)

            self.pushPauseConversion.setEnabled(True)
            self.pushStopConversion.setEnabled(True)
            self.toolSidebar.setCurrentIndex(1)

            worker = qt_multithreading.Worker(slice_converter.SliceConverter().run_converter)
            worker.signals.status.connect(self.update_status)
            worker.signals.progress.connect(self.update_progress)
            worker.signals.finished.connect(lambda: self.setup_build_finished(settings_flag))
            self.threadpool.start(worker)
        else:
            self.setup_build_finished(settings_flag)

    def pause_conversion(self):
        """Executes when the Pause/Resume button in the Slice Conversion group box is clicked"""

        if 'Pause' in self.pushPauseConversion.text():
            self.build['BuildInfo']['Pause'] = True
            self.pushPauseConversion.setText('Resume')
            # Save to the build.json file
            with open('build.json', 'w+') as build:
                json.dump(self.build, build, indent=4, sort_keys=True)

        elif 'Resume' in self.pushPauseConversion.text():
            self.build['BuildInfo']['Pause'] = False
            self.pushPauseConversion.setText('Pause')
            # Save to the build.json file
            with open('build.json', 'w+') as build:
                json.dump(self.build, build, indent=4, sort_keys=True)

    def setup_build_finished(self, settings_flag):
        """Executes when the slice conversion thread is finished, or the Stop button is pressed"""

        # Check for and acquire an attached camera and trigger
        # This method is here so that the image capture cannot be run unless the slice conversion has stopped
        self.acquire_ct()

        self.build['BuildInfo']['Pause'] = False
        self.build['BuildInfo']['Run'] = False

        # Save to the build.json file
        with open('build.json', 'w+') as build:
            json.dump(self.build, build, indent=4, sort_keys=True)

        self.pushPauseConversion.setEnabled(False)
        self.pushStopConversion.setEnabled(False)
        self.toolSidebar.setCurrentIndex(2)

        if not settings_flag:
            self.update_folders()
            self.update_progress(0)
            self.update_status('Build %s setup complete.' % self.build['BuildInfo']['Name'], 5000)
        else:
            self.update_status('Build %s settings changed' % self.build['BuildInfo']['Name'], 5000)

    def clear_menu(self):
        pass

    def save_build(self):
        """Saves the current build to the config.json file when File -> Save is clicked
        Executes save_as_build instead if this is the first time the build is being saved
        """

        if self.build_name:
            # Save the current build as the given filename in the given location
            with open(self.build_name, 'w+') as build:
                json.dump(self.build, build, indent=4, sort_keys=True)

            self.update_status('Build saved to %s.' % os.path.basename(self.build_name), 5000)
        else:
            self.save_as_build()

    def save_as_build(self):
        """Opens a File Dialog when File -> Save As... is clicked
        Allows the user to save the current build's config.json file to whatever location the user specifies
        """

        filename = QFileDialog.getSaveFileName(self, 'Save Build As', '%s/%s' %
                                               (self.build['BuildInfo']['Folder'], self.build['BuildInfo']['Name']),
                                               'JSON File (*.json)')[0]

        # Checking if user has chosen to save the build or clicked cancel
        if filename:
            self.build_name = filename
            self.save_build()

    def export_image(self):
        """Opens a FileDialog Window when File > Export Image... is clicked
        Allows the user to save the currently displayed image to whatever location the user specifies as a .png
        """

        # Open a folder select dialog, allowing the user to choose a location and input a name
        image_name = QFileDialog.getSaveFileName(self, 'Export Image As', '', 'Image (*.png)')[0]

        # Checking if user has chosen to save the image or clicked cancel
        if image_name:
            # Save the currently displayed image which is saved as an entry in the display dictionary
            cv2.imwrite(image_name, self.display['DisplayImage'][self.widgetDisplay.currentIndex()])

            # Open a message box with a save confirmation message
            self.export_confirmation = QMessageBox()
            self.export_confirmation.setIcon(QMessageBox.Information)
            self.export_confirmation.setText('The image has been saved to %s.' % image_name)
            self.export_confirmation.setWindowTitle('Export Image')
            self.export_confirmation.exec_()

    # MENUBAR -> VIEW

    def zoom_in(self):
        if self.actionZoomIn.isChecked():
            self.display['GraphicsNames'][self.widgetDisplay.currentIndex()].zoom_flag = True
        else:
            self.display['GraphicsNames'][self.widgetDisplay.currentIndex()].zoom_flag = False

    def zoom_in_reset(self):
        self.actionZoomIn.setChecked(False)
        self.display['GraphicsNames'][self.widgetDisplay.currentIndex()].zoom_flag = False

    def zoom_out(self):
        self.display['GraphicsNames'][self.widgetDisplay.currentIndex()].reset_image()

    def calibration_results(self):
        """Opens a Modeless Dialog Window when the Calibration Results button is clicked
        Displays the results of the camera calibration to the user"""

        # Load from the config.json file (that contains the calibration results)
        with open('config.json') as file:
            results = json.load(file)

        try:
            self.calibration_results_dialog.close()
        except:
            pass

        self.calibration_results_dialog = dialog_windows.CalibrationResults(self, results['ImageCorrection'])
        self.calibration_results_dialog.show()

    def defect_reports(self):
        """Opens a Modeless Dialog Window when the Defect Reports button is clicked
        Displays the results of the reports as processed by the Defect Detector"""

        if self.DR_dialog is None:
            self.DR_dialog = dialog_windows.DefectReports(self)
            self.DR_dialog.tab_focus.connect(self.tab_focus)
            self.DR_dialog.destroyed.connect(self.defect_reports_closed)
            self.DR_dialog.show()
        else:
            self.DR_dialog.activateWindow()

    def defect_reports_closed(self):
        self.DR_dialog = None

    def histogram_comparison(self):
        pass

    # MENUBAR -> TOOLS

    def camera_calibration(self):
        """Opens a Modeless Dialog Window when the Camera Calibration button is clicked
        Or when Tools -> Camera -> Calibration is clicked
        Allows the user to select a folder of chessboard images to calculate intrinsic values for calibration
        """

        # Check if the dialog window is already open, if not, create a new window and open it
        # Otherwise focus is given back to the open window
        # Signal listen for if the window is closed (destroyed), and sets the window to None if so
        if self.CC_dialog is None:
            self.CC_dialog = dialog_windows.CameraCalibration(self)
            self.CC_dialog.destroyed.connect(self.camera_calibration_closed)
            self.CC_dialog.show()
        else:
            self.CC_dialog.activateWindow()

    def camera_calibration_closed(self):
        """When the Dialog Window is closed, its object is set to None to allow another window to be opened"""
        self.CC_dialog = None

    def overlay_adjustment(self):
        """Opens a Modeless Dialog Window when the Overlay Adjustment button is clicked
        Or when Tools -> Overlay Adjustment is clicked
        Allows the user to adjust and transform the overlay image in a variety of ways
        """

        if self.OA_dialog is None:
            self.OA_dialog = dialog_windows.OverlayAdjustment(self)
            self.OA_dialog.update_overlay.connect(self.update_display)
            self.OA_dialog.destroyed.connect(self.overlay_adjustment_closed)

            self.OA_dialog.show()
        else:
            self.OA_dialog.activateWindow()

    def overlay_adjustment_closed(self):
        self.OA_dialog = None

    def slice_converter(self):
        """Opens a Modeless Dialog Window when the Slice Converter button is clicked
        Or when Tools -> Slice Converter is clicked
        Allows user to convert .cls or .cli files into ASCII encoded scaled contours that OpenCV can draw
        """

        if self.SC_dialog is None:
            self.SC_dialog = dialog_windows.SliceConverter(self)
            self.SC_dialog.destroyed.connect(self.slice_converter_closed)
            self.SC_dialog.show()
        else:
            self.SC_dialog.activateWindow()

    def slice_converter_closed(self):
        self.SC_dialog = None

    def image_converter(self):
        """Opens a FileDialog when the Image Converter button is clicked
        Allows the user to select an image to apply image correction on and saves the processed image in the same folder
        """

        # Get the name of the image file to be processed
        image_name = QFileDialog.getOpenFileName(self, 'Browse...', '', 'Image Files (*.png)')[0]

        # Checking if user has selected a file or clicked cancel
        if image_name:
            # Process and save the image using a thread by passing the function to a worker
            worker = qt_multithreading.Worker(self.image_converter_function, image_name)
            worker.signals.status.connect(self.update_status)
            worker.signals.progress.connect(self.update_progress)
            worker.signals.result.connect(self.image_converter_finished)
            self.threadpool.start(worker)

    @staticmethod
    def image_converter_function(image_name, status, progress):
        """Applies the distortion, perspective, crop and CLAHE processes to the received image
        Also subsequently saves the image after every process"""

        image = cv2.imread('%s' % image_name)
        image_name = os.path.splitext(image_name)[0]

        # Apply the image processing techniques in order, subsequently saving the image and incrementing progress
        progress.emit(0)
        status.emit('Undistorting image...')
        image = image_processing.ImageTransform().distortion_fix(image)
        cv2.imwrite('%s_D.png' % image_name, image)
        progress.emit(25)
        status.emit('Fixing perspective warp...')
        image = image_processing.ImageTransform().perspective_fix(image)
        cv2.imwrite('%s_DP.png' % image_name, image)
        progress.emit(50)
        status.emit('Cropping image to size...')
        image = image_processing.ImageTransform().crop(image)
        cv2.imwrite('%s_DPC.png' % image_name, image)
        progress.emit(75)
        status.emit('Applying CLAHE equalization...')
        image = image_processing.ImageTransform().clahe(image)
        cv2.imwrite('%s_DPCE.png' % image_name, image)
        progress.emit(100)
        status.emit('Image successfully processed and saved to same folder as input image.')

        return os.path.dirname(image_name).replace('/', '\\')

    @staticmethod
    def image_converter_finished(image_folder):
        """Open the folder containing the processed images for the user to view after conversion is finished"""
        subprocess.Popen('explorer %s' % image_folder)

    # MENUBAR -> TOOLS -> DEFECT PROCESSOR

    def process_current(self):
        """Runs the currently displayed image through the DefectDetector and saves it to the appropriate folder
        This is done by saving pertinent information such as the image file names, layer and phase
        To the config.json file, which is then loaded by the Detector"""

        self.all_flag = False
        self.tab_index = self.widgetDisplay.currentIndex()
        self.toggle_processing_buttons(3)
        self.process_settings(self.sliderDisplay.value())

    def process_all(self):
        """Runs all the available images in the currently opened tab through the DefectDetector
        The button also functions as a Process Stop button which halts the processing process"""

        if 'Process All' in self.pushProcessAll.text():
            self.defect_counter = 0
            self.all_flag = True
            self.tab_index = self.widgetDisplay.currentIndex()
            self.pushProcessAll.setStyleSheet('QPushButton {color: #ff0000;}')
            self.pushProcessAll.setText('Process Stop')
            self.actionProcessAll.setText('Process Stop')

            # Remove the already processed defect images from the image list
            self.layer_numbers = sorted(list(set(self.display['LayerNumbers'][self.tab_index]) -
                                      set(self.display['LayerNumbers'][self.tab_index + 4])))
            self.process_settings(self.layer_numbers[self.defect_counter])

        elif 'Process Stop' in self.pushProcessAll.text():
            # On the next process loop, setting this to False will send the process to the finished method
            self.all_flag = False
            self.pushProcessAll.setStyleSheet('')
            self.pushProcessAll.setText('Process All')
            self.actionProcessAll.setText('Process All')
            self.toggle_processing_buttons(3)

    def process_selected(self):
        """Runs the user selected image through the DefectDetector and saves it to the same folder as the input image
        Both the coat and scan defect processes are executed on the image and saved as separate images"""
        pass

    def process_settings(self, layer):
        """Saves the settings to be used to process an image for defects to the build.json file
        This method exists as the only difference between the two options is the layer number"""

        self.processing_flag = True

        # Load from the build.json file
        with open('build.json') as build:
            self.build = json.load(build)

        # Grab some pertinent information (for clearer code purposes)
        phase = self.display['FolderNames'][self.tab_index][:-1]

        self.build['DefectDetector']['Image'] = self.display['ImageList'][self.tab_index][layer - 1]
        self.build['DefectDetector']['Contours'] = self.display['ImageList'][2][layer - 1]
        self.build['DefectDetector']['Layer'] = layer
        self.build['DefectDetector']['Phase'] = phase

        # Set the previous image to be compared against the current image if it is not the first layer
        if layer > 1:
            self.build['DefectDetector']['ImagePrevious'] = self.display['ImageList'][self.tab_index][layer - 2]
        else:
            self.build['DefectDetector']['ImagePrevious'] = ''

        # Save to the build.json file
        with open('build.json', 'w+') as build:
            json.dump(self.build, build, indent=4, sort_keys=True)

        # Vary the status message to display depending on which button was pressed
        if self.all_flag:
            self.toggle_processing_buttons(4)
            self.defect_counter += 1
            self.update_status('Running %s layer %s through the Defect Detector...' % (phase, str(layer).zfill(4)))
        else:
            self.update_status('Running displayed %s image through the Defect Detector...' % phase)

        self.process_run()

    def process_run(self):
        """Setup and execute the worker using the QThreadPool"""
        worker = qt_multithreading.Worker(image_processing.DefectDetector().run_detector)
        worker.signals.status.connect(self.update_status)
        worker.signals.progress.connect(self.update_progress)
        worker.signals.finished.connect(self.process_finished)
        self.threadpool.start(worker)

    def process_finished(self):
        """Decides whether the Defect Processor needs to be run again for consecutive images
        Otherwise the window is set to its processing finished state"""

        self.processing_flag = False
        self.update_folders()

        if self.all_flag and not self.defect_counter == len(self.layer_numbers):
            self.process_settings(self.layer_numbers[self.defect_counter])
        else:
            self.all_flag = False
            self.pushProcessAll.setStyleSheet('')
            self.pushProcessAll.setText('Process All')
            self.actionProcessAll.setText('Process All')
            self.update_status('Defect Detection finished successfully.', 10000)

    def send_notification(self, layer, phase):
        """Sends an email notification if a detected defect goes above the set threshold values
        Only works if a current build is in running and if the appropriate checkboxes were checked"""

        if self.build['Notifications']['Major']:
            worker = qt_multithreading.Worker(extra_functions.Notifications.major_defect_message)

    def toggle_processing_buttons(self, state):
        """Enables or disables the following buttons/actions in one fell swoop depending on the received state"""

        # State 1 is when the current image CANNOT be processed
        if state == 1:
            self.pushProcessCurrent.setEnabled(False)
            self.actionProcessCurrent.setEnabled(False)
            self.pushProcessAll.setEnabled(False)
            self.actionProcessAll.setEnabled(False)
            self.pushProcessSelected.setEnabled(True)
            self.actionProcessSelected.setEnabled(True)
        # State 2 is when the current image CAN be processed
        elif state == 2:
            self.pushProcessCurrent.setEnabled(True)
            self.actionProcessCurrent.setEnabled(True)
            self.pushProcessAll.setEnabled(True)
            self.actionProcessAll.setEnabled(True)
            self.pushProcessSelected.setEnabled(True)
            self.actionProcessSelected.setEnabled(True)
        # State 3 is when a Process Current or Process Selected process is running
        elif state == 3:
            self.pushProcessCurrent.setEnabled(False)
            self.actionProcessCurrent.setEnabled(False)
            self.pushProcessAll.setEnabled(False)
            self.actionProcessAll.setEnabled(False)
            self.pushProcessSelected.setEnabled(False)
            self.actionProcessSelected.setEnabled(False)
        # State 4 is when a Process All is running
        elif state == 4:
            self.pushProcessCurrent.setEnabled(False)
            self.actionProcessCurrent.setEnabled(False)
            self.pushProcessAll.setEnabled(True)
            self.actionProcessAll.setEnabled(True)
            self.pushProcessSelected.setEnabled(False)
            self.actionProcessSelected.setEnabled(False)
        # State 5 is when the current image CANNOT be processed but the tab still has other images that CAN
        elif state == 5:
            self.pushProcessCurrent.setEnabled(False)
            self.actionProcessCurrent.setEnabled(False)
            self.pushProcessAll.setEnabled(True)
            self.actionProcessAll.setEnabled(True)
            self.pushProcessSelected.setEnabled(True)
            self.actionProcessSelected.setEnabled(True)

    # MENUBAR -> SETTINGS

    def camera_settings(self):
        """Opens a Modeless Dialog Window when Tools -> Camera -> Settings is clicked
        Allows the user to change camera settings which will be sent to the camera before images are taken
        """

        if self.CS_dialog is None:
            self.CS_dialog = dialog_windows.CameraSettings(self)
            self.CS_dialog.destroyed.connect(self.camera_settings_closed)
            self.CS_dialog.show()
        else:
            self.CS_dialog.activateWindow()

    def camera_settings_closed(self):
        self.CS_dialog = None

    def build_settings(self):
        """Opens a Modal Window when Settings -> Build Settings is clicked
        Allows the user to change the current build's settings
        """

        BS_dialog = dialog_windows.NewBuild(self, open_flag=True, settings_flag=True)

        if BS_dialog.exec_():
            self.setup_build(True)

    def advanced_mode(self):
        """Allows the user to toggle between basic mode or advanced mode which in essence enables or disables buttons
        These buttons have to do with features or functions which could negatively impact the program if mishandled
        """

        # Grab the bool value of the Advanced Mode 'checkbox' (for clearer code purposes)
        flag = self.actionAdvancedMode.isChecked()

        self.actionCameraCalibration.setEnabled(flag)
        self.pushCameraCalibration.setEnabled(flag)
        self.actionSliceConverter.setEnabled(flag)
        self.pushSliceConverter.setEnabled(flag)
        self.pushOverlayAdjustment.setEnabled(flag)
        self.actionOverlayAdjustment.setEnabled(flag)

        if self.actionAdvancedMode.isChecked():
            self.pushOverlayAdjustment.setEnabled(self.checkOverlay.isChecked())
            self.actionOverlayAdjustment.setEnabled(self.checkOverlay.isChecked())

        self.update_display(self.widgetDisplay.currentIndex())

        # Only disable the following button if it is enabled in the first place
        if self.pushCapture.isEnabled():
            self.pushCapture.setEnabled(False)

    # MENUBAR -> HELP

    def view_help(self):
        pass

    def view_about(self):
        pass

    # LAYER SELECTION

    def set_layer(self):
        """Changes the displayed slider's value which in turn executes the slider_change method"""
        self.sliderDisplay.setValue(self.spinLayer.value())

    # IMAGE CAPTURE

    def acquire_ct(self):
        """Executes after setting up a new or loading a build, or when the Acquire Camera / Trigger button is clicked
        Checks for a valid attached camera and trigger and enables/disables the Run button accordingly"""

        self.update_status_ct(['Acquiring...', 'Acquiring...'])

        # Checks for a valid attached camera and trigger using the threadpool by passing the function to a worker
        worker = qt_multithreading.Worker(self.acquire_ct_function)
        worker.signals.result.connect(self.update_ct)
        self.threadpool.start(worker)

    @staticmethod
    def acquire_ct_function():
        """Function that will be passed to the QThreadPool to be executed"""
        camera = image_capture.ImageCapture().acquire_camera()
        trigger = image_capture.ImageCapture().acquire_trigger()

        # Functions can only return one object, so the two results are combined into a list and returned
        return [camera, trigger]

    def capture_single(self):
        """Executes when the Capture Single Image button is clicked
        Captures and saves a single image by using a worker thread to perform the capture function"""
        self.pushCapture.setEnabled(False)

        # Takes a single image using a thread by passing the function to the worker
        worker = qt_multithreading.Worker(image_capture.ImageCapture().acquire_image_single)
        worker.signals.status.connect(self.update_status_ct)
        worker.signals.name.connect(self.fix_image)
        worker.signals.finished.connect(self.capture_single_finished)
        self.threadpool.start(worker)

    def capture_single_finished(self):
        self.pushCapture.setEnabled(True)

    def run_build(self):
        """Executes when the Run button is clicked
        Polls the trigger device for a trigger, subsequently capturing and saving an image if triggered
        """

        # Enable / disable certain UI elements to prevent concurrent processes
        self.update_status('Running build.')
        self.pushRun.setEnabled(False)
        self.pushPauseResume.setEnabled(True)
        self.pushStop.setEnabled(True)
        self.pushAcquireCT.setEnabled(False)
        self.pushCapture.setEnabled(False)
        self.checkResume.setEnabled(False)
        if self.actionAdvancedMode.isChecked():
            self.pushFauxTrigger.setEnabled(True)

        # Check if the Resume From checkbox is checked and if so, set the current layer to the entered number
        # 0.5 is subtracted as it is assumed that the first image captured will be the previous layer's scan
        if self.checkResume.isChecked():
            self.spinStartingLayer.setEnabled(False)
            self.build['ImageCapture']['Layer'] = self.spinStartingLayer.value() - 0.5
            self.build['ImageCapture']['Phase'] = 1

            # Save to the build.json file
            with open('build.json', 'w+') as build:
                json.dump(self.build, build, indent=4, sort_keys=True)

        # Open the COM port associated with the attached trigger device
        self.serial_trigger = serial.Serial(self.trigger_port, 9600, timeout=1)

        # Reset the elapsed time and idle time counters and initialize the display time to 0
        self.stopwatch_elapsed = 0
        self.stopwatch_idle = 0
        self.update_time()

        # Create a QTimer that will increment the two running timers
        self.timer_stopwatch = QTimer()

        # Connect the timeout of the QTimer to the corresponding function
        self.timer_stopwatch.timeout.connect(self.update_time)

        # Start the QTimer which will timeout and execute the above connected slot method every given milliseconds
        self.timer_stopwatch.start(1000)

        self.capture_run('')

    def capture_run(self, result):
        """Because reading from the serial trigger takes a little bit of time, it temporarily freezes the main UI
        As such, the serial read is turned into a QRunnable function that is passed to a worker using the QThreadPool
        The current method works as a sort of recursive loop, where the result of the trigger poll is checked
        If a trigger is detected, the corresponding image capture function is executed as a worker to the QThreadPool
        Otherwise, another trigger polling worker is started and the loop keeps repeating
        The loop is broken if the Pause button is pressed or the build is stopped outright
        """

        # Check if the build is still 'running'
        if 'PAUSE' in self.pushPauseResume.text() and self.pushPauseResume.isEnabled():
            if 'TRIG' in result:
                self.pushPauseResume.setEnabled(False)
                self.pushStop.setEnabled(False)
                self.pushFauxTrigger.setEnabled(False)
                worker = qt_multithreading.Worker(image_capture.ImageCapture().acquire_image_run)
                worker.signals.status.connect(self.update_status_ct)
                worker.signals.name.connect(self.fix_image)
                worker.signals.finished.connect(self.capture_run_finished)
                self.threadpool.start(worker)
            else:
                self.update_status_ct(['Waiting...', 'Waiting...'])
                worker = qt_multithreading.Worker(self.poll_trigger)
                worker.signals.result.connect(self.capture_run)
                self.threadpool.start(worker)

    def poll_trigger(self):
        """Function that will be passed to the QThreadPool to be executed"""

        return str(self.serial_trigger.readline())

    def capture_run_finished(self):
        """Reset the time idle counter and restart the trigger polling after resetting the serial input"""
        self.serial_trigger.reset_input_buffer()
        self.stopwatch_idle = 0
        self.pushPauseResume.setEnabled(True)
        self.pushStop.setEnabled(True)
        # Enables the Faux Trigger button if advanced mode is on
        if self.actionAdvancedMode.isChecked():
            self.pushFauxTrigger.setEnabled(True)
        self.capture_run('')

    def pause_build(self):
        """Executes when the Pause/Resume button is clicked"""

        # Pause function, stop the timer and the trigger polling loop
        if 'PAUSE' in self.pushPauseResume.text():
            self.pushPauseResume.setStyleSheet('QPushButton {color: #00aa00;}')
            self.pushPauseResume.setText('RESUME')
            self.timer_stopwatch.stop()
            self.update_status('Current build paused.')
            self.update_status_ct(['Paused', 'Paused'])
            self.pushFauxTrigger.setEnabled(False)

        # Resume function, start the timer and restart the trigger polling loop
        elif 'RESUME' in self.pushPauseResume.text():
            self.pushPauseResume.setStyleSheet('QPushButton {color: #ffaa00;}')
            self.pushPauseResume.setText('PAUSE')
            self.timer_stopwatch.start(1000)
            self.capture_run_finished()
            self.update_status('Current build resumed.')
            if self.actionAdvancedMode.isChecked():
                self.pushFauxTrigger.setEnabled(True)

    def stop_build(self):
        """Executes when the Stop button is clicked"""

        # Enable / disable certain UI elements
        # Disabling the Pause button stops the trigger polling loop
        self.update_status('Build stopped.', 10000)
        self.update_status_ct(['Found', self.trigger_port])
        self.pushRun.setEnabled(True)
        self.pushPauseResume.setEnabled(False)
        self.pushStop.setEnabled(False)
        self.pushAcquireCT.setEnabled(True)
        self.checkResume.setEnabled(True)
        self.pushFauxTrigger.setEnabled(False)
        if self.actionAdvancedMode.isChecked():
            self.pushCapture.setEnabled(True)

        # Reset the Pause/Resume button back to its default state (including the text colour)
        self.pushPauseResume.setText('PAUSE')
        self.pushPauseResume.setStyleSheet('')

        # Stop the stopwatch timer and close the serial port
        self.timer_stopwatch.stop()
        self.serial_trigger.close()

    def reset_idle(self):
        """Resets the stopwatch idle counter whenever an image has been captured"""
        self.stopwatch_idle = 0

    # IMAGE PROCESSING

    def fix_image(self, image_name):
        """Use the received image name to load the image in order to fix it, then process it"""

        self.image_name = image_name

        self.update_status('Applying image fixes...')
        worker = qt_multithreading.Worker(self.fix_image_function, image_name)
        worker.signals.finished.connect(self.fix_image_finished)
        self.threadpool.start(worker)

    @staticmethod
    def fix_image_function(image_name):
        """Function that will be passed to the QThreadPool to be executed"""

        # Load the image into memory
        image = cv2.imread(image_name)

        # Apply
        image = image_processing.ImageTransform().distortion_fix(image)
        image = image_processing.ImageTransform().perspective_fix(image)
        image = image_processing.ImageTransform().crop(image)

        # Modify the name of
        if 'coat' in image_name:
            image_name = image_name.replace('coatR', 'coatP').replace('raw', 'processed')
        elif 'scan' in image_name:
            image_name = image_name.replace('scanR', 'scanP').replace('raw', 'processed')
        elif 'single' in image_name:
            image_name = image_name.replace('singleR', 'singleP').replace('raw', 'processed')

        # Save the image using a modified image name
        cv2.imwrite(image_name, image)

    def fix_image_finished(self):

        self.update_status('Image fix successfully applied. Currently detecting defects...')

        # Update the image dictionaries and most importantly, the image ranges
        self.update_folders()

        # Acquire the layer and phase (tab index) from the image name
        layer = int(os.path.splitext(os.path.basename(self.image_name))[0][-4:])
        if 'coat' in self.image_name:
            index = 0
        elif 'scan' in self.image_name:
            index = 1
        else:
            index = 3

        # Set the tab to focus on the current layer and
        self.tab_focus(index, layer)

        # Process the image for defects, the image being the one the above method set focus to
        self.process_current()

    # DISPLAY

    def start_display(self):
        """Displays the image based on the corresponding slider's value on the corresponding tab label
        Allows the user to scroll through the images and jump to specific ones
        The trigger event for changing things is a change in slider value
        Note: The order of the images will be the order that the images are in the folder itself
        The images will need to have proper numbering to ensure that the layer numbers are accurate
        """

        # Update the list of images for all four image folders
        self.update_folders()

        # Set the display flag to true to allow tab changes to update images
        self.display_flag = True

        # Enable certain UI elements such as the slider and the layer box
        self.actionUpdateFolders.setEnabled(True)
        self.spinLayer.setEnabled(True)
        self.toolSidebar.setCurrentIndex(2)

        # Update the maximum ranges of various UI elements
        self.update_ranges(self.widgetDisplay.currentIndex())

        # Initialize the current Image Viewer
        self.update_display(self.widgetDisplay.currentIndex())

    def update_display(self, index):
        """Updates the MainWindow widgetDisplay to show an image on the currently displayed tab as per toggles
        Also responsible for enabling or disabling UI elements if there is or isn't an image to be displayed"""

        # Grab the current tab index (for clearer code purposes)
        if type(index) != int:
            index = self.widgetDisplay.currentIndex()

        # Grab the names of certain elements (for clearer code purposes)
        label = self.display['LabelNames'][index]
        graphics = self.display['GraphicsNames'][index]
        stack = self.display['StackNames'][index]
        image_list = self.display['ImageList'][index]

        value = self.sliderDisplay.value()
        layer = str(value).zfill(4)

        # Assume disabled Processing buttons as default
        if not self.processing_flag:
            self.toggle_processing_buttons(1)

        # Check if the image folder has an actual image to display
        if list(filter(bool, image_list)):
            # Change the stacked widget to the one with the image viewer
            stack.setCurrentIndex(1)

            # Enable all the display related UI elements
            self.groupDisplayOptions.setEnabled(True)
            self.toggle_display_buttons(True)

            # Check if the Defect Analysis radio button is checked and load the related defect image if so
            if self.radioDefects.isChecked():
                if os.path.isfile(self.display['ImageList'][index + 4][value - 1]):
                    image = cv2.imread(self.display['ImageList'][index + 4][value - 1])
                else:
                    label.setText('%s Layer %s Defect Image not in folder.' %
                                  (self.display['FolderNames'][index][:-1], layer))
                    stack.setCurrentIndex(0)

                    self.toggle_display_buttons(False, True)
                    # Exit out of the entire method as there isn't an image to display
                    return

            # Otherwise load the layer image based on the current slider value
            else:
                # Check if the image exists (in case it gets deleted between folder checks)
                if os.path.isfile(image_list[value - 1]):
                    # Load the layer image into memory
                    image = cv2.imread(image_list[value - 1])

                    # Enable the Defect Processor toolbar and actions
                    if not self.processing_flag and index != 2:
                        self.toggle_processing_buttons(2)
                else:
                    # Set the stack to the information label and display the missing layer information
                    label.setText('%s Layer %s Image not in folder.' % (self.display['FolderNames'][index][:-1], layer))
                    stack.setCurrentIndex(0)

                    # Enable the seek buttons if the current layer's image isn't found
                    self.toggle_display_buttons(False, True)

                    # Enable the Defect Processor toolbar and actions
                    if not self.processing_flag and index != 2:
                        self.toggle_processing_buttons(5)
                    return

            if self.checkOverlay.isChecked():
                # Load the overlay image into memory
                overlay = cv2.imread(self.display['ImageList'][2][value - 1])

                # Resize the overlay image if the resolution doesn't match the displayed image
                if overlay.shape[:2] != image.shape[:2]:
                    overlay = cv2.resize(overlay, image.shape[:2][::-1], interpolation=cv2.INTER_CUBIC)

                # Apply the stored transformation values to the overlay image
                overlay = image_processing.ImageTransform().apply_transformation(overlay, True)

                # self.update_status('Translation X - 0 Y - 0 | Rotation - 0.00 | Stretch X - 0 Y - 0', 10000)
                # Display a status message with the current transformation of the overlay image
                # self.update_status('Translation X - %d Y - %d | Rotation - %.2f | Stretch X - %d Y - %d' %
                #                    (self.transform[1], -self.transform[0], -1 * self.transform[2],
                #                     self.transform[4], self.transform[5]), 10000)

                # Apply the overlay on top of the image
                image = cv2.add(image, overlay)

            # Overlays the part names if the Toggle Part Names checkbox is checked
            if self.checkPartNames.isChecked():
                # Load the part names image into memory
                image_names = cv2.imread('%s/part_names.png' % self.build['ImageCapture']['Folder'])

                # Resize the overlay image if the resolution doesn't match the displayed image
                if image_names.shape[:2] != image.shape[:2]:
                    image_names = cv2.resize(image_names, image.shape[:2][::-1], interpolation=cv2.INTER_CUBIC)

                image = cv2.add(image, image_names)

            # Applies CLAHE to the display image if the Equalization checkbox is checked
            if self.checkCLAHE.isChecked():
                image = image_processing.ImageTransform.clahe(image)

            # Convert from OpenCV's BGR format to RGB so that colours are displayed correctly
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Display the image on the current GraphicsView
            graphics.set_image(image)

            # Save the current (modified) image so that it can be exported if need be
            self.display['DisplayImage'][index] = image

            # Disable the seek buttons if there is an image being displayed
            self.toggle_display_buttons(True, True)

            # Disable the Toggle Overlay checkbox if the corresponding overlay image isn't found
            # This is at the end as toggle_display_buttons also affects the aforementioned checkbox
            if os.path.isfile(self.display['ImageList'][2][value - 1]) and not index == 2:
                self.checkOverlay.setEnabled(True)
            else:
                self.checkOverlay.setEnabled(False)
                self.checkOverlay.setChecked(False)

            # Similar to above, disable the Toggle Part Names checkbox if the part names image isn't found
            if os.path.isfile('%s/part_names.png' % self.build['ImageCapture']['Folder']):
                self.checkPartNames.setEnabled(True)
            else:
                self.checkPartNames.setEnabled(False)
                self.checkPartNames.setChecked(False)
        else:
            # If the entire folder is empty, change the stacked widget to the one with the information label
            label.setText('%s folder empty. Nothing to display.' % self.display['FolderNames'][index][:-1])
            stack.setCurrentIndex(0)

            # Disable all the display related UI elements
            self.groupDisplayOptions.setEnabled(False)
            self.toggle_display_buttons(False)

    def toggle_display_buttons(self, flag, seek_flag=False):
        """Enables or disables the following buttons/actions in one fell swoop"""

        self.checkCLAHE.setEnabled(flag)
        self.checkPartNames.setEnabled(flag)
        self.checkOverlay.setEnabled(flag)
        self.actionZoomIn.setEnabled(flag)
        self.actionZoomOut.setEnabled(flag)
        self.actionExportImage.setEnabled(flag)
        self.actionZoomIn.setChecked(False)

        if self.widgetDisplay.currentIndex() == 3:
            self.pushDisplayUpSeek.setEnabled(False)
            self.pushDisplayDownSeek.setEnabled(False)

        if flag:
            if self.widgetDisplay.currentIndex() == 2:
                self.checkOverlay.setEnabled(False)
                self.checkOverlay.setChecked(False)
                self.radioDefects.setEnabled(False)
            else:
                self.checkOverlay.setEnabled(True)
                self.radioDefects.setEnabled(True)

        # Seek flag refers to the button setup when a layer image isn't found (rather than there being no images)
        if seek_flag:
            self.pushDisplayUpSeek.setEnabled(not flag)
            self.pushDisplayDownSeek.setEnabled(not flag)
        else:
            self.frameSlider.setEnabled(flag)
            self.pushGo.setEnabled(flag)

    def toggle_overlay(self):
        """Overlay process is done in the update_display method
        This method is mostly to show the appropriate status message"""

        if self.checkOverlay.isChecked():
            # Display the message for 5 seconds
            self.update_status('Displaying part contours.', 3000)
        else:
            self.update_status('Hiding part contours.', 3000)

        if self.actionAdvancedMode.isChecked():
            self.pushOverlayAdjustment.setEnabled(self.checkOverlay.isChecked())
            self.actionOverlayAdjustment.setEnabled(self.checkOverlay.isChecked())

        self.update_display(self.widgetDisplay.currentIndex())

    def toggle_part_names(self):
        """Shows or hides the part names on the image (so long as the part name image exists)"""

        if self.checkPartNames.isChecked():
            self.update_status('Displaying part names.', 3000)
        else:
            self.update_status('Hiding part names.', 3000)

        self.update_display(self.widgetDisplay.currentIndex())

    def update_overlay(self, transform):
        """Executes the adjustment of the overlay"""
        pass

    def context_menu_display(self, position):
        """Opens a context menu at the right-clicked position of any of the display labels
        This method also handles the Open Image functions
        """

        # Create a QMenu with the respective actions as an instance variable so other methods can modify it
        self.menu_display = QMenu()
        action_show_image = self.menu_display.addAction('Show Image in Explorer')
        action_open_image = self.menu_display.addAction('Open Image in Image Viewer')
        self.menu_display.addSeparator()
        action_export = self.menu_display.addAction('Export Image...')

        # Open the context menu at the received position
        action = self.menu_display.exec_(self.graphicsCE.mapToGlobal(position))

        # Check which action has been clicked and execute the respective methods
        if action:
            # Grab the name of the image using the slider value (subtract 1 due to code starting from 0)
            # Also check if the displayed image is the Defect Analysis one, then a different list will need to be used
            if self.radioDefects.isChecked():
                step = 4
            else:
                step = 0
            name = self.display['ImageList'][self.widgetDisplay.currentIndex() + step][self.sliderDisplay.value() - 1]

            if action == action_show_image:
                # Need to turn the forward slashes into backslash due to windows explorer only working with backslashes
                subprocess.Popen(r"""explorer /select, %s""" % name.replace('/', '\\'))
            elif action == action_open_image:
                os.startfile(name)
            elif action == action_export:
                self.export_image()

    # MISCELLANEOUS UI ELEMENT FUNCTIONALITY

    def tab_change(self, index):
        """Executes when the focused tab on widgetDisplay changes to enable/disable buttons and change layer values"""

        # Stop the change in slider value from changing the picture as well, causing conflicting images
        self.sliderDisplay.blockSignals(True)

        if self.display_flag:
            # Set the layer spinbox's range depending on the currently displayed tab
            self.update_ranges(index)

            # Set the slider's value to the saved layer value of the current tab
            self.sliderDisplay.setValue(self.display['CurrentLayer'][index])

            # Set the current layer number depending on the currently displayed tab
            self.labelLayerNumber.setText('%s / %s' % (str(self.display['CurrentLayer'][index]).zfill(4),
                                                       str(self.display['MaxLayers']).zfill(4)))

            # Set the radio button to Original as contours have no defect images and disable the Defect Processor
            if index == 2:
                self.radioOriginal.setChecked(True)

            # Update the image on the graphics display with the new image (in case image has been deleted)
            self.update_display(index)

            # Zoom out and reset the image
            self.display['GraphicsNames'][index].reset_image()

        self.sliderDisplay.blockSignals(False)

    def tab_focus(self, index, value, defect_flag=False):
        """Changes the tab focus to the received index's tab and sets the slider value to the received value
        Used for when an image has been captured and focus is to be given to the new image
        Also can be used for when an image has just finished processing for defects
        """

        # Double check if the received value is within the layer's range in the first place
        if value > self.display['MaxLayers']:
            self.update_status('Layer %s outside of the available layer range.' % str(value).zfill(4), 3000)
        else:
            # Set the display image to be the defect analyzed image
            if defect_flag:
                self.radioDefects.setChecked(True)

            self.widgetDisplay.setCurrentIndex(index)
            self.sliderDisplay.setValue(value)

    def slider_change(self, value):
        """Executes when the value of the scrollbar changes to then update the tooltip with the new value
        Also updates the relevant layer numbers of specific UI elements and other internal functions
        """

        # Updates the label number and slider tooltip with the currently displayed tab's slider's value
        self.labelLayerNumber.setText('%s / %s' % (str(value).zfill(4), str(self.display['MaxLayers']).zfill(4)))
        self.sliderDisplay.setToolTip(str(value))

        # Save the current slider value to the current tab's layer dictionary key for tab changes
        self.display['CurrentLayer'][self.widgetDisplay.currentIndex()] = value
        self.display['GraphicsNames'][self.widgetDisplay.currentIndex()].reset_image()

        # Update the image on the graphics display with the new image
        self.update_display(self.widgetDisplay.currentIndex())

    def slider_up(self):
        """Increments the slider by 1"""
        self.sliderDisplay.setValue(self.sliderDisplay.value() + 1)

    def slider_up_seek(self):
        """Jumps the slider to the first available image in the positive direction"""

        # If the Defect Analysis radio button is checked, use the defect image list instead
        if self.radioOriginal.isChecked():
            number_list = self.display['LayerNumbers'][self.widgetDisplay.currentIndex()]
        else:
            number_list = self.display['LayerNumbers'][self.widgetDisplay.currentIndex() + 4]

        # If the number list is empty (when Defect Analysis is checked but no images have been processed)
        # Make a list consisting of the first and the last layer
        if not number_list:
            number_list = [1, self.display['MaxLayers']]

        # Find the index of the value closest to the current layer value in the layer number list
        position = bisect.bisect_left(number_list, self.sliderDisplay.value())

        if position == 0:
            self.sliderDisplay.setValue(number_list[0])
        elif position == len(number_list):
            self.sliderDisplay.setValue(self.sliderDisplay.maximum())
        else:
            self.sliderDisplay.setValue(number_list[position])

    def slider_down(self):
        """Decrements the slider by 1"""
        self.sliderDisplay.setValue(self.sliderDisplay.value() - 1)

    def slider_down_seek(self):
        """Jumps the slider to the first available image in the negative direction"""

        if self.radioOriginal.isChecked():
            number_list = self.display['LayerNumbers'][self.widgetDisplay.currentIndex()]
        else:
            number_list = self.display['LayerNumbers'][self.widgetDisplay.currentIndex() + 4]

        if not number_list:
            number_list = [1, self.display['MaxLayers']]

        position = bisect.bisect_left(number_list, self.sliderDisplay.value())

        if position == 0:
            self.sliderDisplay.setValue(1)
        elif position == len(number_list):
            self.sliderDisplay.setValue(number_list[-1])
        else:
            self.sliderDisplay.setValue(number_list[position - 1])

    def update_folders(self):
        """Updates the display dictionary with the updated list of images in all four image folders"""

        for index in range(8):
            # Get a list of numbers of the supposed layer images in the folder (except the single folders)
            if not index == 3 or not index == 6:
                # Reset the layer numbers in the display dictionary
                self.display['LayerNumbers'][index][:] = list()

                for filename in os.listdir(self.display['ImageFolder'][index]):
                    # Skips the first scan picture, which should be 'Layer 0', the picture before the first coat
                    if '0000' in filename:
                        continue

                    # Only grab the images and ignore any other files in the folders
                    if '.png' in filename or '.jpg' in filename or '.jpeg' in filename:
                        try:
                            # Check if the last four characters of the file name are numbers, otherwise file is ignored
                            number = int(os.path.splitext(filename)[0][-4:])
                        except ValueError:
                            pass
                        else:
                            # Save the new number as the new max layer if it is higher than the previous saved number
                            self.display['LayerNumbers'][index].append(number)
                            if number > self.display['MaxLayers']:
                                self.display['MaxLayers'] = number

        for index in range(8):
            self.update_image_list(index)

        # Update the ranges as well
        self.update_ranges(self.widgetDisplay.currentIndex())

        if self.display_flag:
            # Reload any images in the current tab
            self.update_display(self.widgetDisplay.currentIndex())

    def update_image_list(self, index):
        """Updates the ImageList dictionary with a new list of images"""

        if index == 3 or index > 6:
            # Empty the Single folder list and fill it with the file names in the folder
            self.display['ImageList'][index][:] = list()
            for filename in os.listdir(self.display['ImageFolder'][index]):
                if '.png' in filename or '.jpg' in filename or '.jpeg' in filename:
                    self.display['ImageList'][index].append('%s/%s' % (self.display['ImageFolder'][index], filename))
        else:
            # Replace the list with a list of empty strings
            self.display['ImageList'][index] = ['' for _ in range(self.display['MaxLayers'])]

            for filename in os.listdir(self.display['ImageFolder'][index]):
                if '.png' in filename or '.jpg' in filename or '.jpeg' in filename:
                    try:
                        # Check if the last four characters of the file name are numbers, otherwise file is ignored
                        number = int(os.path.splitext(filename)[0][-4:])
                    except ValueError:
                        pass
                    else:
                        # Save the current file name at the index as defined in the file's own name
                        self.display['ImageList'][index][number - 1] = '%s/%s' % (
                            self.display['ImageFolder'][index], filename)

    def update_ranges(self, index):
        """Updates the layer spinbox's maximum acceptable range, tooltip, and the slider's maximum range"""

        self.spinLayer.setMaximum(self.display['MaxLayers'])
        self.spinLayer.setToolTip('1 - %s' % self.display['MaxLayers'])
        self.sliderDisplay.setMaximum(self.display['MaxLayers'])

        # Also updates the slider's pageStep and tickInterval depending on the max number of layers
        self.sliderDisplay.setPageStep(math.ceil(self.display['MaxLayers'] // 50))
        self.sliderDisplay.setTickInterval(math.ceil(self.display['MaxLayers'] // 50))

        self.labelLayerNumber.setText('%s / %s' % (str(self.sliderDisplay.value()).zfill(4),
                                                   str(self.display['MaxLayers']).zfill(4)))

    def update_ct(self, status):
        """Updates the status boxes for the acquisition of the camera and trigger with the received status details
        Also enables or disables the Run and Capture Single Image buttons depending on the result"""

        # Camera status
        if bool(status[0]):
            self.update_status_ct(['Found', ''])
            if self.actionAdvancedMode.isChecked():
                self.pushCapture.setEnabled(True)
            if bool(status[1]):
                self.pushRun.setEnabled(True)
        else:
            self.update_status_ct(['Not Found', ''])
            self.pushRun.setEnabled(False)
            self.pushCapture.setEnabled(False)

        # Trigger status
        if bool(status[1]):
            self.trigger_port = status[1]
            self.update_status_ct(['', self.trigger_port])
        else:
            self.update_status_ct(['', 'Not Found'])
            self.pushRun.setEnabled(False)

    def update_time(self):
        """Updates the timers at the bottom right of the Main Window with an incremented formatted timestamp"""

        self.stopwatch_elapsed += 1
        self.stopwatch_idle += 1

        self.labelElapsedTime.setText(self.format_time(self.stopwatch_elapsed))
        self.labelIdleTime.setText(self.format_time(self.stopwatch_idle))

    @staticmethod
    def format_time(stopwatch):
        """Format the individual seconds, minutes and hours into proper string time format"""

        seconds = str(stopwatch % 60).zfill(2)
        minutes = str(stopwatch % 3600 // 60).zfill(2)
        hours = str(stopwatch // 3600).zfill(2)

        return '%s:%s:%s' % (hours, minutes, seconds)

    def update_status_ct(self, status):
        """Updates both the camera and trigger status bars with the received string arguments (if they exist)"""

        if status[0]:
            self.labelCameraStatus.setText(status[0])
        if status[1]:
            self.labelTriggerStatus.setText(status[1])

    def update_status(self, string, duration=0):
        """Updates the default status bar at the bottom of the Main Window with the received string argument"""
        self.statusBar.showMessage(string, duration)

    def update_progress(self, percentage):
        """Updates the progress bar at the bottom of the Main Window with the received percentage argument"""
        self.progressBar.setValue(int(percentage))

    # CLEANUP

    def closeEvent(self, event):
        """Executes when Menu -> Exit is clicked or the top-right X is clicked"""


if __name__ == '__main__':
    application = QApplication(sys.argv)
    interface = MainWindow()
    interface.show()
    sys.exit(application.exec_())
