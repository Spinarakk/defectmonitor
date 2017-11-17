# Import libraries and modules
import os
import sys
import subprocess
import json
import cv2
import numpy as np
import serial
import bisect
import math

# Import PyQt modules
from PyQt5.QtCore import *
from PyQt5.QtGui import *
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

        # Set the window icon
        self.setWindowIcon(QIcon('gui/logo.ico'))

        # Load default working build settings from the hidden non-user accessible build_default.json file
        with open('build_default.json') as build:
            self.build = json.load(build)

        # Load config settings from the config.json file
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
        self.actionClearBuilds.triggered.connect(self.clear_recent_builds)
        self.actionSave.triggered.connect(self.save_build)
        self.actionSaveAs.triggered.connect(self.save_as_build)
        self.actionExportImage.triggered.connect(self.export_image)
        self.actionExit.triggered.connect(self.exit_program)

        # Menubar -> View
        self.actionZoomIn.triggered.connect(self.zoom_in)
        self.actionZoomOut.triggered.connect(self.zoom_out)
        self.actionCalibrationResults.triggered.connect(self.calibration_results)
        self.actionDefectReports.triggered.connect(self.defect_reports)

        # Menubar -> Tools
        self.actionCameraCalibration.triggered.connect(self.camera_calibration)
        self.actionOverlayAdjustment.triggered.connect(self.overlay_adjustment)
        self.actionSliceConverter.triggered.connect(self.slice_converter)
        self.actionImageConverter.triggered.connect(self.image_converter)
        self.actionUpdateFolders.triggered.connect(self.update_folders)
        self.actionUpdateFolders.triggered.connect(lambda: self.update_status('Image folders updated.', 3000))
        self.actionProcessCurrent.triggered.connect(self.process_current)
        self.actionProcessAll.triggered.connect(self.process_all)

        # Menubar -> Settings
        self.actionCameraSettings.triggered.connect(self.camera_settings)
        self.actionBuildSettings.triggered.connect(self.build_settings)
        self.actionAdvancedMode.triggered.connect(self.advanced_mode)

        # Menubar -> Help
        self.actionViewHelp.triggered.connect(self.view_help)
        self.actionAbout.triggered.connect(self.view_about)

        # Display Options Group Box
        self.radioRaw.clicked.connect(self.update_display)
        self.radioFixed.clicked.connect(self.update_display)
        self.checkCLAHE.toggled.connect(self.update_display)
        self.checkContours.toggled.connect(self.toggle_part_contours)
        self.checkNames.toggled.connect(self.update_display)

        # Overlay Defects Group Box
        self.checkStreak.toggled.connect(self.toggle_streak)
        self.checkChatter.toggled.connect(self.toggle_chatter)
        self.checkPatch.toggled.connect(self.toggle_patch)
        self.checkOutlier.toggled.connect(self.toggle_outlier)
        self.checkPattern.toggled.connect(self.toggle_pattern)

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
        self.pushDefectReports.clicked.connect(self.defect_reports)

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

        # Instantiate dialog variables that cannot have multiple windows for existence validation purposes
        self.DR_dialog = None  # Defect Reports
        self.CC_dialog = None  # Camera Calibration
        self.OA_dialog = None  # Overlay Adjustment
        self.SC_dialog = None  # Slice Converter
        self.CS_dialog = None  # Camera Settings

        # Initiate an empty config file name to be used for saving purposes
        self.build_name = None

        # Initialize the counter for the defect processing method
        self.defect_counter = 0

        # These two lists are used to store the order in which the defect checkboxes were checked and the defect colours
        self.defect_checkboxes = list()
        self.defect_colours = {'Streaks': (0, 0, 255), 'Chatter': (255, 0, 0), 'Patches': (0, 255, 0),
                               'Outliers': (0, 255, 255), 'Pattern': (255, 0, 255)}

        # Create a context menu that will appear when the user right-clicks on any of the display labels
        self.menu_display = QMenu()

        # Fill the Recent Builds drop-down menu with the recent builds
        self.add_recent_builds('')

        # Set the data table's columns and rows to automatically resize appropriately to make it as small as possible
        # self.tableDefects.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableDefects.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableDefects.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.update_table_empty()

        # Because each tab on the widgetDisplay has its own set of associated images, display labels and sliders
        # And because they all do essentially the same functions
        # Easier to store each of these in a dictionary under a specific key to call on one of the four sets
        # The current tab's index will be used to grab the corresponding image, list or name
        self.display = {'ImageList': [list(), list(), list(), list()], 'MaxLayers': 1,
                        'FolderNames': ['Coat/', 'Scan/', 'Contour/', 'Single/'], 'CurrentLayer': [1, 1, 1, 1],
                        'LayerNumbers': [list(), list(), list(), list()],
                        'StackNames': [self.stackedCE, self.stackedSE, self.stackedPC, self.stackedIC],
                        'LabelNames': [self.labelCE, self.labelSE, self.labelPC, self.labelIC],
                        'GraphicsNames': [self.graphicsCE, self.graphicsSE, self.graphicsPC, self.graphicsIC],
                        'DisplayImage': [0, 0, 0, 0],
                        'CheckboxNames': [self.checkStreak, self.checkChatter, self.checkPatch, self.checkOutlier,
                                          self.checkPattern]}

        # Create a QThreadPool which contains an amount of threads that can be used to simultaneously run functions
        self.threadpool = QThreadPool()

    # MENUBAR -> FILE

    def new_build(self):
        """Opens a Modal Dialog Window when File -> New... is clicked
        Allows the user to setup a new build and change settings
        """

        # Create a new build dialog variable and execute it as a modal window
        NB_dialog = dialog_windows.NewBuild(self)

        # Executes the build setup if the OK button is clicked, otherwise nothing happens
        if NB_dialog.exec_():
            self.setup_build()

    def open_build(self):
        """Opens a File Dialog when File -> Open... is clicked or if a recent build action is clicked
        Allows the user to select a previous build's settings
        Subsequently opens the New Build Dialog Window with all the boxes filled in, allowing the user to make changes
        """

        filename = ''

        # Because using lambda and sending the build name outright doesn't work, a workaround is needed
        # The sending QAction is instead queried against a list of QActions in the QMenu for the corresponding index
        # This index is used to grab the full build name path from the build list
        # If none of the actions match, it means that this method was called by the Open Builds action
        for index, action in enumerate(self.menuRecentBuilds.actions()):
            if action is self.sender():
                # Set the filename to the corresponding name in the recent builds list
                filename = self.recent_builds_list[index]

                # Check if the build's json file exists
                if not os.path.isfile(filename):
                    missing_file_error = QMessageBox(self)
                    missing_file_error.setWindowTitle('Error')
                    missing_file_error.setIcon(QMessageBox.Critical)
                    missing_file_error.setText('The file %s could not be opened.\n\nNo such file exists.' % filename)
                    missing_file_error.exec_()

                    # Reset the Recent Builds menu to account for the missing files
                    self.add_recent_builds('')
                    return
                break

        if not filename:
            # Open a File Dialog to allow the user to select a file if it wasn't a recent build that was selected
            filename = QFileDialog.getOpenFileName(self, 'Open', self.build['BuildInfo']['Folder'],
                                                   'JSON File (*.json)')[0]

        # Check if a file has been selected as QFileDialog returns an empty string if cancel was pressed
        if filename:
            # Load from the selected build file and overwrite the contents of the working build dictionary
            with open(filename) as build:
                self.build = json.load(build)

            with open('build.json', 'w+') as build:
                json.dump(self.build, build, indent=4, sort_keys=True)

            self.build_name = filename

            OB_dialog = dialog_windows.NewBuild(self, open_flag=True)

            if OB_dialog.exec_():
                # Add the opened build name to the Recent Builds drop-down menu
                self.add_recent_builds(self.build_name)

                self.setup_build()

    def setup_build(self, settings_flag=False):
        """Sets up the widgetDisplay and any background processes for the current build"""

        # Reload any modified build settings that the New Build dialog has changed
        with open('build.json') as build:
            self.build = json.load(build)

        # Update the window title with the build name
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
            self.actionUpdateFolders.setEnabled(True)
            self.spinLayer.setEnabled(True)
            self.toolSidebar.setCurrentIndex(2)

            # Store the names of the four folders containing the display images in the display dictionary
            self.display['ImageFolder'] = ['%s/fixed/coat' % self.build['ImageCapture']['Folder'],
                                           '%s/fixed/scan' % self.build['ImageCapture']['Folder'],
                                           '%s/contours' % self.build['ImageCapture']['Folder'],
                                           '%s/fixed/single' % self.build['ImageCapture']['Folder']]

            # Update the list of images for all four image folders
            self.update_folders()

            # Set the display flag to true to allow tab changes to update images and update the display with an image
            self.display_flag = True
            self.update_display()

        # Converts and draws the contours if set to do so in the build settings
        if self.build['BuildInfo']['Convert']:
            # Set the appropriate flags in the config.json file to run the slice conversion
            self.build['BuildInfo']['Pause'] = False
            self.build['BuildInfo']['Run'] = True
            self.build['SliceConverter']['Build'] = True

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

        with open('build.json') as build:
            self.build = json.load(build)

        if 'Pause' in self.pushPauseConversion.text():
            self.build['BuildInfo']['Pause'] = True
            self.pushPauseConversion.setText('Resume')
        elif 'Resume' in self.pushPauseConversion.text():
            self.build['BuildInfo']['Pause'] = False
            self.pushPauseConversion.setText('Pause')

        with open('build.json', 'w+') as build:
            json.dump(self.build, build, indent=4, sort_keys=True)

    def setup_build_finished(self, settings_flag):
        """Executes when the slice conversion process is finished, or the Stop button is pressed"""

        with open('build.json') as build:
            self.build = json.load(build)

        self.build['BuildInfo']['Pause'] = False
        self.build['BuildInfo']['Run'] = False

        with open('build.json', 'w+') as build:
            json.dump(self.build, build, indent=4, sort_keys=True)

        # Check for and acquire an attached camera and trigger
        # This method is here so that the image capture cannot be run unless the slice conversion has stopped
        self.acquire_ct()

        self.pushPauseConversion.setEnabled(False)
        self.pushStopConversion.setEnabled(False)

        if not settings_flag:
            self.update_folders()
            self.update_progress(0)
            self.update_status('Build %s setup complete.' % self.build['BuildInfo']['Name'], 5000)
        else:
            self.update_status('Build %s settings changed' % self.build['BuildInfo']['Name'], 5000)

    def add_recent_builds(self, build_name):
        """Adds a new or opened build to the top of the Recent Builds drop-down menu"""

        with open('config.json') as config:
            self.config = json.load(config)

        # Add the opened/saved build name to the list, only if a build name was sent
        # And if it doesn't match a build already in the list, otherwise send that build to the end of the list
        if build_name:
            if build_name in self.config['RecentBuilds']:
                self.config['RecentBuilds'].remove(build_name)
            self.config['RecentBuilds'].append(build_name)

        # Delete the first element if the Recent Builds list gets longer than 10 builds
        if len(self.config['RecentBuilds']) > 10:
            del self.config['RecentBuilds'][0]

        # Store the recent builds list as an instance variable that has been reversed
        self.recent_builds_list = self.config['RecentBuilds'][::-1]

        # Clear the Recent Builds menu and add the reversed list of Recent Builds as actions with connected slots
        # Though first check that these builds exist on disk otherwise remove them from the list
        self.menuRecentBuilds.clear()
        for build in self.recent_builds_list:
            if os.path.isfile(build):
                action = self.menuRecentBuilds.addAction(os.path.basename(build))
                action.triggered.connect(self.open_build)
            else:
                # If the file doesn't exist, remove the build from both lists
                self.recent_builds_list.remove(build)
                self.config['RecentBuilds'].remove(build)

        # Add a separator and finally the Clear Builds action
        self.menuRecentBuilds.addSeparator()
        self.actionClearBuilds = self.menuRecentBuilds.addAction('Clear Builds')
        self.actionClearBuilds.triggered.connect(self.clear_recent_builds)

        with open('config.json', 'w+') as config:
            json.dump(self.config, config, indent=4, sort_keys=True)

    def clear_recent_builds(self):
        """Clears the Recent Builds drop-down menu and the config.json file of all the listed recent builds"""

        with open('config.json') as config:
            self.config = json.load(config)

        # Empties the recent builds list in the config.json file
        self.config['RecentBuilds'] = list()

        # Clear the Recent Builds menu and re-add the Clear Builds QAction
        self.menuRecentBuilds.clear()
        self.actionClearBuilds = self.menuRecentBuilds.addAction('Clear Builds')
        self.actionClearBuilds.triggered.connect(self.clear_recent_builds)

        with open('config.json', 'w+') as config:
            json.dump(self.config, config, indent=4, sort_keys=True)

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

        filename = QFileDialog.getSaveFileName(self, 'Save As', '%s/%s' %
                                               (self.build['BuildInfo']['Folder'], self.build['BuildInfo']['Name']),
                                               'JSON File (*.json)')[0]

        # Checking if user has chosen to save the build or clicked cancel
        if filename:
            self.build_name = filename

            # Add the opened build name to the Recent Builds drop-down menu
            self.add_recent_builds(self.build_name)

            self.save_build()

    def export_image(self):
        """Opens a FileDialog Window when File > Export Image... is clicked
        Allows the user to save the currently displayed image to whatever location the user specifies as a .png
        """

        # Open a folder select dialog, allowing the user to choose a location and input a name
        image_name = QFileDialog.getSaveFileName(self, 'Export Image', '', 'Image (*.png)')[0]

        # Checking if user has chosen to save the image or clicked cancel
        if image_name:
            # Save the currently displayed image which is saved as an entry in the display dictionary
            cv2.imwrite(image_name, self.display['DisplayImage'][self.widgetDisplay.currentIndex()])

            # Open a message box with a save confirmation message
            export_confirmation = QMessageBox(self)
            export_confirmation.setWindowTitle('Export Image')
            export_confirmation.setIcon(QMessageBox.Information)
            export_confirmation.setText('The image has been saved as %s.' % image_name)
            export_confirmation.exec_()

    def exit_program(self):
        """Connecting actionExit to closeEvent directly doesn't work so the window close needs to be called instead"""
        self.close()

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
        image_name = QFileDialog.getOpenFileName(self, 'Image Converter', '', 'Image Files (*.png)')[0]

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
        status.emit('Image successfully converted and saved to same folder as input image.')

        return os.path.dirname(image_name).replace('/', '\\')

    @staticmethod
    def image_converter_finished(image_folder):
        """Open the folder containing the converted images for the user to view after conversion is finished"""
        subprocess.Popen('explorer %s' % image_folder)

    # MENUBAR -> TOOLS -> DEFECT PROCESSOR

    def process_current(self):
        """Runs the currently displayed image through the DefectDetector and saves it to the appropriate folder
        This is done by saving pertinent information such as the image file names, layer and phase
        To the config.json file, which is then loaded by the Detector"""

        # Flag used to indicate that only one image is to be processed which prevents the loop
        self.all_flag = False

        # The widgetDisplay's tab is saved at this instance so that changing the tab doesn't affect the process
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

            # Remove the already processed defect images from the image list as dictated by the combined report keys
            with open('%s/reports/combined_report.json' % self.build['ImageCapture']['Folder']) as report:
                report = json.load(report)

            phases = ['coat', 'scan']
            layers = list()
            for layer in report.keys():
                if phases[self.tab_index] in report[layer]:
                    layers.append(int(layer))

            self.layer_numbers = sorted(list(set(self.display['LayerNumbers'][self.tab_index]) - set(layers)))
            self.process_settings(self.layer_numbers[self.defect_counter])

        elif 'Process Stop' in self.pushProcessAll.text():
            # On the next process loop, setting this to False will send the process to the finished method
            self.all_flag = False
            self.pushProcessAll.setStyleSheet('')
            self.pushProcessAll.setText('Process All')
            self.actionProcessAll.setText('Process All')
            self.toggle_processing_buttons(3)

    def process_settings(self, layer):
        """Saves the settings to be used to process an image for defects to the build.json file
        This method exists as the only difference between the two options is the layer number"""

        self.processing_flag = True

        with open('build.json') as build:
            self.build = json.load(build)

        # Grab some pertinent information (for clearer code purposes)
        phase = self.display['FolderNames'][self.tab_index][:-1].lower()

        self.build['DefectDetector']['Image'] = self.display['ImageList'][self.tab_index][layer - 1]
        self.build['DefectDetector']['Contours'] = self.display['ImageList'][2][layer - 1]
        self.build['DefectDetector']['Layer'] = layer
        self.build['DefectDetector']['Phase'] = phase

        # Set the previous image to be compared against the current image if it is not the first layer
        if layer > 1:
            self.build['DefectDetector']['ImagePrevious'] = self.display['ImageList'][self.tab_index][layer - 2]
        else:
            self.build['DefectDetector']['ImagePrevious'] = ''

        with open('build.json', 'w+') as build:
            json.dump(self.build, build, indent=4, sort_keys=True)

        # Vary the status message to display depending on which button was pressed
        if self.all_flag:
            self.toggle_processing_buttons(4)
            self.defect_counter += 1
            self.update_status('Running %s layer %s through the Defect Detector...' % (phase, str(layer).zfill(4)))
        else:
            self.update_status('Running displayed %s image through the Defect Detector...' % phase)

        worker = qt_multithreading.Worker(image_processing.DefectDetector().run_detector)
        worker.signals.status.connect(self.update_status)
        worker.signals.progress.connect(self.update_progress)
        worker.signals.finished.connect(self.process_finished)
        self.threadpool.start(worker)

    def process_finished(self):
        """Decides whether the Defect Processor needs to be run again for consecutive images
        Otherwise the window is set to its processing finished state"""

        self.processing_flag = False
        self.update_table()
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

        # State 1 is when the current tab of images CANNOT be processed
        if state == 1:
            self.pushProcessCurrent.setEnabled(False)
            self.actionProcessCurrent.setEnabled(False)
            self.pushProcessAll.setEnabled(False)
            self.actionProcessAll.setEnabled(False)
        # State 2 is when the current image CAN be processed
        elif state == 2:
            self.pushProcessCurrent.setEnabled(True)
            self.actionProcessCurrent.setEnabled(True)
            self.pushProcessAll.setEnabled(True)
            self.actionProcessAll.setEnabled(True)
        # State 3 is when a Process Current or Process Selected process is running
        elif state == 3:
            self.pushProcessCurrent.setEnabled(False)
            self.actionProcessCurrent.setEnabled(False)
            self.pushProcessAll.setEnabled(False)
            self.actionProcessAll.setEnabled(False)
        # State 4 is when a Process All is running
        elif state == 4:
            self.pushProcessCurrent.setEnabled(False)
            self.actionProcessCurrent.setEnabled(False)
            self.pushProcessAll.setEnabled(True)
            self.actionProcessAll.setEnabled(True)
        # State 5 is when the current image CANNOT be processed but the tab still has other images that CAN
        elif state == 5:
            self.pushProcessCurrent.setEnabled(False)
            self.actionProcessCurrent.setEnabled(False)
            self.pushProcessAll.setEnabled(True)
            self.actionProcessAll.setEnabled(True)

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
            self.pushOverlayAdjustment.setEnabled(self.checkContours.isChecked())
            self.actionOverlayAdjustment.setEnabled(self.checkContours.isChecked())

        self.update_display()

        # Only disable the following button if it is enabled in the first place
        if self.pushCapture.isEnabled():
            self.pushCapture.setEnabled(False)

    # MENUBAR -> HELP

    def view_help(self):
        pass

    def view_about(self):
        """Opens a Modal About QMessageBox displaying some pertinent information about the application"""

        QMessageBox.about(self, 'About Defect Monitor',
                          '<b>Defect Monitor</b><br><br>Version 0.7.3<br> Defect Monitor is a monitoring application '
                          'used to detect defects within the scan and coat layers of a 3D metal printing build.'
                          '<br><br>Copyright (C) 2017 MCAM.')

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

        # Check whether the build has been saved before running anything
        if self.build_name is None:
            # Open a message box with a save confirmation message so that the user can save the build before running
            save_confirmation = QMessageBox(self)
            save_confirmation.setWindowTitle('Run')
            save_confirmation.setIcon(QMessageBox.Information)
            save_confirmation.setText('The current build needs to be saved before it can be run.\n\n'
                                      'Save the current build?')
            save_confirmation.setStandardButtons(QMessageBox.Save | QMessageBox.Cancel)
            retval = save_confirmation.exec_()

            # Save the build if prompted, otherwise exit the method
            if retval == 2048:
                self.save_as_build()
            else:
                return

        with open('build.json') as build:
            self.build = json.load(build)

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

        # Autosave the build to retain capture numbering
        self.save_build()
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
            image_name = image_name.replace('coatR', 'coatF').replace('raw', 'fixed')
        elif 'scan' in image_name:
            image_name = image_name.replace('scanR', 'scanF').replace('raw', 'fixed')
        elif 'single' in image_name:
            image_name = image_name.replace('singleR', 'singleF').replace('raw', 'fixed')

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

        # Set the tab to focus on the current phase and layer number
        self.tab_focus(index, layer)

        # Process only the coat or scan image for defects, the image being the one the above method set focus to
        if index < 2:
            self.process_current()

    # DISPLAY

    def update_display(self):
        """Updates the MainWindow widgetDisplay to show an image on the currently displayed tab as per toggles
        Also responsible for enabling or disabling UI elements if there is or isn't an image to be displayed"""

        # Grab the names of certain elements (for clearer code purposes)
        index = self.widgetDisplay.currentIndex()
        label = self.display['LabelNames'][index]
        stack = self.display['StackNames'][index]
        image_list = self.display['ImageList'][index]
        image_folder = self.build['ImageCapture']['Folder']
        value = self.sliderDisplay.value()
        layer = str(value).zfill(4)
        phase = self.display['FolderNames'][index][:-1].lower()

        # Check if the image folder has an actual image to display
        if list(filter(bool, image_list)):
            # Change the stacked widget to the one with the image viewer
            stack.setCurrentIndex(1)

            # Grab the filename of the main fixed image from the fixed image list
            filename = image_list[value - 1]

            # Initially assume an image is being displayed
            self.toggle_display_checkboxes(index)

            # Check if the Raw or Fixed radio button is checked to see whether to display the raw or fixed image
            if self.radioRaw.isChecked():
                # Check if the corresponding raw image exists in the raw folder
                filename_raw = filename.replace('fixed', 'raw').replace('F_', 'R_')
                self.toggle_display_checkboxes(5)
                if os.path.isfile(filename_raw):
                    self.uncheck_defects()
                    self.update_image(cv2.imread(filename_raw))
                    return
                else:
                    # Set the stack tab to the information label and display an 'error' message
                    label.setText('%s Layer %s Raw Image does not exist.' % (phase.capitalize(), layer))
                    stack.setCurrentIndex(0)
                    self.toggle_display_control(2)
                    return
            # Otherwise load and display the fixed image
            else:
                # Check if the image exists in the first place (in case it gets deleted beteween folder checks)
                if os.path.isfile(filename):
                    image = cv2.imread(filename)

                    # Enable the Defect Processor toolbar and actions
                    if not self.processing_flag and index < 2:
                        self.toggle_processing_buttons(2)
                else:
                    # Set the stack tab to the information label and display the missing layer information
                    if index == 2:
                        # The part contours tab displays a slightly different message
                        label.setText('Contour Layer %s Image does not exist.' % layer)
                    else:
                        label.setText('%s Layer %s Fixed Image does not exist.' % (phase.capitalize(), layer))
                    stack.setCurrentIndex(0)
                    self.toggle_display_control(2)
                    self.toggle_display_checkboxes(4)

                    # Enable the Defect Processor toolbar and actions
                    if not self.processing_flag and index != 2:
                        self.toggle_processing_buttons(5)
                    return

            # Check if the following defect images exist, and enable or disable the corresponding checkboxes
            # Only do this for the coat and scan images
            if index < 2:
                base = os.path.basename(filename)
                defects = dict()
                defects['Streaks'] = '%s/defects/%s/streaks/%s' % (image_folder, phase, base.replace('F_', 'BS_'))
                defects['Chatter'] = '%s/defects/%s/chatter/%s' % (image_folder, phase, base.replace('F_', 'BC_'))
                defects['Patches'] = '%s/defects/%s/patches/%s' % (image_folder, phase, base.replace('F_', 'SP_'))
                defects['Outliers'] = '%s/defects/%s/outliers/%s' % (image_folder, phase, base.replace('F_', 'CO_'))
                defects['Pattern'] = '%s/defects/%s/pattern/%s' % (image_folder, phase, base.replace('F_', 'OC_'))

                self.checkStreak.setEnabled(os.path.isfile(defects['Streaks']))
                self.checkChatter.setEnabled(os.path.isfile(defects['Chatter']))
                self.checkPatch.setEnabled(os.path.isfile(defects['Patches']))
                self.checkOutlier.setEnabled(os.path.isfile(defects['Outliers']))
                self.checkPattern.setEnabled(os.path.isfile(defects['Pattern']))

                # Overlay the defects in the order they were selected
                for defect in self.defect_checkboxes:
                    mask = cv2.inRange(cv2.imread(defects[defect]), self.defect_colours[defect],
                                       self.defect_colours[defect])
                    image[np.nonzero(mask)] = self.defect_colours[defect]

            # The following conditionals are to check whether to overlay the corresponding images on the current image
            # Overlay the part contours
            if self.checkContours.isChecked():
                # Load the overlay image into memory
                contours = cv2.imread(self.display['ImageList'][2][value - 1])

                # Resize the overlay image if the resolution doesn't match the displayed image
                if contours.shape[:2] != image.shape[:2]:
                    contours = cv2.resize(contours, image.shape[:2][::-1], interpolation=cv2.INTER_CUBIC)

                # Apply the stored transformation values to the overlay image
                contours = image_processing.ImageTransform().apply_transformation(contours, True)

                # Apply the overlay on top of the image
                image = cv2.add(image, contours)

            # Overlay the part names
            if self.checkNames.isChecked():
                # Load the part names image into memory
                image_names = cv2.imread('%s/part_names.png' % image_folder)

                # Resize the overlay image if the resolution doesn't match the displayed image
                if image_names.shape[:2] != image.shape[:2]:
                    image_names = cv2.resize(image_names, image.shape[:2][::-1], interpolation=cv2.INTER_CUBIC)

                image = cv2.add(image, image_names)

            self.update_image(image)
        else:
            # If the entire folder is empty, change the stacked widget to the one with the information label
            label.setText('%s folder empty. Nothing to display.' % phase.capitalize())
            stack.setCurrentIndex(0)

            self.toggle_display_control(1)
            self.toggle_display_checkboxes(4)

            # # Check if the following images exist and enable/disable the corresponding checkbox
            # # Exclude the Image Capture tab from the following conditions, whereby all the checkboxes will be disabled
            # if index < 3:
            #     # Part Names
            #     if os.path.isfile('%s/part_names.png' % image_folder):
            #         self.checkNames.setEnabled(True)
            #     else:
            #         self.checkNames.setEnabled(False)
            #         self.checkNames.setChecked(False)

    def update_image(self, image):
        """These functions were moved to a separate method as they are called multiple times"""

        # Applies CLAHE to the display image
        if self.checkCLAHE.isChecked():
            image = image_processing.ImageTransform.clahe(image)

        # Convert from OpenCV's BGR format to RGB so that colours are displayed correctly
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Display the image on the current GraphicsView
        self.display['GraphicsNames'][self.widgetDisplay.currentIndex()].set_image(image)

        # Save the current (modified) image so that it can be exported if need be
        self.display['DisplayImage'][self.widgetDisplay.currentIndex()] = image

        self.toggle_display_control(3)

    def update_table(self):
        """Updates the Defect Data table with the current layer's defect data if available"""

        # Load the defect (combined) data from the report JSON file
        with open('%s/reports/combined_report.json' % self.build['ImageCapture']['Folder']) as report:
            report = json.load(report)

        index = self.widgetDisplay.currentIndex()
        layer = str(self.sliderDisplay.value()).zfill(4)
        colours = list()

        # Process to fill the table is very similar to the display_report method within the DefectReports class
        # Therefore this section will not be commented at all
        if report:
            if index == 0:
                thresholds = [self.config['Threshold']['Occurrences'], self.config['Threshold']['Occurrences'],
                              self.config['Threshold']['PixelSize'], self.config['Threshold']['PixelSize'],
                              self.config['Threshold']['HistogramCoat'], None]

                try:
                    data = report[layer]['coat']
                except (IndexError, KeyError):
                    self.update_table_empty()
                    return

                if data:
                    data_sorted = [data['BS'][1], data['BC'][1], data['SP'][0], data['CO'][0], 0, 0]

                    try:
                        data_sorted[4] = round(data['HC'], 2)
                    except (KeyError, IndexError):
                        pass

                    for index, value in enumerate(data_sorted):
                        if thresholds[index] is None:
                            colours.append(QColor(255, 255, 255))
                        elif value < thresholds[index]:
                            colours.append(QColor(0, 255, 0))
                        else:
                            colours.append(QColor(255, 0, 0))
                else:
                    self.update_table_empty()
                    return

            elif index == 1:
                thresholds = [self.config['Threshold']['Occurrences'], self.config['Threshold']['Occurrences'],
                              None, None, self.config['Threshold']['HistogramScan'],
                              self.config['Threshold']['Overlay']]

                try:
                    data = report[layer]['scan']
                except (IndexError, KeyError):
                    self.update_table_empty()
                    return

                if data:
                    data_sorted = [data['BS'][1], data['BC'][1], 0, 0, 0, 0]

                    try:
                        data_sorted[4] = round(data['HC'], 2)
                    except (KeyError, IndexError):
                        pass

                    try:
                        data_sorted[5] = round(data['OC'] * 100, 4)
                    except (KeyError, IndexError):
                        pass

                    for index, value in enumerate(data_sorted):
                        if thresholds[index] is None:
                            colours.append(QColor(255, 255, 255))
                        elif value < thresholds[index] and index < 5:
                            colours.append(QColor(0, 255, 0))
                        elif value > thresholds[index] and index == 5:
                            colours.append(QColor(0, 255, 0))
                        else:
                            colours.append(QColor(255, 0, 0))

                else:
                    self.update_table_empty()
                    return

            for row in range(6):
                self.tableDefects.setItem(row, 0, QTableWidgetItem(str(data_sorted[row])))
                self.tableDefects.item(row, 0).setBackground(colours[row])
        else:
            self.update_table_empty()

    def update_table_empty(self):
        """Updates the Defect Data table with empty 0 values with a white background if the data isn't available
        Or if the current tab isn't either the coat or scan tabs"""

        for row in range(6):
            self.tableDefects.setItem(row, 0, QTableWidgetItem('0'))
            self.tableDefects.item(row, 0).setBackground(QColor(255, 255, 255))

    def toggle_display_control(self, state):
        """Enables or disables the following buttons/actions in one fell swoop depending on the received state"""

        # State 1 - No images in folder
        if state == 1 or state == 2:
            self.actionZoomIn.setEnabled(False)
            self.actionZoomIn.setChecked(False)
            self.actionZoomOut.setEnabled(False)
            self.actionExportImage.setEnabled(False)
            self.frameSlider.setEnabled(False)
            self.pushGo.setEnabled(False)

            # State 2 - Image not found, have images in folder
            if state == 2:
                self.frameSlider.setEnabled(True)
                self.pushDisplayUpSeek.setEnabled(True)
                self.pushDisplayDownSeek.setEnabled(True)
                self.pushGo.setEnabled(True)
        # State 3 - Image found
        elif state == 3:
            self.actionZoomIn.setEnabled(True)
            self.actionZoomOut.setEnabled(True)
            self.actionExportImage.setEnabled(True)
            self.frameSlider.setEnabled(True)
            self.pushDisplayUpSeek.setEnabled(False)
            self.pushDisplayDownSeek.setEnabled(False)
            self.pushGo.setEnabled(True)

    def toggle_display_checkboxes(self, state):

        value = self.sliderDisplay.value()

        # State 4 - No image being displayed at all
        if state == 4:
            self.groupDisplayOptions.setEnabled(False)
            self.groupOverlayDefects.setEnabled(False)

        # State 0 or 1 - Coat or Scan tab clicked
        elif state == 0 or state == 1:
            self.groupDisplayOptions.setEnabled(True)
            self.groupOverlayDefects.setEnabled(True)
            self.radioRaw.setEnabled(True)

            if os.path.isfile(self.display['ImageList'][2][value - 1]):
                self.checkContours.setEnabled(True)
            else:
                self.checkContours.setEnabled(False)
                self.checkContours.setChecked(False)

        # State 2 - Part Contours tab clicked
        # State 3 - Image Capture tab clicked
        elif state == 2 or state == 3:
            self.groupDisplayOptions.setEnabled(True)
            self.groupOverlayDefects.setEnabled(False)
            self.checkContours.setEnabled(False)
            self.checkContours.setChecked(False)

            # Because the above changes are common to both states 3 and 4
            if state == 2:
                self.radioRaw.setEnabled(False)
            else:
                self.radioRaw.setEnabled(True)

                if os.path.isfile(self.display['ImageList'][2][value - 1]):
                    self.checkContours.setEnabled(True)
                else:
                    self.checkContours.setEnabled(False)
                    self.checkContours.setChecked(False)

        # State 5 - Raw image being displayed
        elif state == 5:
            self.groupOverlayDefects.setEnabled(False)
            self.checkContours.setEnabled(False)
            self.checkContours.setChecked(False)
            self.checkNames.setEnabled(False)
            self.checkNames.setChecked(False)

        # This state applies for all four tabs if an image is being displayed
        if state is not 4:
            if os.path.isfile('%s/part_names.png' % self.build['ImageCapture']['Folder']):
                self.checkNames.setEnabled(True)
            else:
                self.checkNames.setEnabled(False)
                self.checkNames.setChecked(False)

    def uncheck_defects(self):
        """Uncheck all the Overlay Defects checkboxes when changing tabs or images"""

        for checkbox in self.display['CheckboxNames']:
            checkbox.blockSignals(True)
            checkbox.setChecked(False)
            checkbox.blockSignals(False)

        self.defect_checkboxes = list()

    def toggle_part_contours(self):
        """Overlays or hides the part contours on top of the display image (if it exists)"""

        if self.actionAdvancedMode.isChecked():
            self.pushOverlayAdjustment.setEnabled(self.checkContours.isChecked())
            self.actionOverlayAdjustment.setEnabled(self.checkContours.isChecked())

        self.update_display()

    def toggle_streak(self):
        if self.checkStreak.isChecked():
            self.defect_checkboxes.append('Streaks')
        else:
            self.defect_checkboxes.remove('Streaks')

        self.update_display()

    def toggle_chatter(self):
        if self.checkChatter.isChecked():
            self.defect_checkboxes.append('Chatter')
        else:
            self.defect_checkboxes.remove('Chatter')

        self.update_display()

    def toggle_patch(self):
        if self.checkPatch.isChecked():
            self.defect_checkboxes.append('Patches')
        else:
            self.defect_checkboxes.remove('Patches')

        self.update_display()

    def toggle_outlier(self):
        if self.checkOutlier.isChecked():
            self.defect_checkboxes.append('Outliers')
        else:
            self.defect_checkboxes.remove('Outliers')

        self.update_display()

    def toggle_pattern(self):
        if self.checkPattern.isChecked():
            self.defect_checkboxes.append('Pattern')
        else:
            self.defect_checkboxes.remove('Pattern')

        self.update_display()

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
            if self.radioRaw.isChecked():
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
            # Set the slider's value to the saved layer value of the current tab
            self.sliderDisplay.setValue(self.display['CurrentLayer'][index])

            # Set the current layer number depending on the currently displayed tab
            self.labelLayerNumber.setText('%s / %s' % (str(self.display['CurrentLayer'][index]).zfill(4),
                                                       str(self.display['MaxLayers']).zfill(4)))

            # Set the radio button to Original as contours have no defect images
            if index == 2:
                self.radioFixed.setChecked(True)

            # Unchecks all the Overlay Defects checkboxes
            self.uncheck_defects()

            # Update the image on the graphics display with the new image (in case image has been deleted)
            self.update_display()

            # Update the Defect Data table if the coat or scan tabs are being displayed, otherwise set to 0
            if index < 2:
                self.update_table()
            else:
                self.update_table_empty()

            # Zoom out and reset the image
            self.display['GraphicsNames'][index].reset_image()

        self.sliderDisplay.blockSignals(False)

    def tab_focus(self, index, value, defect_flag=False):
        """Changes the tab focus to the received index's tab and sets the slider value to the received value
        Used for when an image has been captured and focus is to be given to the new image
        Also can be used for when an image has just finished processing for defects
        """
        # TODO FIX UP THE CLICKING OF THE REPORT TAB FOCUS
        # Double check if the received value is within the layer's range in the first place
        if value > self.display['MaxLayers']:
            self.update_status('Layer %s outside of the available layer range.' % str(value).zfill(4), 3000)
        else:
            # Set the display image to be the defect analyzed image
            if defect_flag:
                self.radioRaw.setChecked(True)

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

        # Unchecks all the Overlay Defects checkboxes
        self.uncheck_defects()

        # Update the image on the graphics display with the new image
        self.update_display()

        # Update the Defect Data table if the coat or scan tabs are being displayed
        if self.widgetDisplay.currentIndex() < 2:
            self.update_table()

    def slider_up(self):
        """Increments the slider by 1"""
        self.sliderDisplay.setValue(self.sliderDisplay.value() + 1)

    def slider_up_seek(self):
        """Jumps the slider to the first available image in the positive direction"""

        number_list = self.display['LayerNumbers'][self.widgetDisplay.currentIndex()]

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

        number_list = self.display['LayerNumbers'][self.widgetDisplay.currentIndex()]

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

        # Iterate through all but the last folder in the list (the single folder) and create a list of layer numbers
        for index, folder_name in enumerate(self.display['ImageFolder'][:-1]):
            # Reset the list of layer numbers in the display dictionary
            self.display['LayerNumbers'][index][:] = list()

            # Get a list of numbers of the supposed layer images in the folder (except the single folder)
            for filename in os.listdir(folder_name):
                # Only grab the .png images and ignore any other files in the folder
                if '.png' in filename:
                    try:
                        # Check if the last four characters of the filename are numbers, otherwise file is ignored
                        number = int(os.path.splitext(filename)[0][-4:])
                    except ValueError:
                        continue
                    else:
                        # Add the number to the list of layer numbers in the display dictionary
                        self.display['LayerNumbers'][index].append(number)

                        # Save the new number as the new max layer if it is higher than the previous saved number
                        if number > self.display['MaxLayers']:
                            self.display['MaxLayers'] = number

        # Iterate through all but the last folder in the list again
        # Repeated as the max layers needs to be determined first before creating a set list of image names
        for index, folder_name in enumerate(self.display['ImageFolder'][:-1]):
            # Replace the list with a max layer sized list of empty strings
            self.display['ImageList'][index] = ['' for _ in range(self.display['MaxLayers'])]

            for filename in os.listdir(folder_name):
                if '.png' in filename:
                    try:
                        # Check if the last four characters of the file name are numbers, otherwise file is ignored
                        number = int(os.path.splitext(filename)[0][-4:])
                    except ValueError:
                        continue
                    else:
                        # Save the current filename at the index as defined in the file's own name's number
                        self.display['ImageList'][index][number - 1] = '%s/%s' % (folder_name, filename)

        # Create a list of image names for the Single folder as well
        self.display['ImageList'][-1][:] = list()
        for filename in os.listdir(self.display['ImageFolder'][-1]):
            if '.png' in filename:
                self.display['ImageList'][-1].append('%s/%s' % (self.display['ImageFolder'][-1], filename))

        # Update the max layer range
        self.update_max_layers()

        if self.display_flag:
            # Reload any images in the current tab
            self.update_display()

    def update_max_layers(self):
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

        # Only ask to save if the user has actually started/opened a build, aka if the display flag is set
        if self.display_flag:
            # Open a message box with a save confirmation message so that the user can save the build before closing
            save_confirmation = QMessageBox(self)
            save_confirmation.setWindowTitle('Defect Monitor')
            save_confirmation.setIcon(QMessageBox.Warning)
            save_confirmation.setText('Do you want to save the changes to this build before closing?\n\n'
                                      'If you don\'t save, changes to your build will be lost.')
            save_confirmation.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            retval = save_confirmation.exec_()

            # Save the build if the Save button was pressed
            if retval == 2048:
                self.save_build()
            # Ignore the closing of the Main Window if the Cancel button was pressed
            elif retval == 4194304:
                event.ignore()
                # Otherwise just close the Main Window without saving


if __name__ == '__main__':
    application = QApplication(sys.argv)
    interface = MainWindow()
    interface.show()
    sys.exit(application.exec_())
