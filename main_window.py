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

# Import PyQt GUIs
from gui import mainWindow

# # Import related modules
import dialog_windows
import image_capture
import image_processing
import notifications
import qt_thread


class MainWindow(QMainWindow, mainWindow.Ui_mainWindow):
    """Module used to initiate the main GUI window and all of its associated dialogs/widgets
    Only methods that relate directly manipulating any element of the MainWindow UI are allowed in this module
    All other functions are called using the QThreadPool and split into their own separate modules
    """

    def __init__(self, parent=None):

        # Setup Main Window UI
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)
        self.window_settings = QSettings('MCAM', 'Defect Monitor')

        try:
            self.restoreGeometry(self.window_settings.value('Defect Monitor Geometry', ''))
        except TypeError:
            pass

        # Set the window icon
        self.setWindowIcon(QIcon('gui/logo.ico'))

        # Set the version number here
        self.version = '1.1.2'

        # Load default build settings from the hidden non-user accessible build_default.json file
        self.build = self.load('build_default.json')

        # Load config settings from the config.json file
        self.config = self.load('config.json')

        # Verify that the stored Build folder exists, and create a new default one if it doesn't
        if not os.path.isdir(self.config['BuildFolder']):
            self.config['BuildFolder'] = os.path.dirname(os.getcwd().replace('\\', '/')) + '/Builds'
            if not os.path.isdir(self.config['BuildFolder']):
                os.makedirs(self.config['BuildFolder'])

        # Save the default build to the current working build.json file (using w+ in case file doesn't exist)
        self.save(self.build, 'build.json')

        # Save the config settings to account for any new build folders
        self.save(self.config, 'config.json')

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        # Menubar -> File
        self.actionNew.triggered.connect(self.new_build)
        self.actionOpen.triggered.connect(self.open_build)
        self.actionClearBuilds.triggered.connect(self.clear_recent_builds)
        self.actionSave.triggered.connect(self.save_build)
        self.actionExportImage.triggered.connect(self.export_image)
        self.actionExit.triggered.connect(self.exit_program)

        # Menubar -> View
        self.actionZoomIn.triggered.connect(self.zoom_in)
        self.actionZoomOut.triggered.connect(self.zoom_out)
        self.actionCalibrationResults.triggered.connect(self.calibration_results)
        self.actionDefectReports.triggered.connect(self.defect_reports)

        # Menubar -> Tools
        self.actionCameraSettings.triggered.connect(self.camera_settings)
        self.actionCameraCalibration.triggered.connect(self.camera_calibration)
        self.actionAcquireCamera.triggered.connect(self.acquire_camera)
        self.actionAcquireTrigger.triggered.connect(self.acquire_trigger)
        self.actionStressTest.triggered.connect(self.stress_test)
        self.actionSliceConverter.triggered.connect(self.slice_converter)
        self.actionImageConverter.triggered.connect(self.image_converter)
        self.actionSnapshot.triggered.connect(self.snapshot)
        self.actionRun.triggered.connect(self.run_build)
        self.actionStop.triggered.connect(self.stop_build)
        self.actionFauxTrigger.triggered.connect(self.faux_trigger)
        self.actionProcessCurrent.triggered.connect(self.process_current)
        self.actionProcessAll.triggered.connect(self.process_all)

        # Menubar -> Settings
        self.actionBuildSettings.triggered.connect(self.build_settings)
        self.actionUpdateFolders.triggered.connect(lambda: self.update_folders(True))
        self.actionUpdateFolders.triggered.connect(lambda: self.update_status('Image folders updated.', 3000))
        self.actionPreferences.triggered.connect(self.preferences)

        # Menubar -> Help
        self.actionAbout.triggered.connect(self.about)

        # Display Options Group Box
        for element in self.groupDisplayOptions.findChildren(QCheckBox):
            element.toggled.connect(self.update_display)

        # Overlay Defects Group Box
        self.checkToggleAll.toggled.connect(self.toggle_all)
        self.checkStreak.toggled.connect(self.toggle_defect)
        self.checkChatter.toggled.connect(self.toggle_defect)
        self.checkPatch.toggled.connect(self.toggle_defect)
        self.checkOutlier.toggled.connect(self.toggle_defect)
        self.checkPattern.toggled.connect(self.toggle_defect)

        # Sidebar Toolbox Assorted Tools
        self.pushCameraCalibration.clicked.connect(self.camera_calibration)
        self.pushSliceConverter.clicked.connect(self.slice_converter)
        self.pushImageConverter.clicked.connect(self.image_converter)

        # Sidebar Toolbox Image Capture
        self.pushSnapshot.clicked.connect(self.snapshot)
        self.pushRun.clicked.connect(self.run_build)
        self.pushStop.clicked.connect(self.stop_build)

        # Sidebar Toolbox Defect Processor
        self.pushProcessCurrent.clicked.connect(self.process_current)
        self.pushProcessAll.clicked.connect(self.process_all)
        self.pushDefectReports.clicked.connect(self.defect_reports)

        # Layer Selection
        self.spinLayer.editingFinished.connect(self.set_layer)
        self.pushGo.clicked.connect(self.set_layer)

        # Display Widget
        self.widgetDisplay.currentChanged.connect(self.tab_change)
        for graphics in self.findChildren(QGraphicsView):
            graphics.zoom_done.connect(self.zoom_done)
            graphics.customContextMenuRequested.connect(self.context_menu_display)

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
        self.run_flag = False
        self.trigger_port = False

        # Initialize the counter for the defect processing method
        self.defect_counter = 0

        # These two lists are used to store the order in which the defect checkboxes were checked and the defect colours
        self.defect_checkbox = list()
        self.defect_colours = {'Streaks': (0, 0, 255), 'Chatter': (255, 0, 0), 'Patches': (0, 255, 0),
                               'Outliers': (0, 255, 255), 'Pattern': (255, 0, 255)}

        # Create a context menu that will appear when the user right-clicks on any of the display labels
        self.menu_display = QMenu()

        # Fill the Recent Builds drop-down menu with the recent builds
        self.add_recent_build('')

        # Set the data table's columns and rows to automatically resize appropriately to make it as small as possible
        self.tableDefects.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.update_table_empty()

        # Because each tab on the widgetDisplay has its own set of associated images, display labels and sliders
        # And because they all do essentially the same functions
        # Easier to store each of these in a dictionary under a specific key to call on one of the four sets
        # The current tab's index will be used to grab the corresponding image, list or name
        self.display = {'ImageList': [list(), list(), list(), list()], 'MaxLayers': 1,
                        'FolderNames': ['Coat/', 'Scan/', 'Contour/', 'Snapshot/'], 'CurrentLayer': [1, 1, 1, 1],
                        'LayerNumbers': [list(), list(), list(), list()],
                        'StackNames': [self.stackedCE, self.stackedSE, self.stackedPC, self.stackedIS],
                        'LabelNames': [self.labelCE, self.labelSE, self.labelPC, self.labelIS],
                        'GraphicsNames': [self.graphicsCE, self.graphicsSE, self.graphicsPC, self.graphicsIS],
                        'DisplayImage': [0, 0, 0, 0],
                        'CheckboxNames': [self.checkStreak, self.checkChatter, self.checkPatch, self.checkOutlier,
                                          self.checkPattern],
                        'DefectNames': ['Streaks', 'Chatter', 'Patches', 'Outliers', 'Pattern']}

        # Create a QThreadPool which contains an amount of threads that can be used to simultaneously run functions
        self.threadpool = QThreadPool()

    # MENUBAR -> FILE

    def new_build(self):
        """Opens the New Build dialog window"""

        # Execute the new build dialog variable as a modal window
        if dialog_windows.NewBuild(self).exec_():
            self.setup_build(False, False)

    def open_build(self):
        """Opens the Open Build dialog window, which is essentially the New Build window but with changed elements
        Only opens the window if the opened file exists, otherwise an error is displayed
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
                    self.add_recent_build('')
                    return
                break

        if not filename:
            # Open a File Dialog to allow the user to select a file if it wasn't a recent build that was selected
            filename = QFileDialog.getOpenFileName(self, 'Open', self.config['BuildFolder'], 'JSON File (*.json)')[0]

        # Check if a file has been selected as QFileDialog returns an empty string if cancel was pressed
        if filename:
            # Send and load the selected build's settings within the Open Build dialog window
            if dialog_windows.NewBuild(self, build_file=filename).exec_():
                # Add the opened build name to the Recent Builds drop-down menu
                self.add_recent_build(filename)
                self.setup_build(False, True)

    def setup_build(self, settings_flag=False, load_flag=False):
        """Sets up the display window and any background processes for the current build"""

        # Reload any modified build settings that the New Build dialog window has changed
        self.build = self.load('build.json')

        # Update the window title with the build name
        self.setWindowTitle('Defect Monitor - Build ' + self.build['BuildInfo']['Name'])
        self.update_progress(0)

        # Don't do the following if this method was triggered by changing the build settings
        if not settings_flag:
            # Enable certain UI elements
            self.actionSave.setEnabled(True)
            self.actionBuildSettings.setEnabled(True)
            self.actionAcquireCamera.setEnabled(True)
            self.actionAcquireTrigger.setEnabled(True)
            self.pushDefectReports.setEnabled(True)
            self.actionDefectReports.setEnabled(True)
            self.actionUpdateFolders.setEnabled(True)
            self.spinLayer.setEnabled(True)
            self.toolSidebar.setCurrentIndex(1)

            # Store the names of the four folders containing the display images in the display dictionary
            self.display['ImageFolder'] = ['%s/fixed/coat' % self.build['BuildInfo']['Folder'],
                                           '%s/fixed/scan' % self.build['BuildInfo']['Folder'],
                                           '%s/contours' % self.build['BuildInfo']['Folder'],
                                           '%s/fixed/snapshot' % self.build['BuildInfo']['Folder']]

            # Set the display flag to true to allow tab changes to update images
            self.display_flag = True

            # Check and acquire an attached camera and trigger if available
            self.acquire_camera()
            self.acquire_trigger()

            # Update the display to start displaying images
            self.update_folders(True)

            if not load_flag:
                # Open the Slice Converter dialog window to let the user add slice files to the build
                self.slice_converter()

            self.update_status('Build %s setup complete.' % self.build['BuildInfo']['Name'], 5000)
        else:
            self.update_status('Build %s settings changed' % self.build['BuildInfo']['Name'], 5000)

    def add_recent_build(self, build_name):
        """Adds a new or opened build to the top of the Recent Builds drop-down menu
        Also does some list management processes to ensure the drop-down menu appears as expected
        """

        self.config = self.load('config.json')

        # Add the opened/saved build name to the list, only if a build name was sent
        # And send the build to the end of the list if it already is on the list
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
                self.config['RecentBuilds'].remove(build)

        # Copy the reversed list again in case files got removed
        self.recent_builds_list = self.config['RecentBuilds'][::-1]

        # Add a separator and finally the Clear Builds action
        self.menuRecentBuilds.addSeparator()
        self.actionClearBuilds = self.menuRecentBuilds.addAction('Clear Builds')
        self.actionClearBuilds.triggered.connect(self.clear_recent_builds)

        self.save(self.config, 'config.json')

    def clear_recent_builds(self):
        """Clears the Recent Builds drop-down menu and the config.json file of all the listed recent builds"""

        self.config = self.load('config.json')

        # Empties the recent builds list in the config.json file
        self.config['RecentBuilds'] = list()

        # Clear the Recent Builds menu and re-add the Clear Builds QAction
        self.menuRecentBuilds.clear()
        self.actionClearBuilds = self.menuRecentBuilds.addAction('Clear Builds')
        self.actionClearBuilds.triggered.connect(self.clear_recent_builds)
        self.save(self.config, 'config.json')

    def save_build(self):
        """Saves the current build to the set build setting's filename"""

        # Reload the build settings in case of any changes
        self.build = self.load('build.json')
        self.save(self.build, self.build['Filename'])
        self.update_status('Build saved to %s.' % self.build['Filename'], 5000)

    def export_image(self):
        """Saves the currently displayed image to whatever location the user specifies as a .png"""

        # Open a folder select dialog, allowing the user to choose a location and input a name
        filename = QFileDialog.getSaveFileName(self, 'Export Image', '', 'Image (*.png)')[0]

        # Checking if user has chosen to save the image or clicked cancel
        if filename:
            # Convert the displayed image (which is saved as an entry in the display dictionary) from BGR to RGB
            image = cv2.cvtColor(self.display['DisplayImage'][self.widgetDisplay.currentIndex()], cv2.COLOR_BGR2RGB)
            cv2.imwrite(filename, image)

            # Open a message box with an export confirmation message
            export_confirmation = QMessageBox(self)
            export_confirmation.setWindowTitle('Export Image')
            export_confirmation.setIcon(QMessageBox.Information)
            export_confirmation.setText('The image has been exported to %s.' % filename)
            export_confirmation.exec_()

    def exit_program(self):
        """Connecting actionExit to closeEvent directly doesn't work so the window close needs to be called instead"""
        self.close()

    # MENUBAR -> VIEW

    def zoom_in(self):
        """Sets the currently displayed Graphics Viewer's zoom function on"""
        self.display['GraphicsNames'][self.widgetDisplay.currentIndex()].zoom_flag = self.actionZoomIn.isChecked()

    def zoom_done(self):
        """Disables the zoom function and the checked status of the Zoom In action after performing a zoom action"""
        self.actionZoomIn.setChecked(False)
        self.display['GraphicsNames'][self.widgetDisplay.currentIndex()].zoom_flag = False

    def zoom_out(self):
        """Resets the zoom state of the currently displayed Graphics Viewer"""
        self.display['GraphicsNames'][self.widgetDisplay.currentIndex()].reset_image()

    def calibration_results(self):
        """Opens the Calibration Results dialog window"""

        try:
            self.CR_dialog.close()
        except (AttributeError, RuntimeError):
            pass

        # Load from the config.json file (that contains the calibration results)
        self.CR_dialog = dialog_windows.CalibrationResults(self, self.load('config.json')['ImageCorrection'])
        self.CR_dialog.show()

    def defect_reports(self):
        """Opens the Defect Reports dialog window"""

        try:
            self.DR_dialog.close()
        except (AttributeError, RuntimeError):
            pass

        self.DR_dialog = dialog_windows.DefectReports(self)
        self.DR_dialog.tab_focus.connect(self.tab_focus)
        self.DR_dialog.show()

    # MENUBAR -> TOOLS

    def camera_calibration(self):
        """Opens the Camera Calibration dialog window"""
        dialog_windows.CameraCalibration(self).exec_()

    def stress_test(self):
        """Opens the Stress Test dialog window"""
        dialog_windows.StressTest(self).exec_()

    def slice_converter(self):
        """Opens the Slice Converter dialog window"""

        dialog_windows.SliceConverter(self).exec_()

        # Reload the build.json file and update the folders and display when the Slice Converter window is closed
        if self.display_flag:
            self.build = self.load('build.json')
            self.update_folders(True)

    def image_converter(self):
        """Opens the Image Converter dialog window"""
        dialog_windows.ImageConverter(self).exec_()

    # MENUBAR -> TOOLS -> DEFECT PROCESSOR

    def process_current(self):
        """Runs the currently displayed image through the Defect Processor and saves it to the appropriate folder"""

        # Flag used to indicate that only one image is to be processed which prevents the loop
        self.all_flag = False

        # The widgetDisplay's tab is saved at this instance so that changing the tab doesn't affect the process
        self.tab_index = self.widgetDisplay.currentIndex()
        self.toggle_processing_buttons(0)
        self.process_settings(self.sliderDisplay.value())

    def process_all(self):
        """Runs all the images in the currently opened tab that haven't been processed through the Defect Processor
        The button also functions as a Process Stop button which halts the running process
        """

        if 'Process All' in self.pushProcessAll.text():
            self.defect_counter = 0
            self.all_flag = True
            self.tab_index = self.widgetDisplay.currentIndex()

            # Change the Process All button into a Process Stop button
            self.pushProcessAll.setStyleSheet('QPushButton {color: #ff0000;}')
            self.pushProcessAll.setText('Process Stop')
            self.actionProcessAll.setText('Process Stop')

            # Remove the already processed defect images from the image list as dictated by the combined report keys
            report = self.load('%s/reports/combined_report.json' % self.build['BuildInfo']['Folder'])
            phases = ['coat', 'scan']
            layers = list()

            for layer in report.keys():
                if phases[self.tab_index] in report[layer]:
                    layers.append(int(layer))

            self.layer_numbers = sorted(list(set(self.display['LayerNumbers'][self.tab_index]) ^ set(layers)))
            self.process_settings(self.layer_numbers[self.defect_counter])

        elif 'Process Stop' in self.pushProcessAll.text():
            # On the next process loop, setting this to False will send the process to the finished method
            self.all_flag = False
            self.pushProcessAll.setStyleSheet('')
            self.pushProcessAll.setText('Process All')
            self.actionProcessAll.setText('Process All')
            self.toggle_processing_buttons(0)

    def process_settings(self, layer):
        """Setup and sends the image name to be processed to the Defect Processor module"""

        self.processing_flag = True

        # Grab some pertinent information (for clearer code purposes)
        phase = self.display['FolderNames'][self.tab_index][:-1].lower()

        # Vary the status message to display depending on which button was pressed
        if self.all_flag:
            self.toggle_processing_buttons(2)
            self.defect_counter += 1
            self.update_status('Running %s layer %s through the Defect Detector...' % (phase, str(layer).zfill(4)))
        else:
            self.update_status('Running displayed %s image through the Defect Detector...' % phase)

        # Send the image name and any other required values to the defect processor
        worker = qt_thread.Worker(image_processing.DefectProcessor().run_processor,
                                  self.display['ImageList'][self.tab_index][layer - 1], layer, phase,
                                  self.build['BuildInfo']['Folder'], self.build['SliceConverter']['Colours'],
                                  self.build['ROI'])
        worker.signals.status.connect(self.update_status)
        worker.signals.progress.connect(self.update_progress)
        worker.signals.finished.connect(self.process_finished)
        self.threadpool.start(worker)

    def process_finished(self):
        """When the Processor has finished. determine if it needs to be run again for consecutive images
        Otherwise the Main Window is set to its processing finished state"""

        self.processing_flag = False
        self.update_folders(True)

        if self.all_flag and not self.defect_counter == len(self.layer_numbers):
            self.process_settings(self.layer_numbers[self.defect_counter])
        else:
            self.all_flag = False
            self.pushProcessAll.setStyleSheet('')
            self.pushProcessAll.setText('Process All')
            self.actionProcessAll.setText('Process All')
            self.update_status('Defect Detection finished successfully.', 10000)

    def toggle_processing_buttons(self, state):
        """Enables or disable the following buttons/actions when switching display tabs"""

        # State 0 is when the current tab of images CANNOT be processed, or when a Process Current is running
        # State 1 is when the current image CAN be processed
        # State 2 is when a Process All is running
        # Or when the current image CANNOT be processed but the tab still has other images that CAN
        self.pushProcessCurrent.setEnabled(state == 1)
        self.actionProcessCurrent.setEnabled(state == 1)
        self.pushProcessAll.setEnabled(state != 0)
        self.actionProcessAll.setEnabled(state != 0)

    # MENUBAR -> SETTINGS

    def camera_settings(self):
        """Opens the Camera Settings dialog window"""
        dialog_windows.CameraSettings(self).exec_()

    def build_settings(self):
        """Opens the Build Settings dialog window, which is essentially the New Build window but with changed elements
        Reloads the current build with any updated settings if updated
        """
        if dialog_windows.NewBuild(self, build_file='build.json', settings_flag=True).exec_():
            self.setup_build(True, False)

    def acquire_camera(self):
        """Checks for a valid attached camera and enables/disables the Run and Capture buttons accordingly"""

        self.update_status_camera('Acquiring...')

        state = bool(image_capture.ImageCapture().acquire_camera())
        self.actionSnapshot.setEnabled(state)
        self.pushSnapshot.setEnabled(state)
        self.actionStressTest.setEnabled(state)
        self.pushRun.setEnabled(state and bool(self.trigger_port))
        self.actionRun.setEnabled(state and bool(self.trigger_port))

        # Status Messages
        if state:
            self.update_status_camera('Found')
        else:
            self.update_status_camera('Not Found')

    def acquire_trigger(self):
        """Checks for a valid attached serial trigger and enables/disables the Run and Capture buttons accordingly"""

        self.update_status_trigger('Acquiring...')

        self.trigger_port = image_capture.ImageCapture().acquire_trigger()

        if bool(self.trigger_port):
            self.update_status_trigger(self.trigger_port)
            if 'Found' in self.labelCameraStatus.text():
                self.pushRun.setEnabled(True)
                self.actionRun.setEnabled(True)
        else:
            self.update_status_trigger('Not Found')
            self.pushRun.setEnabled(False)
            self.actionRun.setEnabled(False)

    def preferences(self):
        """Opens the Preferences dialog window and reloads the config.json file if any preferences were changed"""
        if dialog_windows.Preferences(self).exec_():
            self.config = self.load('config.json')

    # MENUBAR -> HELP

    def about(self):
        """Opens a QMessageBox displaying some pertinent 'About' information about the application"""

        QMessageBox.about(self, 'About Defect Monitor',
                          '<b>Defect Monitor</b><br><br>Version %s<br> Defect Monitor is a monitoring application '
                          'used to detect defects within the scan and coat layers of a 3D metal printing build.'
                          '<br><br>For assistance with the program or to report bugs/errors/crashes, please contact '
                          'Nicholas Lee at nicholascklee@gmail.com (preferred) or at 04 1209 8784.'% self.version)

        # Copyright message: '<br><br>Copyright (C) 2017 MCAM.'

    # LAYER SELECTION

    def set_layer(self):
        """Changes the layer slider's value which in turn executes the slider change method"""
        self.sliderDisplay.setValue(self.spinLayer.value())

    # IMAGE CAPTURE

    def snapshot(self):
        """Captures and saves a single snapshot image"""

        self.build = self.load('build.json')

        # Save the enabled state of the Run button so that the same state is applied after snapshot is done
        self.run_state = self.pushRun.isEnabled()

        # Disable certain UI elements to prevent concurrent processes
        self.toggle_snapshot_buttons(False)

        # Capture a single image using a thread by passing the function to the worker
        worker = qt_thread.Worker(image_capture.ImageCapture().capture_snapshot,
                                  self.build['ImageCapture']['Snapshot'],
                                          '%s/raw/snapshot' % self.build['BuildInfo']['Folder'],
                                  self.config['CameraSettings'])
        worker.signals.status_camera.connect(self.update_status_camera)
        worker.signals.name.connect(self.fix_image)
        worker.signals.result.connect(self.snapshot_finished)
        self.threadpool.start(worker)

    def snapshot_finished(self, flag):
        """Re-enable UI elements and only increment the snapshot layer if the capture was a success"""
        
        self.toggle_snapshot_buttons(True)

        if flag:
            # If the snapshot was a success, increment the snapshot layer counter and save the build file
            self.build['ImageCapture']['Snapshot'] += 1
            self.save(self.build, 'build.json')
        else:
            self.update_status('Snapshot failed to be captured. See command prompt for error message.', 3000)

    def toggle_snapshot_buttons(self, flag):
        """Enable or disable the following buttons/actions when a snapshot image is to be captured"""

        self.pushSnapshot.setEnabled(flag)
        self.actionSnapshot.setEnabled(flag)
        self.actionAcquireCamera.setEnabled(flag)
        self.actionAcquireTrigger.setEnabled(flag)
        self.actionStressTest.setEnabled(flag)
        self.pushRun.setEnabled(self.run_state)
        self.actionRun.setEnabled(self.run_state)

    def run_build(self):
        """Sets up values, states and timers to capture images indefinitely by polling the trigger device for a trigger
        Subsequently captures and saves an image if triggered and continues this loop until stopped
        The button also functions as a Pause/Resume button which halts the running process
        """

        if 'RUN' in self.pushRun.text():
            self.build = self.load('build.json')

            # Enable / disable certain UI elements to prevent concurrent processes
            self.toggle_run_buttons(False)
            self.update_status('Running build.')

            # Change the RUN button/action into a PAUSE/RESUME button/action
            self.pushRun.setStyleSheet('QPushButton {color: #ffaa00;}')
            self.pushRun.setText('PAUSE')
            self.actionRun.setText('Pause')

            # Check if the Resume From checkbox is checked and if so, set the current layer to the entered number
            # 0.5 is subtracted as it is assumed that the first image captured will be the previous layer's scan
            if self.checkResume.isChecked():
                self.spinStartingLayer.setEnabled(False)
                self.build['ImageCapture']['Layer'] = self.spinStartingLayer.value() - 0.5
                self.build['ImageCapture']['Phase'] = 1

                # Save the build to retain capture numbering
                self.save(self.build, 'build.json')

            # Open the COM port associated with the attached trigger device
            self.serial_trigger = serial.Serial(self.trigger_port, 9600, timeout=1)

            # Reset the elapsed time and idle time counters and initialize the display time to 0
            self.stopwatch_elapsed = 0
            self.stopwatch_idle = 0
            self.update_time()
            self.timeout_flag = True

            # Create a QTimer that will increment the two running timers
            self.timer_stopwatch = QTimer()

            # Connect the timeout of the QTimer to the corresponding function
            self.timer_stopwatch.timeout.connect(self.update_time)

            # Start the QTimer which will timeout and execute the above connected slot method every given milliseconds
            self.timer_stopwatch.start(1000)

            # Set a flag used for process states and for the faux trigger
            self.run_flag = True

            # Start the capture run process
            self.run_loop('')

        elif 'PAUSE' in self.pushRun.text():
            # Pause the build
            self.pushRun.setStyleSheet('QPushButton {color: $00aa00;}')
            self.pushRun.setText('RESUME')
            self.actionRun.setText('Resume')
            self.run_flag = False
            self.timer_stopwatch.stop()
            self.update_status_camera('Paused')
            self.update_status_trigger('Paused')
            self.update_status('Current build paused.')
            self.actionFauxTrigger.setEnabled(False)

        elif 'RESUME' in self.pushRun.text():
            # Resume the build
            self.pushRun.setStyleSheet('QPushButton {color: #ffaa00;}')
            self.pushRun.setText('PAUSE')
            self.actionRun.setText('Pause')
            self.run_flag = True
            self.timer_stopwatch.start(1000)
            self.update_status('Current build resumed.')
            self.actionFauxTrigger.setEnabled(True)
            self.run_exit()

    def run_loop(self, result):
        """Because reading from the serial trigger takes a little bit of ti me, it temporarily freezes the main UI
        As such, the serial read is turned into a QRunnable function that is passed to a worker using the QThreadPool
        The current method works as a sort of recursive loop, where the result of the trigger poll is checked
        If a trigger is detected, the corresponding image capture function is executed as a worker to the QThreadPool
        Otherwise, another trigger polling worker is started and the loop keeps repeating
        The loop is broken if the Pause button is pressed or the build is stopped outright
        """

        # Check if the build is still 'running'
        if self.run_flag:
            if 'TRIG' in result:
                # Disable all the image capture buttons
                self.toggle_capture_buttons(False)

                # Determine the name of the current phase (coat or scan) and the raw folder to save images to
                phase = self.display['FolderNames'][self.build['ImageCapture']['Phase']][:-1].lower()
                folder = '%s/raw' % self.build['BuildInfo']['Folder']

                # Capture an image
                worker = qt_thread.Worker(image_capture.ImageCapture().capture_run, self.build['ImageCapture']['Layer'],
                                          phase, folder, self.config['CameraSettings'])
                worker.signals.status_camera.connect(self.update_status_camera)
                worker.signals.status_trigger.connect(self.update_status_trigger)
                worker.signals.name.connect(self.fix_image)
                worker.signals.result.connect(self.run_exit)
                self.threadpool.start(worker)
            else:
                self.update_status_camera('Waiting...')
                self.update_status_trigger('Waiting...')
                worker = qt_thread.Worker(self.poll_trigger)
                worker.signals.result.connect(self.run_loop)
                self.threadpool.start(worker)

    def poll_trigger(self):
        """Function that will be passed to the QThreadPool to be executed, put into a thread as it takes a bit of time
        Simply checks the serial trigger for a TRIG output"""
        return str(self.serial_trigger.readline())

    def faux_trigger(self):
        """Sends a TRIG result to the run loop to capture an image and flips the run flag so the internal loop stops"""
        self.run_loop('TRIG')
        self.run_flag = False

    def run_exit(self, flag):
        """Cleanup method after an image capture regardless if it was successful or not (skips image if not)"""

        # Reset the serial trigger and the idle stopwatch
        self.serial_trigger.reset_input_buffer()
        self.stopwatch_idle = 0

        # Re-enable all the image capture buttons
        self.toggle_capture_buttons(True)

        # Increment the run capture layer and toggle the phase
        self.build['ImageCapture']['Layer'] += 0.5
        self.build['ImageCapture']['Phase'] ^= 1

        # Save the build to retain capture numbering
        self.save(self.build, 'build.json')

        # If the image failed to be captured, simply display an error message and skip the layer's image
        if not flag:
            self.update_status('Image failed to be captured. See command prompt for error message.', 3000)

        # Check if the max layers has been set (by drawing the contours)
        if self.build['SliceConverter']['MaxLayers']:
            # Check if the current layer number exceeds the maximum number of layers
            if self.build['ImageCapture']['Layer'] > self.build['SliceConverter']['MaxLayers']:
                # Send a 'finished' notification to the stored email address
                worker = qt_thread.Worker(notifications.Notifications().send, self.build['BuildInfo']['EmailAddress'],
                                          'finish', info=self.build['BuildInfo']['Name'])
                self.threadpool.start(worker)

                # Display a finish popup as well
                finish_confirmation = QMessageBox(self)
                finish_confirmation.setWindowTitle('Build Finished')
                finish_confirmation.setIcon(QMessageBox.Information)
                finish_confirmation.setText('The build\'s most recent layer number has exceeded the max layer number '
                                            'as determined by the build\'s entered slice files. As such, it is assumed '
                                            'that the current build has finished.\nRegardless, the program will still '
                                            'continue to capture additional images should the trigger continue to be '
                                            'triggered.')
                finish_confirmation.show()

        # Go back into the trigger polling loop after resetting the run flag
        self.run_flag = True
        self.run_loop('')

    def stop_build(self):
        """Stops the running build and resets the window buttons back"""

        self.run_flag = False

        # Enable / disable certain UI elements
        # Disabling the Pause button stops the trigger polling loop
        self.toggle_run_buttons(True)
        self.update_status('Build stopped.', 3000)
        self.update_status_camera('Found')
        self.update_status_trigger(self.trigger_port)

        # Reset the Pause/Resume button back to its default RUN state (including the text colour)
        self.pushRun.setStyleSheet('QPushButton {color: #008080;}')
        self.pushRun.setText('RUN')
        self.actionRun.setText('Run')

        # Stop the stopwatch timer and close the serial port
        self.timer_stopwatch.stop()
        self.serial_trigger.close()

    def toggle_run_buttons(self, flag):
        """Enable or disable the following buttons/actions when a build has been started or stopped"""

        self.actionNew.setEnabled(flag)
        self.actionOpen.setEnabled(flag)
        self.menuRecentBuilds.setEnabled(flag)
        self.actionCameraSettings.setEnabled(flag)
        self.pushCameraCalibration.setEnabled(flag)
        self.actionCameraCalibration.setEnabled(flag)
        self.pushSliceConverter.setEnabled(flag)
        self.actionSliceConverter.setEnabled(flag)
        self.pushImageConverter.setEnabled(flag)
        self.actionImageConverter.setEnabled(flag)
        self.actionBuildSettings.setEnabled(flag)
        self.actionPreferences.setEnabled(flag)
        self.checkResume.setEnabled(flag)
        self.actionAcquireCamera.setEnabled(flag)
        self.actionAcquireTrigger.setEnabled(flag)
        self.actionStressTest.setEnabled(flag)
        self.pushSnapshot.setEnabled(flag)
        self.actionSnapshot.setEnabled(flag)
        self.actionFauxTrigger.setEnabled(not flag)
        self.pushStop.setEnabled(not flag)

    def toggle_capture_buttons(self, flag):
        """Enable or disable the following buttons/actions when an image is to be captured during a build run"""

        self.pushRun.setEnabled(flag)
        self.actionRun.setEnabled(flag)
        self.actionFauxTrigger.setEnabled(flag)
        self.pushStop.setEnabled(flag)

    # IMAGE PROCESSING

    def fix_image(self, image_name):
        """Use the received image name to load the image in order to fix it"""

        # Fixed image name is stored for the exit function and for the Idle Notification message
        self.image_name = image_name.replace('R_', 'F_').replace('raw', 'fixed')
        self.update_status('Applying image fixes...')

        worker = qt_thread.Worker(image_processing.ImageFix().fix_image, image_name,
                                  self.config['ImageCorrection'])
        worker.signals.result.connect(self.fix_image_finished)
        self.threadpool.start(worker)

    def fix_image_finished(self, image_name):
        """Cleanup method after the image has been fixed and sends the image to the defect processor if eligible"""

        self.update_status('Image fix successfully applied.', 2000)

        # Update the image dictionaries and layer ranges
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

        # Delete the raw image if the setting (within Preferences) is unchecked
        if not self.config['KeepRaw']:
            os.remove(image_name)

        # Process only the coat or scan image for defects, the image being the one the above method set focus to
        if index < 2:
            self.update_status('Image fix successfully applied. Currently detecting defects...')
            self.process_current()

    # DISPLAY

    def update_display(self):
        """Updates the Main Window's display to show an image on the currently displayed tab as per toggles
        Also responsible for enabling or disabling display checkbox elements
        """

        # Grab the names of certain elements (for clearer code purposes)
        index = self.widgetDisplay.currentIndex()
        label = self.display['LabelNames'][index]
        stack = self.display['StackNames'][index]
        image_list = self.display['ImageList'][index]
        image_folder = self.build['BuildInfo']['Folder']
        value = self.sliderDisplay.value()
        layer = str(value).zfill(4)
        phase = self.display['FolderNames'][index][:-1].lower()
        roi = self.build['ROI']

        # Set a default disabled state for the Defect Processor buttons
        self.toggle_processing_buttons(0)

        # Check if the image folder has an actual image to display
        if list(filter(bool, image_list)):
            # Change the stacked widget to the one with the image viewer
            stack.setCurrentIndex(1)

            # Grab the filename of the main fixed image from the fixed image list
            filename = image_list[value - 1]

            # Initially assume an image is being displayed and enable both display groupboxes
            self.groupDisplayOptions.setEnabled(True)

            # Check if the image exists in the first place (in case it gets deleted between folder checks)
            if os.path.isfile(filename):
                image = cv2.imread(filename)

                # Enable the Defect Processor toolbar and actions if on coat or scan tab
                if not self.processing_flag and index < 2:
                    self.toggle_processing_buttons(1)
            else:
                # Set the stack tab to the information label and display the missing layer information
                label.setText('%s Layer %s Image does not exist.' % (phase.capitalize(), layer))
                stack.setCurrentIndex(0)

                # Set all the UI elements accordingly
                self.toggle_display_control(1)
                self.groupDisplayOptions.setEnabled(False)
                self.groupOverlayDefects.setEnabled(False)

                # Enable the Defect Processor toolbar and actions
                if not self.processing_flag and index < 2:
                    self.toggle_processing_buttons(2)
                return

            # Check if the Part Contours, Part Names and Gridlines images exist, otherwise disable their checkboxes
            # Part Contours only toggleable on the Coat and Scan tabs
            if index < 2:
                if os.path.isfile(self.display['ImageList'][2][value - 1]):
                    self.checkContours.setEnabled(True)
                else:
                    self.checkContours.setEnabled(False)
                    self.checkContours.setChecked(False)
            else:
                self.checkContours.setEnabled(False)
                self.checkContours.setChecked(False)

            # Part Names only toggleable on the Coat, Scan and Part Contour tabs
            if os.path.isfile('%s/part_names.png' % image_folder) and index < 3:
                self.checkNames.setEnabled(True)
            else:
                self.checkNames.setEnabled(False)
                self.checkNames.setChecked(False)

            if os.path.isfile('gridlines.png'):
                self.checkGridlines.setEnabled(True)
            else:
                self.checkGridlines.setEnabled(False)
                self.checkGridlines.setChecked(False)

            # Region of Interest toggleable anywhere
            if roi[0]:
                self.checkROI.setEnabled(True)
            else:
                self.checkROI.setEnabled(False)
                self.checkROI.setChecked(False)

            # Check if the following defect images exist, and enable or disable the corresponding checkboxes
            # Subsequently overlay the defects in the order they were selected
            # Only do this for the coat and scan images, otherwise uncheck all checked defects and disable the groupbox
            if index < 2:
                base = os.path.basename(filename)
                defects = dict()
                defects['Streaks'] = '%s/defects/%s/streaks/%s' % (image_folder, phase, base.replace('F_', 'BS_'))
                defects['Chatter'] = '%s/defects/%s/chatter/%s' % (image_folder, phase, base.replace('F_', 'BC_'))
                defects['Patches'] = '%s/defects/%s/patches/%s' % (image_folder, phase, base.replace('F_', 'SP_'))
                defects['Outliers'] = '%s/defects/%s/outliers/%s' % (image_folder, phase, base.replace('F_', 'CO_'))
                defects['Pattern'] = '%s/defects/%s/pattern/%s' % (image_folder, phase, base.replace('F_', 'OC_'))

                # Because coats and scans have different combinations of defects, each tab has its own checkbox config
                self.checkPatch.setEnabled(index == 0)
                self.checkOutlier.setEnabled(index == 0)
                self.checkPattern.setEnabled(index == 1)

                # Overlay the defects in the order they were selected
                for defect in self.defect_checkbox:
                    # Check if the image exists in the first place, otherwise display an error message box
                    if os.path.isfile(defects[defect]):
                        # Directly replace the colours of the original image with the defect colour
                        mask = cv2.inRange(cv2.imread(defects[defect]), self.defect_colours[defect],
                                           self.defect_colours[defect])
                        image[np.nonzero(mask)] = self.defect_colours[defect]
                    else:
                        missing_file_error = QMessageBox(self)
                        missing_file_error.setWindowTitle('Error')
                        missing_file_error.setIcon(QMessageBox.Critical)
                        missing_file_error.setText('The %s defect image could not be found.' % defect.lower())
                        missing_file_error.exec_()

                        # Uncheck the checkbox in question
                        self.display['CheckboxNames'][self.display['DefectNames'].index(defect)].setChecked(False)
            else:
                # Disable and uncheck all the Overlay Defects checkboxes
                for checkbox in self.groupOverlayDefects.findChildren(QCheckBox):
                    checkbox.blockSignals(True)
                    checkbox.setChecked(False)
                    checkbox.blockSignals(False)

                self.defect_checkbox = list()
                self.groupOverlayDefects.setEnabled(False)

            # The following conditionals are to check whether to overlay the corresponding images on the current image
            # Overlay the part contours
            if self.checkContours.isChecked():
                # Load the overlay image into memory
                contours = cv2.imread(self.display['ImageList'][2][value - 1])

                # Resize the overlay image if the resolution doesn't match the displayed image
                if contours.shape[:2] != image.shape[:2]:
                    contours = cv2.resize(contours, image.shape[:2][::-1], interpolation=cv2.INTER_CUBIC)

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

            # Overlay the gridlines
            if self.checkGridlines.isChecked():
                image_gridlines = cv2.imread('gridlines.png')

                if image_gridlines.shape[:2] != image.shape[:2]:
                    image_gridlines = cv2.resize(image_gridlines, image.shape[:2][::-1], interpolation=cv2.INTER_CUBIC)

                image = cv2.add(image, image_gridlines)

            # Overlay the ROI box
            if self.checkROI.isChecked():
                cv2.rectangle(image, (roi[1], roi[2]), (roi[3], roi[4]), (255, 255, 255), 5)

            # Applies CLAHE to the display image
            if self.checkEqualization.isChecked():
                image = image_processing.ImageFix.clahe(image)

            # Convert from OpenCV's BGR format to RGB so that colours are displayed correctly
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Display the image on the current GraphicsView
            self.display['GraphicsNames'][self.widgetDisplay.currentIndex()].set_image(image)

            # Save the current (modified) image so that it can be exported if need be
            self.display['DisplayImage'][self.widgetDisplay.currentIndex()] = image

            # Enable all display control elements
            self.toggle_display_control(2)
        else:
            # If the entire folder is empty, change the stacked widget to the one with the information label
            label.setText('%s folder empty. Nothing to display.' % phase.capitalize())
            stack.setCurrentIndex(0)

            # Disable all display control elements and checkboxes
            self.toggle_display_control(0)
            self.groupDisplayOptions.setEnabled(False)
            self.groupOverlayDefects.setEnabled(False)

    def toggle_display_control(self, state):
        """Enables or disable the following buttons/actions when switching display tabs"""

        # State 0 - No images in folder
        # State 1 - Image not found, have images in folder
        # State 2 - Image found
        self.actionZoomIn.setEnabled(state == 2)
        self.actionZoomOut.setEnabled(state == 2)
        self.actionExportImage.setEnabled(state == 2)
        self.frameSlider.setEnabled(state > 0)
        self.pushGo.setEnabled(state > 0)
        self.pushDisplayUpSeek.setEnabled(state == 1)
        self.pushDisplayDownSeek.setEnabled(state == 1)

        if state < 2:
            self.actionZoomIn.setChecked(False)

    def toggle_all(self):
        """Checks or unchecks all the available (enabled) defect checkboxes"""

        self.defect_checkbox = list()

        # Signals for each checkbox is blocked while checking so that the below method doesn't get called
        for index, checkbox in enumerate(self.display['CheckboxNames']):
            checkbox.blockSignals(True)
            if checkbox.isEnabled():
                checkbox.setChecked(self.checkToggleAll.isChecked())
                if self.checkToggleAll.isChecked():
                    self.defect_checkbox.append(self.display['DefectNames'][index])
            checkbox.blockSignals(False)

        self.update_display()

    def toggle_defect(self):
        """Appends or removes the toggled defect from the checkbox list and subsequently updates the display"""

        # Grab the index of the checkbox that sent this function call to append or remove the corresponding
        # Use it to append or remove the corresponding defect name from the defect list
        if self.sender().isChecked():
            self.defect_checkbox.append(self.display['DefectNames'][self.display['CheckboxNames'].index(self.sender())])
        else:
            self.defect_checkbox.remove(self.display['DefectNames'][self.display['CheckboxNames'].index(self.sender())])

        self.update_display()

    def update_table(self):
        """Updates the Defect Data table with the current layer's defect data if available"""

        # Load the combined defect report json file
        report = self.load('%s/reports/combined_report.json' % self.build['BuildInfo']['Folder'])
        index = self.widgetDisplay.currentIndex()
        layer = str(self.sliderDisplay.value()).zfill(4)
        colours = list()

        # Process to fill the table is very similar to the display_report method within the DefectReports class
        # Therefore this section will not be commented at all
        if report and index < 2:

            self.groupOverlayDefects.setEnabled(True)

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
                            colours.append(QColor(255, 255, 0))
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
                            colours.append(QColor(255, 255, 0))
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
        Or if the current tab isn't either the coat or scan tabs
        """

        for row in range(6):
            self.tableDefects.setItem(row, 0, QTableWidgetItem('0'))
            self.tableDefects.item(row, 0).setBackground(QColor(255, 255, 0))

        # Disable the Overlay Defects groupBox as an empty table would imply no defects to display
        self.checkToggleAll.setChecked(False)
        self.groupOverlayDefects.setEnabled(False)

    def context_menu_display(self, position):
        """Opens a context menu at the right-clicked position of any of the display labels"""

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
            name = self.display['ImageList'][self.widgetDisplay.currentIndex()][self.sliderDisplay.value() - 1]

            if action == action_show_image:
                # Need to turn the forward slashes into backslash due to windows explorer only working with backslashes
                subprocess.Popen(r"""explorer /select, %s""" % name.replace('/', '\\'))
            elif action == action_open_image:
                os.startfile(name)
            elif action == action_export:
                self.export_image()

    # MISCELLANEOUS UI ELEMENT FUNCTIONALITY

    def tab_change(self, index):
        """When the display tab changes, enable/disable buttons and change layer values to the corresponding phase"""

        # Stop the change in slider value from changing the picture as well, causing conflicting images
        self.sliderDisplay.blockSignals(True)

        if self.display_flag:
            # Uncheck all the defect checkboxes
            self.checkToggleAll.setChecked(False)

            # Update the max layers
            self.update_layer_values()

            # Set the slider's value to the saved layer value of the current tab and reset the image zoom
            self.sliderDisplay.setValue(self.display['CurrentLayer'][index])
            self.display['GraphicsNames'][index].reset_image()

            # Update the defect data table and the image on the graphics display with the new image
            self.update_table()
            self.update_display()

        self.sliderDisplay.blockSignals(False)

    def tab_focus(self, index, layer, defect_flag=False, defect=0):
        """Changes the tab focus to the received index's tab and sets the slider value to the received value
        Used for when an image has been captured and focus is to be given to the new image
        Also can be used for when an image has just finished processing for defects
        """

        # Double check if the received value is within the layer's range in the first place
        if layer > self.display['MaxLayers'] and index < 3:
            self.update_status('Layer %s outside of the available layer range.' % str(layer).zfill(4), 3000)
        else:
            self.widgetDisplay.setCurrentIndex(index)
            self.sliderDisplay.setValue(layer)

            if defect_flag and self.groupOverlayDefects.isEnabled():
                self.checkToggleAll.setChecked(defect < 0)
                self.toggle_all()

                if self.display['CheckboxNames'][defect].isEnabled():
                    self.display['CheckboxNames'][defect].setChecked(True)

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

        # Update layer ranges in the corresponding UI elements
        self.update_layer_values()

        # Update the defect data table and the image on the graphics display with the new image
        self.update_table()
        self.update_display()

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

    def update_folders(self, update_flag=True):
        """Updates the display dictionary with the updated list of images in all four image folders"""

        # Iterate through all but the last folder in the list (the snapshot folder) and create a list of layer numbers
        for index, folder_name in enumerate(self.display['ImageFolder'][:-1]):
            # Reset the list of layer numbers in the display dictionary
            self.display['LayerNumbers'][index][:] = list()

            # Get a list of numbers of the supposed layer images in the folder (except the snapshot folder)
            for filename in os.listdir(folder_name):
                # Only grab the .png images and images with coatF, scanF or contour in their name
                # Ignore any other files and incorrectly named images in the folder
                if '.png' in filename:
                    if 'coatF' in filename or 'scanF' in filename or 'contour' in filename:
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

        # Create a list of image names for the snapshot folder as well
        self.display['ImageList'][3][:] = list()
        for filename in os.listdir(self.display['ImageFolder'][3]):
            if '.png' in filename:
                self.display['ImageList'][3].append('%s/%s' % (self.display['ImageFolder'][3], filename))

        # Update the layer ranges in the corresponding UI elements
        self.update_layer_values()

        # If this method was called just to update the lists and not the displays
        if update_flag:
            self.update_table()
            self.update_display()

    def update_layer_values(self):
        """Updates the layer spinbox's maximum acceptable range, tooltip, and the slider's maximum range"""

        # The Image Capture tab has different ranges and values
        if self.widgetDisplay.currentIndex() < 3:
            max_layers = self.display['MaxLayers']
        else:
            max_layers = len(self.display['ImageList'][3])

        # Addresses the issue of the empty snapshot image list causing the slider minimum to be set to 0
        if max_layers == 0:
            max_layers += 1

        # Layer Number
        self.spinLayer.setMaximum(max_layers)
        self.spinLayer.setToolTip('1 - %s' % max_layers)
        self.labelLayerNumber.setText('%s / %s' %
                                      (str(self.display['CurrentLayer'][self.widgetDisplay.currentIndex()]).zfill(4),
                                       str(max_layers).zfill(4)))

        # Display Slider
        self.sliderDisplay.setMaximum(max_layers)
        self.sliderDisplay.setToolTip(str(self.display['CurrentLayer'][self.widgetDisplay.currentIndex()]))
        self.sliderDisplay.setPageStep(math.ceil(max_layers // 50))
        self.sliderDisplay.setTickInterval(math.ceil(max_layers // 50))

    def update_time(self):
        """Updates the timers at the bottom right of the Main Window with an incremented formatted timestamp
        Also checks that the stopwatch idle hasn't exceeded a predefined idle time limit and if so, send a notification
        """

        self.stopwatch_elapsed += 1
        self.stopwatch_idle += 1

        # If the idle time exceeds the stored idle timeout, display an error popup and send a notification
        if self.stopwatch_idle > self.config['IdleTimeout'] and self.timeout_flag:
            # Create an information list to be used to construct the notification email message
            info = [self.build['BuildInfo']['Name'], self.config['IdleTimeout'],
                    self.build['ImageCapture']['Phase'], self.build['ImageCapture']['Layer']]

            # Send the notification email
            worker = qt_thread.Worker(notifications.Notifications().send, self.build['BuildInfo']['EmailAddress'],
                                      'idle', self.image_name, info)
            self.threadpool.start(worker)

            # Stop this conditional from being accessed after being accessed once
            self.timeout_flag = False

            idle_error = QMessageBox(self)
            idle_error.setWindowTitle('Error')
            idle_error.setIcon(QMessageBox.Critical)
            idle_error.setText('An image has not been taken in the last %s minutes.\nThe machine might have '
                               'malfunctioned, and error might have occured or the user has forgotten to stop the '
                               'image taking process. A notification email has been sent to %s at %s.\nThe image '
                               'capturing process will continue indefinitely regardless.' %
                               (self.config['IdleTimeout'], self.build['BuildInfo']['Username'],
                                self.build['BuildInfo']['EmailAddress']))
            idle_error.show()

        self.labelElapsedTime.setText(self.format_time(self.stopwatch_elapsed))
        self.labelIdleTime.setText(self.format_time(self.stopwatch_idle))

    @staticmethod
    def format_time(stopwatch):
        """Formats the stopwatch counter into proper string hour:minute:second format"""

        seconds = str(stopwatch % 60).zfill(2)
        minutes = str(stopwatch % 3600 // 60).zfill(2)
        hours = str(stopwatch // 3600).zfill(2)
        return '%s:%s:%s' % (hours, minutes, seconds)

    def update_status_camera(self, status):
        """Updates the camera status bar with the received string argument"""
        self.labelCameraStatus.setText(status)

    def update_status_trigger(self, status):
        """Updates the trigger status bar with the received string argument"""
        self.labelTriggerStatus.setText(status)

    def update_status(self, string, duration=0):
        """Updates the default status bar at the bottom of the Main Window with the received string argument"""
        self.statusBar.showMessage(string, duration)

    def update_progress(self, percentage):
        """Updates the progress bar at the bottom of the Main Window with the received percentage argument"""
        self.progressBar.setValue(int(percentage))

    @staticmethod
    def save(data, filename):
        """Saves the received data to the received filename"""
        with open(filename, 'w+') as file:
            json.dump(data, file, indent=4, sort_keys=True)

    @staticmethod
    def load(filename):
        """Loads the received filename and return it to the caller method"""
        with open(filename) as file:
            data = json.load(file)
        return data

    # CLEANUP

    def closeEvent(self, event):
        """If a process is in progress, display an error message and prevent the user from exiting the program
        Otherwise save the current build settings before closing the application if a build has been created/opened
        """

        if self.run_flag or self.processing_flag:
            run_error = QMessageBox(self)
            run_error.setWindowTitle('Error')
            run_error.setIcon(QMessageBox.Critical)
            run_error.setText('Build or Defect Processor in progress.\n'
                              'Please stop or wait for the active process to finish before exiting.')
            run_error.exec_()
            event.ignore()
        else:
            if self.display_flag:
                self.save_build()
            self.window_settings.setValue('Defect Monitor Geometry', self.saveGeometry())


if __name__ == '__main__':
    application = QApplication(sys.argv)
    interface = MainWindow()
    interface.show()
    sys.exit(application.exec_())
