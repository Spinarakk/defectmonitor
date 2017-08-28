# Import external libraries
import os
import sys
import subprocess
import json
import cv2
from PyQt4.QtGui import *
from PyQt4.QtCore import *

# Compile and import PyQt GUIs
os.system('build_gui.bat')
from gui import mainWindow

# Import related modules
import dialog_windows
import extra_functions
import image_processing
import defect_analysis
import slice_converter


class MainWindow(QMainWindow, mainWindow.Ui_mainWindow):
    """Main module used to initiate the main GUI window and all of its associated dialogs/widgets
    Only methods that relate directly manipulating any element of the MainWindow UI are allowed in this module
    All other functions related to image processing etc. are called using QThreads and split into separate modules
    All dialog windows are found and called in the dialog_windows.py
    Note: All QSomeName namespaces are from either the PyQt4.QtGui or PyQt4.QtCore module, including SIGNAL
    """

    def __init__(self, parent=None):

        # Setup Main Window UI
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)

        # Load configuration settings from the config.json file, the hidden configuration file
        # If config.json is empty or missing, the hidden config_default.json file is read and dumped as config.json
        try:
            with open('config.json') as config:
                self.config = json.load(config)
        except (IOError, ValueError):
            with open('config_backup.json') as config:
                self.config = json.load(config)

        # Get the current working directory and save it to the config.json file so later methods can grab it
        # Additionally, create a default builds folder (if it doesn't exist) using the cwd to store images
        self.config['WorkingDirectory'] = os.getcwd().replace('\\', '/')
        self.config['BuildInfo']['Folder'] = self.config['WorkingDirectory'] + '/builds'
        if not os.path.isdir(self.config['BuildInfo']['Folder']):
            os.makedirs(self.config['BuildInfo']['Folder'])

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
        self.actionImageCapture.triggered.connect(self.image_capture)
        self.actionCameraSettings.triggered.connect(self.camera_settings)
        self.actionSliceConverter.triggered.connect(self.slice_converter)
        self.actionDefectProcess.triggered.connect(self.defect_processing)
        self.actionImageConverter.triggered.connect(self.image_converter)
        self.actionOverlayAdjustment.triggered.connect(self.overlay_adjustment)
        self.actionSettings.triggered.connect(self.change_settings)

        # Menubar -> Help

        # Display Options Group Box
        self.radioOriginal.toggled.connect(self.update_display)
        self.radioCLAHE.toggled.connect(self.update_display)
        self.radioDefects.toggled.connect(self.update_display)
        self.checkToggleOverlay.toggled.connect(self.toggle_overlay)

        # Assorted Tools Group Box
        self.buttonCameraCalibration.clicked.connect(self.camera_calibration)
        self.buttonSliceConverter.clicked.connect(self.slice_converter)
        self.buttonImageCapture.clicked.connect(self.image_capture)
        self.buttonDefectProcessing.clicked.connect(self.defect_processing)
        self.buttonImageConverter.clicked.connect(self.image_converter)
        self.buttonOverlayAdjustment.clicked.connect(self.overlay_adjustment)

        # Frames
        self.buttonGo.clicked.connect(self.set_layer)
        self.buttonCheckCT.clicked.connect(self.check_camera_trigger)

        # Image Capture
        self.buttonRun.clicked.connect(self.run)
        self.buttonStop.clicked.connect(self.stop)
        # self.buttonDisplayVF.clicked.connect(self.display_video)

        # Display Widget
        self.widgetDisplay.currentChanged.connect(self.tab_change)
        self.labelDisplayCE.customContextMenuRequested.connect(self.context_menu_display)
        self.labelDisplaySE.customContextMenuRequested.connect(self.context_menu_display)
        self.labelDisplayPC.customContextMenuRequested.connect(self.context_menu_display)
        self.labelDisplayIC.customContextMenuRequested.connect(self.context_menu_display)

        # Sliders & Buttons
        self.sliderCE.valueChanged.connect(self.slider_change)
        self.buttonSliderUpCE.clicked.connect(self.slider_up)
        self.buttonSliderDownCE.clicked.connect(self.slider_down)
        self.sliderSE.valueChanged.connect(self.slider_change)
        self.buttonSliderUpSE.clicked.connect(self.slider_up)
        self.buttonSliderDownSE.clicked.connect(self.slider_down)
        self.sliderPC.valueChanged.connect(self.slider_change)
        self.buttonSliderUpPC.clicked.connect(self.slider_up)
        self.buttonSliderDownPC.clicked.connect(self.slider_down)
        self.sliderIC.valueChanged.connect(self.slider_change)
        self.buttonSliderUpIC.clicked.connect(self.slider_up)
        self.buttonSliderDownIC.clicked.connect(self.slider_down)

        # Flags for various conditions
        self.display_flag = False

        # Instantiate any instances that cannot be run simultaneously
        self.FM_instance = None

        # Instantiate dialog variables that cannot have multiple windows for existence validation purposes
        self.CC_dialog = None
        self.CS_dialog = None
        self.SC_dialog = None
        self.IC_dialog = None
        self.OA_dialog = None

        # Initiate an empty config file name to be used for saving purposes
        self.config_name = None

        # Create a context menu that will appear when the user right-clicks on any of the display labels
        self.menu_display = QMenu()

        # Because each tab on the widgetDisplay has its own set of associated images, display labels and sliders
        # And because they all do essentially the same functions
        # Easier to store each of these in a dictionary under a specific key to call on one of the four sets
        # The current tab's index will be used to grab the corresponding image, list or name
        self.display = {'Image': [0, 0, 0, 0], 'ImageList': [[], [], [], []], 'LayerRange': [1, 1, 1, 1],
                        'FolderNames': ['Coat/', 'Scan/', 'Contour/', 'Single/'],
                        'LabelNames': [self.labelDisplayCE, self.labelDisplaySE, self.labelDisplayPC, self.labelDisplayIC],
                        'SliderNames': [self.sliderCE, self.sliderSE, self.sliderPC, self.sliderIC]}

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
        file_name = str(QFileDialog.getOpenFileName(self, 'Browse...', '', 'JSON File (*.json)'))

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
                self.setup_build(True)

    def setup_build(self, open_flag=False):
        """Sets up the MainWindow and any background threads for the current build"""

        try:
            # Check if the Basler Pylon software has been installed correctly
            # Also if the pypylon folder is available and is the correct version
            import image_capture
        except ImportError:
            # Open a message box with an error stating that certain features cannot be accessed
            self.export_confirmation = QMessageBox()
            self.export_confirmation.setIcon(QMessageBox.Critical)
            self.export_confirmation.setText(
                "Unable to access camera related functions.<br><br>Either the Basler Pylon Software is not "
                "installed, the software wasn't installed as a developer, or PyPylon is either "
                "missing from the working directory, not installed properly, or the incorrect x32/x64 version is "
                "being used.")
            self.export_confirmation.setWindowTitle('New Build')
            self.export_confirmation.exec_()
        else:
            # Set the imported module as an instance variable
            self.image_capture_module = image_capture

            with open('config.json') as config:
                self.config = json.load(config)

            # Store config settings as respective variables and update appropriate UI elements
            self.transform = self.config['ImageCorrection']['TransformParameters']
            self.setWindowTitle('Defect Monitor - Build ' + self.config['BuildInfo']['Name'])

            # Enable certain UI elements
            self.actionSave.setEnabled(True)
            self.actionSaveAs.setEnabled(True)
            self.buttonImageCapture.setEnabled(True)
            self.buttonCheckCT.setEnabled(True)

            # Store the names of the four folders to be monitored in the display dictionary
            self.display['ImageFolder'] = ['%s/processed/coat' % self.config['ImageCapture']['Folder'],
                                           '%s/processed/scan' % self.config['ImageCapture']['Folder'],
                                           '%s/contours' % self.config['ImageCapture']['Folder'],
                                           '%s/processed/single' % self.config['ImageCapture']['Folder']]

            # Instantiate and run a FolderMonitor instance
            self.FM_instance = extra_functions.FolderMonitor(self.display['ImageFolder'])
            self.connect(self.FM_instance, SIGNAL("folder_change(QString)"), self.folder_change)
            self.FM_instance.start()

            self.start_display()

            # Checks for a valid attached camera and trigger
            self.update_status('Checking for valid camera and trigger...')
            self.check_camera_trigger()

            # Converts and draws the contours
            if self.config['BuildInfo']['Convert']:
                # Instantiate and run a SliceConverter instance
                self.SC_instance = slice_converter.SliceConverter(self.config['SliceConverter']['Files'],
                                                                  self.config['BuildInfo']['Draw'])
                self.connect(self.SC_instance, SIGNAL("update_status(QString)"), self.update_status)
                self.connect(self.SC_instance, SIGNAL("update_progress(QString)"), self.update_progress)
                self.connect(self.SC_instance, SIGNAL("finished()"), self.setup_build_finished)
                self.SC_instance.start()
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
        config_name = str(QFileDialog.getSaveFileName(self, 'Save Build As', '', 'JSON File (*.json)',
                                                                   selectedFilter='*.json'))

        # Checking if user has chosen to save the build or clicked cancel
        if config_name:
            self.config_name = config_name
            self.save_build()

    def export_image(self):
        """Opens a FileDialog Window when File > Export Image... is clicked
        Allows the user to save the currently displayed image to whatever location the user specifies as a .png
        """

        # Open a folder select dialog, allowing the user to choose a location and input a name
        image_name = str(QFileDialog.getSaveFileName(self, 'Export Image As', '', 'Image (*.png)',
                                                                   selectedFilter='*.png'))

        # Checking if user has chosen to save the image or clicked cancel
        if image_name:
            # Save the currently displayed image which is saved as an entry in the display dictionary
            cv2.imwrite(image_name, self.display['DisplayImage'])

            # Open a message box with a save confirmation message
            self.export_confirmation = QMessageBox()
            self.export_confirmation.setIcon(QMessageBox.Information)
            self.export_confirmation.setText('The image has been saved to %s.' % image_name)
            self.export_confirmation.setWindowTitle('Export Image')
            self.export_confirmation.exec_()

    def close_build(self):
        pass

    # MENUBAR -> VIEW
    def zoom_in(self):
        pass

    def zoom_out(self):
        pass

    # MENUBAR -> TOOLS

    def camera_calibration(self):
        """Opens a Modeless Dialog Window when the Camera Calibration button is clicked
        Or when Tools -> Camera -> Calibration is clicked
        Allows the user to select a folder of chessboard images to calculate the camera's intrinsic values for calibration
        """

        # Check if the dialog window is already open, if not, create a new window and open it
        # Otherwise focus is given back to the open window
        # Signals listen for if the window is closed, and sets the window to None if so
        if self.CC_dialog is None:
            self.CC_dialog = dialog_windows.CameraCalibration(self)
            self.connect(self.CC_dialog, SIGNAL("destroyed()"), self.camera_calibration_closed)
            self.CC_dialog.show()
        else:
            self.CC_dialog.activateWindow()

    def camera_calibration_closed(self):
        """When the Dialog Window is closed, its object is set to None to allow another window to be opened"""
        self.CC_dialog = None

    def image_capture(self):
        """Opens a Modeless Dialog Window when the Image Capture button is clicked
        Or when Tools -> Camera -> Image Capture is clicked
        Allows the user to capture images from an attached camera, either a single shot or continuously using a trigger
        """

        if self.IC_dialog is None:
            self.IC_dialog = dialog_windows.ImageCapture(self, self.config['ImageCapture']['Folder'])
            self.connect(self.IC_dialog, SIGNAL("destroyed()"), self.image_capture_closed)
            self.connect(self.IC_dialog, SIGNAL("tab_focus(QString, QString)"), self.tab_focus)
            self.IC_dialog.show()
        else:
            self.IC_dialog.activateWindow()

    def image_capture_closed(self):
        """When the Dialog Window is closed, its object is set to None to allow another window to be opened"""
        self.IC_dialog = None

    def camera_settings(self):
        """Opens a Modeless Dialog Window when Tools -> Camera -> Settings is clicked
        Allows the user to change camera settings which will be sent to the camera before images are taken
        """

        if self.CS_dialog is None:
            self.CS_dialog = dialog_windows.CameraSettings(self)
            self.connect(self.CS_dialog, SIGNAL("destroyed()"), self.camera_settings_closed)
            self.CS_dialog.show()
        else:
            self.CS_dialog.activateWindow()

    def camera_settings_closed(self):
        """When the Dialog Window is closed, its object is set to None to allow another window to be opened"""
        self.CS_dialog = None

    def slice_converter(self):
        """Opens a Modeless Dialog Window when the Slice Converter button is clicked
        Or when Tools -> Slice Converter is clicked
        Allows user to convert .cls or .cli files into ASCII encoded scaled contours that OpenCV can draw
        """

        if self.SC_dialog is None:
            self.SC_dialog = dialog_windows.SliceConverter(self)
            self.connect(self.SC_dialog, SIGNAL("destroyed()"), self.slice_converter_closed)
            self.SC_dialog.show()
        else:
            self.SC_dialog.activateWindow()

    def slice_converter_closed(self):
        """When the Dialog Window is closed, its object is set to None to allow another window to be opened"""
        self.SC_dialog = None

    def overlay_adjustment(self):
        """Opens a Modeless Dialog Window when the Overlay Adjustment button is clicked
        Or when Tools -> Overlay Adjustment is clicked
        Allows the user to adjust and transform the overlay image in a variety of ways
        """

        if self.OA_dialog is None:
            self.OA_dialog = dialog_windows.OverlayAdjustment(self)
            self.connect(self.OA_dialog, SIGNAL("destroyed()"), self.overlay_adjustment_closed)
            self.connect(self.OA_dialog, SIGNAL("update_overlay(PyQt_PyObject)"), self.update_overlay)
        else:
            self.OA_dialog.activateWindow()

    def overlay_adjustment_closed(self):
        """When the Dialog Window is closed, its object is set to None to allow another window to be opened"""
        self.OA_dialog = None

    def defect_processing(self):
        """Executes when the Analyze for Defects button is clicked
        Takes the currently displayed image and applies a bunch of OpenCV code as defined under DefectDetection
        Displays the processed image on the label in the Defect Analyzer tab on the MainWindow
        """

        self.update_progress('0')
        overlay = self.display['Image'][2]
        # Check which tab is currently being displayed on the widgetDisplay
        if self.widgetDisplay.currentIndex() == 0:
            image = self.display['Image'][0]
            detector = defect_analysis.DefectDetection(image, overlay, self.display['SliderNames'][
                self.widgetDisplay.currentIndex()].value())
            detector.run()
        elif self.widgetDisplay.currentIndex() == 1:
            image = self.display['Image'][1]

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
            cv2.imwrite('%s/defects/scan_contours_%s.jpg' % (self.config['ImageCapture']['Folder'], self.display['SliderNames'][
                self.widgetDisplay.currentIndex()].value()), image)

    def image_converter(self):
        """Opens a FileDialog when Image Converter button is pressed
        Allows the user to select an image to apply image correction on and saves the processed image in the same folder
        """

        # Get the name of the image file to be processed
        image_name = QFileDialog.getOpenFileName(self, 'Browse...', '', 'Image Files (*.png)')

        # Checking if user has selected a file or clicked cancel
        if image_name:
            self.update_progress(0)
            self.update_status('Processing image...')

            # Read the image
            image_raw = cv2.imread('%s' % image_name)

            # Apply the image processing techniques in order
            image_undistort = image_processing.ImageCorrection(None).distortion_fix(image_raw)
            self.update_progress(20)
            image_perspective = image_processing.ImageCorrection(None).perspective_fix(image_undistort)
            self.update_progress(40)
            image_crop = image_processing.ImageCorrection(None).crop(image_perspective)
            self.update_progress(60)
            image_clahe = image_processing.ImageCorrection(None).clahe(image_crop)
            self.update_progress(80)

            # Save the cropped image and CLAHE applied image in the same folder after removing .png from the file name
            image_name.replace('.png', '')
            cv2.imwrite('%s_undistort.png' % image_name, image_undistort)
            cv2.imwrite('%s_perspective.png' % image_name, image_perspective)
            cv2.imwrite('%s_crop.png' % image_name, image_crop)
            cv2.imwrite('%s_clahe.png' % image_name, image_clahe)

            self.update_progress(100)
            self.update_status('Image successfully processed.')

    def change_settings(self):
        pass

    # MENUBAR -> HELP

    # BUTTONS
    def set_layer(self):
        """Changes the displayed slider's value which in turn executes the slider_change method"""
        self.display['SliderNames'][self.widgetDisplay.currentIndex()].setValue(self.spinLayer.value())

    def run(self):
        self.buttonRun.setEnabled(False)
        self.buttonStop.setEnabled(True)

        self.stopwatch_instance = extra_functions.Stopwatch()
        self.connect(self.stopwatch_instance, SIGNAL("update_time(QString, QString)"), self.update_time)
        self.stopwatch_instance.start()

    def stop(self):

        self.stopwatch_instance.stop()

        self.buttonRun.setEnabled(True)
        self.buttonStop.setEnabled(False)


    # TOGGLES AND CHECKBOXES

    def toggle_overlay(self):
        """Overlay process is done in the update_display method
        This method is mostly to show the appropriate status message"""

        if self.checkToggleOverlay.isChecked():
            # Display the message for 5 seconds
            self.update_status('Displaying part contours.')
            self.buttonOverlayAdjustment.setEnabled(True)
        else:
            self.update_status('Hiding part contours.')
            self.buttonOverlayAdjustment.setEnabled(False)

        self.update_display()

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

        for index in xrange(4):
            # Update the current image using the current value of the corresponding slider
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

        # Display the image on the label
        self.update_display()

        # Enable all the sliders and up/down buttons in all five tabs
        self.sliderCE.setEnabled(True)
        self.buttonSliderUpCE.setEnabled(True)
        self.buttonSliderDownCE.setEnabled(True)
        self.sliderSE.setEnabled(True)
        self.buttonSliderUpSE.setEnabled(True)
        self.buttonSliderDownSE.setEnabled(True)
        self.sliderPC.setEnabled(True)
        self.buttonSliderUpPC.setEnabled(True)
        self.buttonSliderDownPC.setEnabled(True)
        self.sliderIC.setEnabled(True)
        self.buttonSliderUpIC.setEnabled(True)
        self.buttonSliderDownIC.setEnabled(True)

        # Enable and set the currently displayed tab's layer range
        self.spinLayer.setEnabled(True)
        self.buttonGo.setEnabled(True)
        self.update_layer_range(self.widgetDisplay.currentIndex())

    def update_display(self, resize_flag=False):
        """Updates the MainWindow widgetDisplay to show an image on the currently displayed tab as per toggles"""

        # Grab the current tab index (for clearer code purposes)
        index = self.widgetDisplay.currentIndex()

        # Grab the names of certain elements (for clearer code purposes)
        label = self.display['LabelNames'][index]
        image = self.display['Image'][index]

        # Check if the image folder has an actual image to display
        if not self.display['ImageList'][index]:
            label.setText('%s folder empty. Nothing to display.' % self.display['FolderNames'][index][:-1])
        else:
            # If the window was just resized, transform the currently displayed image rather than processing a new one
            if resize_flag:
                image = self.display['DisplayImage']
            else:
                if self.checkToggleOverlay.isChecked():

                    self.update_image(2)
                    overlay = self.display['Image'][2]

                    # Resizes the overlay image if the resolution doesn't match the displayed image
                    if overlay.shape[:2] != image.shape[:2]:
                        overlay = cv2.resize(overlay, image.shape[:2][::-1], interpolation=cv2.INTER_CUBIC)

                    overlay = image_processing.ImageCorrection(None).transform(overlay, self.transform)

                    #self.update_status('Translation X - 0 Y - 0 | Rotation - 0.00 | Stretch X - 0 Y - 0', 10000)
                    # Display a status message with the current transformation of the overlay image
                    self.update_status('Translation X - %d Y - %d | Rotation - %.2f | Stretch X - %d Y - %d' %
                                       (self.transform[1], -self.transform[0], -1 * self.transform[2],
                                        self.transform[4], self.transform[5]), 10000)

                    image = cv2.add(image, overlay)

                if self.radioCLAHE.isChecked():
                    image = image_processing.ImageCorrection.clahe(image)

            # Display the image on the current display label and save a copy of the image to the display dictionary
            # This image copy will be used for export images and for resize events as it's faster
            label.setPixmap(self.convert2pixmap(image, label))
            self.display['DisplayImage'] = image.copy()

    def update_overlay(self, transform):
        """Executes the adjustment of the overlay"""
        with open('config.json') as config:
            self.config = json.load(config)

        self.transform = transform

        self.update_display()

    @staticmethod
    def convert2pixmap(image, label):
        """Converts the received image into Pixmap format that can be displayed on the label in Qt"""

        # If the image is a BGR image, convert to RGB so that colours can be displayed properly
        if (len(image.shape)==3):
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Convert to pixmap using in-built Qt functions
        q_image = QImage(image.data, image.shape[1], image.shape[0], 3 * image.shape[1],
                               QImage.Format_RGB888)
        q_pixmap = QPixmap.fromImage(q_image)

        return q_pixmap.scaled(label.frameSize().width(), label.frameSize().height(),
                               aspectRatioMode=Qt.KeepAspectRatio)

    # MISCELlANEOUS UI ELEMENT FUNCTIONALITY

    def tab_change(self, index):
        """Executes when the focused tab on widgetDisplay changes to enable/disable buttons and change layer values"""

        # Set the current layer number depending on the currently displayed tab
        self.labelLayerNumber.setText(str(self.display['SliderNames'][index].value()).zfill(4))

        # Set the layer spinbox's range depending on the currently displayed tab
        self.update_layer_range(index)

        # If the Display Images button has been pressed
        if self.display_flag:
            self.update_display()
            # Disable the display options groupbox if there isn't a currently displayed image
            if self.display['ImageList'][index] == []:
                self.groupDisplayOptions.setEnabled(False)
                self.menu_display.setEnabled(False)
            else:
                self.groupDisplayOptions.setEnabled(True)
                self.menu_display.setEnabled(True)
                if index > 1 and index < 4:
                    self.buttonDefectProcessing.setEnabled(False)
                    self.checkToggleOverlay.setEnabled(False)
                    self.checkToggleOverlay.setChecked(False)
                else:
                    self.buttonDefectProcessing.setEnabled(True)
                    self.checkToggleOverlay.setEnabled(True)

    def tab_focus(self, index, value):
        """Changes the tab focus to the received index's tab and sets the slider value to the received value
        Used for when an image has been captured and focus is given to the new image
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

        # Check if a valid image is being displayed, otherwise diable the menu
        if not self.display['ImageList'][self.widgetDisplay.currentIndex()]:
            self.menu_display.setEnabled(False)

        # Open the context menu at the received position
        action = self.menu_display.exec_(self.labelDisplayCE.mapToGlobal(position))

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
        self.display['SliderNames'][self.widgetDisplay.currentIndex()].setToolTip(str(value))
        # Reloads the current image using the current value of the corresponding slider
        self.update_image(self.widgetDisplay.currentIndex())

        # Display the image on the label
        self.update_display()

    def slider_up(self):
        """Increments the slider by 1, which slider depends on the current selected tab"""

        # Grab the name of the currently displayed slider (for clearer code purposes)
        slider = self.display['SliderNames'][self.widgetDisplay.currentIndex()]

        # Set the new value of the slider by an increment of 1
        slider.setValue(slider.value() + 1)

    def slider_down(self):
        """Decrements the slider by 1, which slider depends on the current selected tab"""
        # Grab the name of the currently displayed slider (for clearer code purposes)
        slider = self.display['SliderNames'][self.widgetDisplay.currentIndex()]

        # Set the new value of the slider by an increment of 1
        slider.setValue(slider.value() - 1)

    def folder_change(self, slider):
        """Executes whenever a change of items in any of the image folders is detected
        Updates the Layer spinBox and the Sliders with a new range of acceptable values
        """

        # Updates various UI elements with updated values
        self.update_image_list(int(slider))
        self.update_layer_range(self.widgetDisplay.currentIndex())

        if self.display_flag:
            self.update_image(int(slider))
            self.update_display()

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
            index_overlay = index
            if self.checkToggleOverlay.isChecked():
                index_overlay = self.widgetDisplay.currentIndex()
            try:
                # Load the image into memory and store it in the dictionary
                # Decrement by 1 because code starts at 0
                self.display['Image'][index] = \
                    cv2.imread('%s' % self.display['ImageList'][index]
                    [self.display['SliderNames'][index_overlay].value() - 1])
            except IndexError:
                self.update_status('Part contours not found.')
        else:
            self.display['Image'][index] = None

    def update_layer_range(self, index):
        """Updates the layer spinbox's maximum acceptable range, tooltip, and the sliders"""
        self.spinLayer.setMaximum(self.display['LayerRange'][index])
        self.spinLayer.setToolTip('1 - %s' % self.display['LayerRange'][index])
        self.display['SliderNames'][index].setMaximum(self.display['LayerRange'][index])

    def check_camera_trigger(self):
        """Checks for a valid attached camera and trigger"""

        camera_flag = self.image_capture_module.ImageCapture().acquire_camera()
        trigger_flag = self.image_capture_module.ImageCapture().acquire_trigger()

        if bool(camera_flag):
            self.labelCameraStatus.setText('FOUND')
            if bool(trigger_flag):
                self.buttonRun.setEnabled(True)
        else:
            self.labelCameraStatus.setText('NOT FOUND')
            self.labelTriggerStatus.setText('NOT FOUND')
            self.buttonRun.setEnabled(False)
        if bool(trigger_flag):
            self.labelTriggerStatus.setText(str(trigger_flag))

    def resizeEvent(self, event):
        """Executes whenever the MainWindow changes in size due to resizing or maximizing the window
        All it does is resize the currently displayed image while maintaining the image's aspect ratio"""
        if self.display_flag:
            self.update_display(True)

    def update_time(self, time_elapsed, time_idle):
        """Updates the timers at the bottom right of the Main Window with the received time"""
        self.labelElapsedTime.setText(time_elapsed)
        self.labelIdleTime.setText(time_idle)

    def update_status(self, string, duration=0):
        """Updates the default status bar at the bottom of the Main Window with the received string argument"""
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
        self.config['BuildInfo']['Name'] = 'Default'
        self.config['ImageCapture']['Layer'] = 0.5
        self.config['ImageCapture']['Phase'] = 1
        self.config['ImageCapture']['Single'] = 1

        # Terminates running FolderMonitor QThread if running
        try:
            self.FM_instance.stop()
        except AttributeError:
            pass

        # Save configuration settings to config.json file
        with open('config.json', 'w+') as config:
            json.dump(self.config, config, indent=4, sort_keys=True)


if __name__ == '__main__':
    def main():
        application = QApplication(sys.argv)
        interface = MainWindow()
        interface.show()
        sys.exit(application.exec_())


    main()
