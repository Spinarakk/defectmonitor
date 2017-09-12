# Import libraries and modules
import os
import sys
import subprocess
import json
import cv2
import serial

# Import PyQt modules
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

uic.compileUiDir('gui')
# # Import related modules
import dialog_windows
import image_capture
import image_processing
import defect_analysis
import slice_converter
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

        # Load default configuration settings from the hidden config_default.json file
        with open('config_default.json') as config:
            self.config = json.load(config)

        # Get the current working directory and save it to the config.json file so later methods can grab it
        # Additionally, create a default builds folder (if it doesn't exist) using the cwd to store images
        self.config['WorkingDirectory'] = os.getcwd().replace('\\', '/')
        self.config['BuildInfo']['Folder'] = os.path.dirname(self.config['WorkingDirectory']) + '/Builds'
        if not os.path.isdir(self.config['BuildInfo']['Folder']):
            os.makedirs(self.config['BuildInfo']['Folder'])

        # Save the default config to the current working config.json file
        with open('config.json', 'w+') as config:
            json.dump(self.config, config, indent=4, sort_keys=True)

        # Setup event listeners for all the relevant UI components, and connect them to specific functions
        # Menubar -> File
        self.actionNew.triggered.connect(self.new_build)
        self.actionOpen.triggered.connect(self.open_build)
        self.actionClearMenu.triggered.connect(self.clear_menu)
        self.actionSave.triggered.connect(self.save_build)
        self.actionSaveAs.triggered.connect(self.save_as_build)
        self.actionExportImage.triggered.connect(self.export_image)
        self.actionClose.triggered.connect(self.close_build)
        self.actionQuit.triggered.connect(self.closeEvent)

        # Menubar -> View
        self.actionZoomIn.triggered.connect(self.zoom_in)
        self.actionZoomOut.triggered.connect(self.zoom_out)

        # Menubar -> Tools
        self.actionCameraCalibration.triggered.connect(self.camera_calibration)
        self.actionOverlayAdjustment.triggered.connect(self.overlay_adjustment)
        self.actionSliceConverter.triggered.connect(self.slice_converter)
        self.actionImageConverter.triggered.connect(self.image_converter)

        # Menubar -> Settings
        self.actionCameraSettings.triggered.connect(self.camera_settings)
        self.actionBuildSettings.triggered.connect(self.build_settings)

        # Menubar -> Help
        self.actionViewHelp.triggered.connect(self.view_help)
        self.actionAbout.triggered.connect(self.view_about)

        # Display Options Group Box
        self.radioOriginal.toggled.connect(self.update_display)
        self.radioCLAHE.toggled.connect(self.update_display)
        self.radioDefects.toggled.connect(self.update_display)
        self.checkOverlay.toggled.connect(self.toggle_overlay)

        # Assorted Tools Group Box
        self.pushCameraCalibration.clicked.connect(self.camera_calibration)
        self.pushOverlayAdjustment.clicked.connect(self.overlay_adjustment)
        self.pushSliceConverter.clicked.connect(self.slice_converter)
        self.pushImageConverter.clicked.connect(self.image_converter)

        # Layer Selection
        self.pushGo.clicked.connect(self.set_layer)

        # Image Capture
        self.pushAcquireCT.clicked.connect(self.acquire_ct)
        self.pushCapture.clicked.connect(self.capture_single)
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
        self.pushDisplayDown.clicked.connect(self.slider_down)

        # Flags for various conditions
        self.display_flag = False

        # Instantiate any instances that cannot be run simultaneously
        self.FM_instance = None

        # Instantiate dialog variables that cannot have multiple windows for existence validation purposes
        self.CC_dialog = None
        self.OA_dialog = None
        self.SC_dialog = None
        self.CS_dialog = None

        # Initiate an empty config file name to be used for saving purposes
        self.config_name = None

        # Create a context menu that will appear when the user right-clicks on any of the display labels
        self.menu_display = QMenu()

        # Because each tab on the widgetDisplay has its own set of associated images, display labels and sliders
        # And because they all do essentially the same functions
        # Easier to store each of these in a dictionary under a specific key to call on one of the four sets
        # The current tab's index will be used to grab the corresponding image, list or name
        self.display = {'Image': [0, 0, 0, 0], 'ImageList': [[], [], [], []], 'LayerRange': [1, 1, 1, 1],
                        'FolderNames': ['Coat/', 'Scan/', 'Contour/', 'Single/'], 'CurrentLayer': [1, 1, 1, 1],
                        'StackNames': [self.stackedCE, self.stackedSE, self.stackedPC, self.stackedIC],
                        'LabelNames': [self.labelCE, self.labelSE, self.labelPC, self.labelIC],
                        'GraphicsNames': [self.graphicsCE, self.graphicsSE, self.graphicsPC, self.graphicsIC],
                        'DisplayImage': [0, 0, 0, 0]}

        # Create a threadpool which contains an amount of threads that can be used to simultaneously run functions
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
        Allows the user to select a previous build's configuration settings
        Subsequently opens the New Build Dialog Window with all the boxes filled in, allowing the user to make changes
        """

        # Acquire the name of the config file to be opened and read
        file_name, _ = QFileDialog.getOpenFileName(self, 'Browse...', '', 'JSON File (*.json)')

        # Check if a file has been selected as QFileDialog returns an empty string if cancel was pressed
        if file_name:
            # Open the config file and overwrite the contents of the default config file with the new config file
            with open(file_name) as config:
                self.config = json.load(config)
            with open('config.json', 'w+') as config:
                json.dump(self.config, config, indent=4, sort_keys=True)

            self.config_name = file_name

            OB_dialog = dialog_windows.NewBuild(self, open_flag=True)

            if OB_dialog.exec_():
                self.setup_build()

    def setup_build(self):
        """Sets up the widgetDisplay and any background processes for the current build"""

        with open('config.json') as config:
            self.config = json.load(config)

        # Store config settings as respective variables and update appropriate UI elements
        self.transform = self.config['ImageCorrection']['TransformParameters']
        self.setWindowTitle('Defect Monitor - Build ' + self.config['BuildInfo']['Name'])

        # Enable certain UI elements
        self.actionSave.setEnabled(True)
        self.actionSaveAs.setEnabled(True)
        self.pushAcquireCT.setEnabled(True)

        # Store the names of the four folders to be monitored in the display dictionary
        self.display['ImageFolder'] = ['%s/processed/coat' % self.config['ImageCapture']['Folder'],
                                       '%s/processed/scan' % self.config['ImageCapture']['Folder'],
                                       '%s/contours' % self.config['ImageCapture']['Folder'],
                                       '%s/processed/single' % self.config['ImageCapture']['Folder']]

        # Instantiate a QFileSystemWatcher that will monitor the given folders and emit a signal if changes are detected
        self.folder_monitor = QFileSystemWatcher()
        self.folder_monitor.addPaths(self.display['ImageFolder'])
        self.folder_monitor.directoryChanged.connect(self.folder_change)

        # Start the display image viewer to start showing images
        self.start_display()

        # Check and acquire an attached camera and trigger
        self.acquire_ct()

        # Converts and draws the contours
        if self.config['BuildInfo']['Convert']:
            worker = qt_multithreading.Worker(slice_converter.SliceConverter().convert)
            worker.signals.status.connect(self.update_status)
            if not self.checkSuppress.isChecked():
                worker.signals.progress.connect(self.update_progress)
            worker.signals.finished.connect(self.setup_build_finished)
            self.threadpool.start(worker)
        else:
            self.setup_build_finished()

    def setup_build_finished(self):
        self.update_status('Build %s setup complete.' % self.config['BuildInfo']['Name'])

    def clear_menu(self):
        pass

    def save_build(self):
        """Saves the current build to the config.json file when File -> Save is clicked
        Executes save_as_build instead if this is the first time the build is being saved
        """

        if self.config_name:
            # Save the config file as the given name in the given location
            with open(self.config_name, 'w+') as config:
                json.dump(self.config, config, indent=4, sort_keys=True)
            self.update_status('Build saved to %s.' % os.path.basename(self.config_name), 5000)
        else:
            self.save_as_build()

    def save_as_build(self):
        """Opens a File Dialog when File -> Save As... is clicked
        Allows the user to save the current build's config.json file to whatever location the user specifies
        """

        config_name, _ = QFileDialog.getSaveFileName(self, 'Save Build As', '', 'JSON File (*.json)')

        # Checking if user has chosen to save the build or clicked cancel
        if config_name:
            self.config_name = config_name
            self.save_build()

    def export_image(self):
        """Opens a FileDialog Window when File > Export Image... is clicked
        Allows the user to save the currently displayed image to whatever location the user specifies as a .png
        """

        # Open a folder select dialog, allowing the user to choose a location and input a name
        image_name, _ = QFileDialog.getSaveFileName(self, 'Export Image As', '', 'Image (*.png)')

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

    def close_build(self):
        """Closes the current build when File -> Close is clicked or when a new build is created/opened"""

        # Remove the paths from the QFileSystemWatcher
        self.folder_monitor.removePaths(self.display['ImageFolder'])

        for index in range(4):
            self.display['StackNames'][index].setCurrentIndex(0)
            self.display['LabelNames'][index].setText('Create or Open a Build to View Images')

        #TODO

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

    # MENUBAR -> TOOLS

    def camera_calibration(self):
        """Opens a Modeless Dialog Window when the Camera Calibration button is clicked
        Or when Tools -> Camera -> Calibration is clicked
        Allows the user to select a folder of chessboard images to calculate the camera's intrinsic values for calibration
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
            self.connect(self.OA_dialog, pyqtSignal("destroyed()"), self.overlay_adjustment_closed)
            self.connect(self.OA_dialog, pyqtSignal("update_overlay(PyQt_PyObject)"), self.update_overlay)
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
        image_name, _ = QFileDialog.getOpenFileName(self, 'Browse...', '', 'Image Files (*.png)')

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
        image_name = image_name.replace('.png', '')

        # Apply the image processing techniques in order, subsequently saving the image and incrementing progress
        progress.emit(0)
        status.emit('Undistorting image...')
        image = image_processing.ImageCorrection().distortion_fix(image)
        cv2.imwrite('%s_undistort.png' % image_name, image)
        progress.emit(25)
        status.emit('Fixing perspective warp...')
        image = image_processing.ImageCorrection().perspective_fix(image)
        cv2.imwrite('%s_perspective.png' % image_name, image)
        progress.emit(50)
        status.emit('Cropping image to size...')
        image = image_processing.ImageCorrection().crop(image)
        cv2.imwrite('%s_crop.png' % image_name, image)
        progress.emit(75)
        status.emit('Applying CLAHE equalization...')
        image = image_processing.ImageCorrection().clahe(image)
        cv2.imwrite('%s_clahe.png' % image_name, image)
        progress.emit(100)
        status.emit('Image successfully processed and saved to same folder as input image.')

        return os.path.dirname(image_name).replace('/', '\\')

    @staticmethod
    def image_converter_finished(image_folder):
        """Open the folder containing the processed images for the user to view after conversion is finished"""
        subprocess.Popen('explorer %s' % image_folder)

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
        pass

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

        self.labelCameraStatus.setText('ACQUIRING...')
        self.labelTriggerStatus.setText('ACQUIRING...')

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
        worker.signals.status.connect(self.update_status)
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

        # Check if the Resume From checkbox is checked and if so, set the current layer to the entered number
        # 0.5 is subtracted as it is assumed that the first image captured will be the previous layer's scan
        if self.checkResume.isChecked():
            self.spinStartingLayer.setEnabled(False)
            self.config['ImageCapture']['Layer'] = self.spinStartingLayer.value() - 0.5
            self.config['ImageCapture']['Phase'] = 1

            with open('config.json', 'w+') as config:
                json.dump(self.config, config, indent=4, sort_keys=True)

        # Open the COM port associated with the attached trigger device
        self.serial_trigger = serial.Serial(self.labelTriggerStatus.text(), 9600, timeout=1)

        # Reset the elapsed time and idle time counters
        self.stopwatch_elapsed = 0
        self.stopwatch_idle = 0

        # Create a QTimer that will increment the two running timers
        self.timer_stopwatch = QTimer()

        # Connect the timeout of the QTimer to the corresponding function
        self.timer_stopwatch.timeout.connect(self.update_time)

        # Start the QTimer which will timeout and execute the connected slot every given milliseconds
        self.timer_stopwatch.start(1000)

        # See docstring of the following function for an explanation of how the trigger polling works
        # self.worker_trigger = qt_multithreading.Worker(self.poll_trigger)
        # self.worker_trigger.signals.result.connect(self.capture_run)

        self.capture_run('')

    def capture_run(self, result):
        """Because reading from the serial trigger takes a little bit of time, it temporarily freezes the main UI
        As such, the serial read is turned into a QRunnable function that is passed to a worker using the QThreadPool
        The current method works as a sort of recursive loop, where the result of the trigger poll is checked
        If a trigger is detected, the corresponding image capture function is executed as a worker to the QThreadPool
        Otherwise, another trigger polling worker is started and the loop keeps repeating
        The loop is broken if the Pause button is pressed or the build is stopped outright
        """

        if 'PAUSE' in self.pushPauseResume.text() and self.pushPauseResume.isEnabled():
            if 'TRIG' in result:
                self.pushPauseResume.setEnabled(False)
                self.pushStop.setEnabled(False)
                worker = qt_multithreading.Worker(image_capture.ImageCapture().acquire_image_run)
                worker.signals.status.connect(self.update_status)
                worker.signals.finished.connect(self.capture_run_finished)
                self.threadpool.start(worker)
            else:
                self.update_status('Waiting for trigger.')
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
        self.capture_run('')

    def pause_build(self):
        """Executes when the Pause/Resume button is clicked"""

        # Pause function, stop the timer and the trigger polling loop
        if 'PAUSE' in self.pushPauseResume.text():
            self.pushPauseResume.setStyleSheet('QPushButton {color: #00aa00;}')
            self.pushPauseResume.setText('RESUME')
            self.timer_stopwatch.stop()
            self.update_status('Current build paused.')

        # Resume function, start the timer and restart the trigger polling loop
        elif 'RESUME' in self.pushPauseResume.text():
            self.pushPauseResume.setStyleSheet('QPushButton {color: #ffaa00;}')
            self.pushPauseResume.setText('PAUSE')
            self.timer_stopwatch.start(1000)
            self.capture_run_finished()
            self.update_status('Current build resumed.')

    def stop_build(self):
        """Executes when the Stop button is clicked"""

        # Enable / disable certain UI elements
        # Disabling the Pause button stops the trigger polling loop
        self.update_status('Build stopped.', 10000)
        self.pushRun.setEnabled(True)
        self.pushPauseResume.setEnabled(False)
        self.pushStop.setEnabled(False)
        self.pushAcquireCT.setEnabled(True)
        self.pushCapture.setEnabled(True)
        self.checkResume.setEnabled(True)

        # Stop the stopwatch timer and close the serial port
        self.timer_stopwatch.stop()
        self.serial_trigger.close()

    def reset_idle(self):
        """Resets the stopwatch idle counter whenever an image has been captured"""
        self.stopwatch_idle = 0

    # DISPLAY

    def start_display(self):
        """Displays the image based on the corresponding slider's value on the corresponding tab label
        Allows the user to scroll through the images and jump to specific ones
        The trigger event for changing things is a change in slider value
        Note: The order of the images will be the order that the images are in the folder itself
        The images will need to have proper numbering to ensure that the layer numbers are accurate
        """

        # Empty strings to concatenate additional strings to for the status message
        status_empty = str()
        status_display = str()

        for index in range(4):
            # Update the current image using the current value of the corresponding slider
            self.update_image_list(index)
            self.update_image(index)

            # Checks if the list is empty or not
            if self.display['ImageList'][index]:

                # Concatenate a string to be used for the status message
                status_display += self.display['FolderNames'][index]
                # Enable certain UI elements
                self.groupDisplayOptions.setEnabled(True)
            else:
                status_empty += self.display['FolderNames'][index]

        if status_empty == '':
            self.update_status('Displaying %s images on their respective tabs.' % status_display[:-1])
        else:
            self.update_status('%s folder(s) empty. Displaying %s images on their respective tabs.' %
                               (status_empty[:-1], status_display[:-1]))

        self.display_flag = True
        self.actionZoomIn.setEnabled(True)
        self.actionZoomOut.setEnabled(True)

        self.update_ranges(self.widgetDisplay.currentIndex())

        # Display the image on the graphics scene
        for index in range(4):
            self.update_display(index)

        # Enable the slider and its up and down buttons
        self.frameSlider.setEnabled(True)

        # Enable and set the currently displayed tab's layer range
        self.spinLayer.setEnabled(True)
        self.pushGo.setEnabled(True)

    def update_display(self, index=None):
        """Updates the MainWindow widgetDisplay to show an image on the currently displayed tab as per toggles"""

        # Grab the current tab index (for clearer code purposes)
        if index is None:
            index = self.widgetDisplay.currentIndex()

        # Grab the names of certain elements (for clearer code purposes)
        label = self.display['LabelNames'][index]
        graphics = self.display['GraphicsNames'][index]
        stack = self.display['StackNames'][index]
        image = self.display['Image'][index]

        # Check if the image folder has an actual image to display
        if not self.display['ImageList'][index]:
            stack.setCurrentIndex(0)
            label.setText('%s folder empty. Nothing to display.' % self.display['FolderNames'][index][:-1])
        else:
            stack.setCurrentIndex(1)
            if self.checkOverlay.isChecked():

                # Update and grab the current overlay image
                self.update_image(2)
                overlay = self.display['Image'][2]

                # Resizes the overlay image if the resolution doesn't match the displayed image
                if overlay.shape[:2] != image.shape[:2]:
                    overlay = cv2.resize(overlay, image.shape[:2][::-1], interpolation=cv2.INTER_CUBIC)

                overlay = image_processing.ImageCorrection(None).transform(overlay, self.transform)

                # self.update_status('Translation X - 0 Y - 0 | Rotation - 0.00 | Stretch X - 0 Y - 0', 10000)
                # Display a status message with the current transformation of the overlay image
                self.update_status('Translation X - %d Y - %d | Rotation - %.2f | Stretch X - %d Y - %d' %
                                   (self.transform[1], -self.transform[0], -1 * self.transform[2],
                                    self.transform[4], self.transform[5]), 10000)

                image = cv2.add(image, overlay)

            if self.radioCLAHE.isChecked():
                image = image_processing.ImageCorrection.clahe(image)

            # Display the image on the current GraphicsView
            graphics.set_image(self.convert2pixmap(image))

            # Save the current (modified) image so that it can be exported if need be
            self.display['DisplayImage'][index] = image

    def toggle_overlay(self):
        """Overlay process is done in the update_display method
        This method is mostly to show the appropriate status message"""

        if self.checkOverlay.isChecked():
            # Display the message for 5 seconds
            self.update_status('Displaying part contours.')
            self.pushOverlayAdjustment.setEnabled(True)
        else:
            self.update_status('Hiding part contours.')
            self.pushOverlayAdjustment.setEnabled(False)

        self.update_display(self.widgetDisplay.currentIndex())

    def update_overlay(self, transform):
        """Executes the adjustment of the overlay"""
        with open('config.json') as config:
            self.config = json.load(config)

        self.transform = transform

        self.update_display(self.widgetDisplay.currentIndex())

    @staticmethod
    def convert2pixmap(image):
        """Converts the received image into Pixmap format that can be displayed on the label in Qt"""

        # If the image is a BGR image, convert to RGB so that colours can be displayed properly
        if (len(image.shape) == 3): image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Convert to pixmap using in-built Qt functions
        qimage = QImage(image.data, image.shape[1], image.shape[0], 3 * image.shape[1], QImage.Format_RGB888)
        return QPixmap.fromImage(qimage)

    # MISCELlANEOUS UI ELEMENT FUNCTIONALITY

    def tab_change(self, index):
        """Executes when the focused tab on widgetDisplay changes to enable/disable buttons and change layer values"""

        self.sliderDisplay.blockSignals(True)

        if self.display_flag:
            # Set the layer spinbox's range depending on the currently displayed tab
            self.update_ranges(index)
            self.sliderDisplay.setValue(self.display['CurrentLayer'][index])
            self.display['GraphicsNames'][index].reset_image()

            # Set the current layer number depending on the currently displayed tab
            self.labelLayerNumber.setText(str(self.display['CurrentLayer'][index]).zfill(4))

            # Disable the display options groupbox if there isn't a currently displayed image
            if self.display['ImageList'][index] == []:
                self.groupDisplayOptions.setEnabled(False)
                self.menu_display.setEnabled(False)
            else:
                self.groupDisplayOptions.setEnabled(True)
                self.menu_display.setEnabled(True)
                if index == 2:
                    self.checkOverlay.setEnabled(False)
                    self.checkOverlay.setChecked(False)
                else:
                    self.checkOverlay.setEnabled(True)

        self.sliderDisplay.blockSignals(False)

    def tab_focus(self, index, value):
        """Changes the tab focus to the received index's tab and sets the slider value to the received value
        Used for when an image has been captured and focus is to be given to the new image
        """
        pass
        # if self.display_flag:
        #     self.widgetDisplay.setCurrentIndex(int(index))
        #     self.display['SliderNames'][int(index)].setValue(int(value))

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
            # Grab the name of the image using the displayed layer number (subtract 1 due to code starting from 0)
            name = self.display['ImageList'][self.widgetDisplay.currentIndex()][int(self.labelLayerNumber.text()) - 1]
            if action == action_show_image:
                # Need to turn the forward slashes into backslash due to windows explorer only working with backslashes
                subprocess.Popen(r"""explorer /select, %s""" % name.replace('/', '\\'))
            elif action == action_open_image:
                os.startfile(name)
            elif action == action_export:
                self.export_image()

    def slider_change(self, value):
        """Executes when the value of the scrollbar changes to then update the tooltip with the new value
        Also updates the relevant layer numbers of specific UI elements and other internal functions
        """

        # Updates the label number and slider tooltip with the currently displayed tab's slider's value
        self.labelLayerNumber.setText(str(value).zfill(4))
        self.sliderDisplay.setToolTip(str(value))
        self.display['CurrentLayer'][self.widgetDisplay.currentIndex()] = value
        self.display['GraphicsNames'][self.widgetDisplay.currentIndex()].reset_image()

        # Reloads the current image using the current value of the corresponding slider
        self.update_image(self.widgetDisplay.currentIndex())

        # Display the image on the label
        self.update_display(self.widgetDisplay.currentIndex())

    def slider_up(self):
        """Increments the slider by 1"""
        self.sliderDisplay.setValue(self.sliderDisplay.value() + 1)

    def slider_down(self):
        """Decrements the slider by 1"""
        self.sliderDisplay.setValue(self.sliderDisplay.value() - 1)

    def folder_change(self, folder):
        """Executes whenever a change of items in any of the image folders is detected by the QFileSystemWatcher
        Updates the Layer spinBox and the Sliders with a new range of acceptable values
        """

        # Correlate the received folder to an index value
        if 'coat' in os.path.basename(folder):
            index = 0
        elif 'scan' in os.path.basename(folder):
            index = 1
        elif 'contour' in os.path.basename(folder):
            index = 2
        elif 'single' in os.path.basename(folder):
            index = 3

        # Updates various UI elements with updated values
        self.update_image_list(index)
        self.update_ranges(self.widgetDisplay.currentIndex())

        if self.display_flag:
            self.update_image(index)
            self.update_display(index)

    def update_image_list(self, index):
        """Updates the ImageList dictionary with a new list of images"""

        # Empty the list via slice assignment
        self.display['ImageList'][index][:] = list()

        # Checks the returned sorted folder list for actual images (.png or .jpg) while ignoring other files
        for filename in os.listdir(self.display['ImageFolder'][index]):
            if '.png' in filename or '.jpg' in filename or '.jpeg' in filename:
                self.display['ImageList'][index].append(self.display['ImageFolder'][index] + '/' + filename)

        # If the list of filenames remains empty (aka no images in folder), set the corresponding image to None
        # Also enable/disable certain UI elements if the received index matches the current widgetDisplay's index
        if not self.display['ImageList'][index]:
            self.display['Image'][index] = None
            self.display['LayerRange'][index] = 1
            if self.widgetDisplay.currentIndex() == index:
                self.groupDisplayOptions.setEnabled(False)
                self.menu_display.setEnabled(False)
        else:
            # Save the ranges in a list whose index corresponds with the tabs
            self.display['LayerRange'][index] = len(self.display['ImageList'][index])
            if self.widgetDisplay.currentIndex() == index:
                self.groupDisplayOptions.setEnabled(True)
                self.menu_display.setEnabled(True)

    def update_image(self, index):
        """Updates the Image dictionary with the loaded images"""

        # Check if list isn't empty, otherwise set the corresponding image to None
        if self.display['ImageList'][index]:
            # Check if the Toggle Overlay checkbox is checked
            # If so, use the current tab's slider value to choose which overlay image to load
            try:
                # Load the image into memory and store it in the dictionary
                # Decrement by 1 because code starts at 0
                self.display['Image'][index] = cv2.imread(
                    self.display['ImageList'][index][self.sliderDisplay.value() - 1])
            except IndexError:
                self.update_status('Part contours not found.')
        else:
            self.display['Image'][index] = None

    def update_ranges(self, index):
        """Updates the layer spinbox's maximum acceptable range, tooltip, and the slider's maximum range"""
        self.spinLayer.setMaximum(self.display['LayerRange'][index])
        self.spinLayer.setToolTip('1 - %s' % self.display['LayerRange'][index])
        self.sliderDisplay.setMaximum(self.display['LayerRange'][index])

    def update_ct(self, status):
        """Updates the status boxes for the acquisition of the camera and trigger with the received status details
        Also enables or disables the Run and Capture Single Image buttons depending on the result"""

        # Camera status
        if bool(status[0]):
            self.labelCameraStatus.setText('FOUND')
            self.pushCapture.setEnabled(True)
            if bool(status[1]):
                self.pushRun.setEnabled(True)
        else:
            self.labelCameraStatus.setText('NOT FOUND')
            self.pushRun.setEnabled(False)
            self.pushCapture.setEnabled(False)

        # Trigger status
        if bool(status[1]):
            self.labelTriggerStatus.setText(status[1])
        else:
            self.labelTriggerStatus.setText('NOT FOUND')
            self.pushRun.setEnabled(False)

    def update_time(self):
        """Updates the timers at the bottom right of the Main Window with an incremented formatted timestamp"""

        self.stopwatch_elapsed += 1
        self.stopwatch_idle += 1

        self.labelElapsedTime.setText(self.format_time(self.stopwatch_elapsed))
        self.labelIdleTime.setText(self.format_time(self.stopwatch_idle))

    @staticmethod
    def format_time(time):
        """Format the individual seconds, minutes and hours into proper string time format"""
        seconds = str(time % 60).zfill(2)
        minutes = str(int((time % 3600) / 60)).zfill(2)
        hours = str(int(time / 3600)).zfill(2)

        return '%s:%s:%s' % (hours, minutes, seconds)

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
        application.setAttribute(Qt.AA_Use96Dpi)
        interface = MainWindow()
        interface.show()
        sys.exit(application.exec_())
