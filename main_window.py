# Import external libraries
import os
import sys
import shutil
import json
import cv2
from PyQt4 import QtGui
from PyQt4.QtCore import SIGNAL, Qt, QEvent

# Compile and import PyQt GUIs
os.system('build_gui.bat')
from gui import mainWindow

# Import related modules
import dialog_windows
import extra_functions
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

        # Menubar -> View

        # Menubar -> Tools
        self.actionCameraCalibration.triggered.connect(self.camera_calibration)
        self.actionImageCapture.triggered.connect(self.image_capture)
        self.actionCameraSettings.triggered.connect(self.camera_settings)
        self.actionSliceConverter.triggered.connect(self.slice_converter)
        self.actionNotificationSettings.triggered.connect(self.notification_settings)
        self.actionDefectProcess.triggered.connect(self.defect_processing)
        self.actionImageConverter.triggered.connect(self.image_converter)
        self.actionOptions.triggered.connect(self.options)

        # Menubar -> Help

        # Display Options Group Box
        self.radioOriginal.toggled.connect(self.update_display)
        self.radioCLAHE.toggled.connect(self.update_display)
        self.checkToggleOverlay.toggled.connect(self.toggle_overlay)

        # OpenCV Processing Group Box
        self.radioOpenCV1.toggled.connect(self.update_display)
        self.radioOpenCV2.toggled.connect(self.update_display)
        self.radioOpenCV3.toggled.connect(self.update_display)
        self.radioOpenCV4.toggled.connect(self.update_display)
        self.radioOpenCV5.toggled.connect(self.update_display)

        # Assorted Tools Group Box
        self.buttonCameraCalibration.clicked.connect(self.camera_calibration)
        self.buttonSliceConverter.clicked.connect(self.slice_converter)
        self.buttonImageCapture.clicked.connect(self.image_capture)
        self.buttonNotificationSettings.clicked.connect(self.notification_settings)
        self.buttonDefectProcessing.clicked.connect(self.defect_processing)
        self.buttonImageConverter.clicked.connect(self.image_converter)
        self.buttonDisplayImages.clicked.connect(self.display_images)

        # Layer Number Frame
        self.buttonGo.clicked.connect(self.set_layer)

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

        # Sliders & Buttons
        self.sliderCE.valueChanged.connect(self.slider_change)
        self.buttonSliderUpCE.clicked.connect(self.slider_up)
        self.buttonSliderDownCE.clicked.connect(self.slider_down)
        self.sliderSE.valueChanged.connect(self.slider_change)
        self.buttonSliderUpSE.clicked.connect(self.slider_up)
        self.buttonSliderDownSE.clicked.connect(self.slider_down)
        self.sliderSLE.valueChanged.connect(self.slider_change)
        self.buttonSliderUpSLE.clicked.connect(self.slider_up)
        self.buttonSliderDownSLE.clicked.connect(self.slider_down)
        self.sliderDA.valueChanged.connect(self.slider_change)
        self.buttonSliderUpDA.clicked.connect(self.slider_up)
        self.buttonSliderDownDA.clicked.connect(self.slider_down)
        self.sliderIC.valueChanged.connect(self.slider_change)
        self.buttonSliderUpIC.clicked.connect(self.slider_up)
        self.buttonSliderDownIC.clicked.connect(self.slider_down)

        # Flags for various conditions
        self.display_flag = False

        # Instantiate any instances that cannot be run simultaneously
        self.FM_instance = None

        # Because each tab on the widgetDisplay has its own set of associated images, display labels and sliders
        # And because they all do essentially the same functions
        # Easier to store each of these in a dictionary under a specific key to call on one of the five sets
        # The current tab's index will be used to grab the corresponding list or name
        self.display = {'Image': [0, 0, 0, 0, 0], 'ImageList': [[], [], [], [], []],
                        'LayerRange': [1, 1, 1, 1, 1], 'SliderValue': [1, 1, 1, 1, 1],
                        'FolderNames': ['Coat/', 'Scan/', 'Slice/', 'Defect/', 'Single/'],
                        'LabelNames': [self.labelDisplayCE, self.labelDisplaySE, self.labelDisplaySLE,
                                       self.labelDisplayDA, self.labelDisplayIC],
                        'SliderNames': [self.sliderCE, self.sliderSE, self.sliderSLE, self.sliderDA, self.sliderIC]}

    # MENUBAR -> FILE

    def new_build(self):
        """Opens a Dialog Window when File > New Build... is clicked
        Allows user to setup a new build and change settings
        Setup as a Modal window, blocking input to other visible windows until this window is closed
        """

        # Create the dialog variable and execute it as a modal window
        new_build_dialog = dialog_windows.NewBuild(self)
        retval = new_build_dialog.exec_()

        # Executes the following if the OK button is clicked
        if retval:
            # Load configuration settings from config.json file
            with open('config.json') as config:
                self.config = json.load(config)

            # Store config settings as respective variables and update appropriate UI elements
            self.setWindowTitle('Defect Monitor - Build ' + str(self.config['BuildName']))
            self.update_status('New build created. Click Image Capture to begin capturing images.')

            # Enable certain UI elements
            self.buttonImageCapture.setEnabled(True)
            self.buttonDisplayImages.setEnabled(True)

            # Instantiate a dialog variable for existence validation purposes
            self.image_capture_dialog = None

            if self.checkTestFolders.isChecked():
                # TODO Temporary list of folders to use in the meantime
                self.display['ImageFolder'] = ['%s/samples/folder1' % self.config['WorkingDirectory'],
                                               '%s/samples/folder2' % self.config['WorkingDirectory'],
                                               '%s/samples/folder3' % self.config['WorkingDirectory'],
                                               '%s/samples/folder4' % self.config['WorkingDirectory'],
                                               '%s/samples/folder5' % self.config['WorkingDirectory']]
            else:
                # Store the names of the five folders to be monitored in the display dictionary
                self.display['ImageFolder'] = ['%s/processed/coat' % self.config['ImageFolder'],
                                               '%s/processed/scan' % self.config['ImageFolder'],
                                               '%s/slice' % self.config['ImageFolder'],
                                               '%s/defects' % self.config['ImageFolder'],
                                               '%s/processed/single' % self.config['ImageFolder']]

            # If a previous Folder Monitor instance exists, stop it
            if self.FM_instance:
                self.FM_instance.stop()

            # Instantiate and run a FolderMonitor instance
            self.FM_instance = extra_functions.FolderMonitor(self.display['ImageFolder'])
            self.connect(self.FM_instance, SIGNAL("folder_change(QString)"), self.folder_change)
            self.FM_instance.start()

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
        self.export_image_name = QtGui.QFileDialog.getSaveFileName(self, 'Export Image As', '', 'Image (*.png)',
                                                                   selectedFilter='*.png')

        # Checking if user has chosen to save the image or clicked cancel
        if self.export_image_name:
            # Check which tab is currently being displayed on the widgetDisplay
            if self.widgetDisplay.currentIndex() == 0:
                cv2.imwrite(str(self.export_image_name), self.image_display_coat)
            elif self.widgetDisplay.currentIndex() == 1:
                cv2.imwrite(str(self.export_image_name), self.image_display_scan)
            elif self.widgetDisplay.currentIndex() == 3:
                cv2.imwrite(str(self.export_image_name), self.image_display_defect)

            # Open a message box with a save confirmation message
            self.export_confirmation = QtGui.QMessageBox()
            self.export_confirmation.setIcon(QtGui.QMessageBox.Information)
            self.export_confirmation.setText('Your image has been saved to %s.' % self.export_image_name)
            self.export_confirmation.setWindowTitle('Export Image')
            self.export_confirmation.exec_()

    # MENUBAR -> VIEW

    # MENUBAR -> TOOLS

    def camera_calibration(self):
        """Opens a Dialog Window when the Camera Calibration button is clicked
        Allows the user to specify a folder of checkboard images to calibrate the attached camera
        Setup as a Modal window, blocking input to other visible windows until this window is closed
        """

        self.update_status('')

        # Create the dialog variable and execute it as a modal window
        camera_calibration_dialog = dialog_windows.CameraCalibration(self)
        camera_calibration_dialog.exec_()

    def image_capture(self):
        """Opens a Dialog Window when the Image Capture button is clicked
        Allows the user to capture images from an attached camera, either a single shot or continuously using a trigger
        Setup as a Modeless window, operating independently of other windows
        """

        self.update_status('')

        if self.image_capture_dialog is None:
            self.image_capture_dialog = dialog_windows.ImageCapture(self, self.config['ImageFolder'])
            try:
                self.connect(self.image_capture_dialog, SIGNAL("accepted()"), self.image_capture_close)
                self.connect(self.image_capture_dialog, SIGNAL("tab_focus(QString, QString)"), self.tab_focus)
            except RuntimeError:
                self.image_capture_close
        try:
            self.image_capture_dialog.show()
            self.image_capture_dialog.activateWindow()
        except RuntimeError:
            self.image_capture_dialog = None

    def image_capture_close(self):
        self.image_capture_dialog = None

    def camera_settings(self):
        """Opens a Dialog Window when Setup > Camera Settings is clicked
        Allows the user to change camera settings which will be sent to the camera before images are taken
        Setup as a Modeless window, operating independently of other windows
        """

        # Create the dialog variable and execute it as a modeless window
        camera_settings_dialog = dialog_windows.CameraSettings(self)
        camera_settings_dialog.show()
        camera_settings_dialog.activateWindow()

    def slice_converter(self):
        """Opens a Dialog Window when the Slice Converter button is clicked
        Allows the user to convert any slice files from .cls or .cli format into ASCII format
        Setup as a Modal window, blocking input to other visible windows until this window is closed
        """

        self.update_status('')

        # Create the dialog variable and execute it as a modal window
        slice_converter_dialog = dialog_windows.SliceConverter(self)
        slice_converter_dialog.exec_()

    def notification_settings(self):
        """Opens a Dialog Window when Setup > Report Settings > Notification Settings is clicked
        Allows user to enter and change the email address and what notifications to be notified of
        Setup as a Modal window, blocking input to other visible windows until this window is closed
        """

        self.update_status('')

        # Create the dialog variable and execute it as a modal window
        notification_settings_dialog = dialog_windows.NotificationSettings(self)
        notification_settings_dialog.exec_()

    def defect_processing(self):
        """Executes when the Analyze for Defects button is clicked
        Takes the currently displayed image and applies a bunch of OpenCV code as defined under DefectDetection
        Displays the processed image on the label in the Defect Analyzer tab on the MainWindow
        """

        self.update_progress('0')

        # Check which tab is currently being displayed on the widgetDisplay
        if self.widgetDisplay.currentIndex() == 0:
            image_raw = self.image_display_coat
        elif self.widgetDisplay.currentIndex() == 1:
            image_raw = self.image_display_scan
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
        self.widgetDisplay.setCurrentIndex(3)
        self.update_status('Displaying images...')

        # Display the defect images on the widgetDisplay tab
        self.update_display()

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

    def display_images(self):
        """Displays the image based on the corresponding slider's value on the corresponding tab label
        Allows the user to scroll through the images and jump to specific ones
        The trigger event for changing things is a change in slider value
        Note: The order of the images will be the order that the images are in the folder itself
        The images will need to have proper numbering to ensure that the layer numbers are accurate
        """

        # Empty strings to concatenate additional strings to for the status message
        status_empty = ''
        status_display = ''

        for index in xrange(5):
            # Update the current image using the current value of the corresponding slider
            self.update_image(index)
            # Start an event filter that detects changes in the label
            self.display['SliderNames'][index].installEventFilter(self)

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
        self.sliderSLE.setEnabled(True)
        self.buttonSliderUpSLE.setEnabled(True)
        self.buttonSliderDownSLE.setEnabled(True)
        self.sliderDA.setEnabled(True)
        self.buttonSliderUpDA.setEnabled(True)
        self.buttonSliderDownDA.setEnabled(True)
        self.sliderIC.setEnabled(True)
        self.buttonSliderUpIC.setEnabled(True)
        self.buttonSliderDownIC.setEnabled(True)

        # Enable and set the currently displayed tab's layer range
        self.spinLayer.setEnabled(True)
        self.buttonGo.setEnabled(True)
        self.update_layer_range(self.widgetDisplay.currentIndex())

    def options(self):
        pass

    # MENUBAR -> HELP

    # BUTTONS
    def set_layer(self):
        """Changes the displayed slider's value which in turn executes the slider_change method"""
        self.display['SliderNames'][self.widgetDisplay.currentIndex()].setValue(self.spinLayer.value())

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
        """Overlay process is done in the update_display method
        This method is mostly to show the appropriate status message"""

        if self.checkToggleOverlay.isChecked():
            # Display the message for 5 seconds
            self.update_status('Displaying part contours.', 5000)
        else:
            self.update_status('Hiding part contours.', 5000)

        self.update_display()

    # DISPLAY

    def update_display(self):
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
            if self.checkToggleOverlay.isChecked():
                self.update_image(2)
                overlay = self.display['Image'][2]
                if overlay.shape[:2] != image.shape[:2]:
                    overlay = cv2.resize(overlay, image.shape[:2][::-1], interpolation=cv2.INTER_CUBIC )
                image = cv2.add(image, overlay)

            if self.radioCLAHE.isChecked():
                label.setPixmap(self.convert2pixmap(image_processing.ImageCorrection.clahe(image), label))
            else:
                label.setPixmap(self.convert2pixmap(image, label))

        # This block updates the Defect Analyzer tab
        if self.groupOpenCV.isEnabled():
            if self.radioOpenCV1.isChecked(): self.image_display_defect = self.image_defect_1
            if self.radioOpenCV2.isChecked(): self.image_display_defect = self.image_defect_2
            if self.radioOpenCV3.isChecked(): self.image_display_defect = self.image_defect_3
            if self.radioOpenCV4.isChecked(): self.image_display_defect = self.image_defect_4
            if self.radioOpenCV5.isChecked(): self.image_display_defect = self.image_defect_5

            # Display the defect image on its respective label after converting it to pixmap
            self.labelDisplayDA.setPixmap(self.convert2pixmap(self.image_display_defect))

    @staticmethod
    def convert2pixmap(image, label):
        """Converts the received image into Pixmap format that can be displayed on the label in Qt"""

        # If the image is a BGR image, convert to RGB so that colours can be displayed properly
        if (len(image.shape)==3):
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Convert to pixmap using in-built Qt functions
        q_image = QtGui.QImage(image.data, image.shape[1], image.shape[0], 3 * image.shape[1],
                               QtGui.QImage.Format_RGB888)
        q_pixmap = QtGui.QPixmap.fromImage(q_image)

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
            else:
                self.groupDisplayOptions.setEnabled(True)
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
        if self.display_flag:
            self.widgetDisplay.setCurrentIndex(int(index))
            self.display['SliderNames'][int(index)].setValue(int(value))

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

        self.update_status('')

        # Updates various UI elements with updated values
        self.update_image_list(int(slider))
        self.update_layer_range(self.widgetDisplay.currentIndex())

        if self.display_flag:
            self.update_image(int(slider))
            self.update_display()

    def update_image_list(self, index):
        """Updates the ImageList dictionary with a new list of images"""

        # Empty the list via slice assignment
        self.display['ImageList'][index][:] = []

        # Checks the returned sorted folder list for actual images (.png or .jpg) while ignoring other files
        for filename in sorted(os.listdir(self.display['ImageFolder'][index])):
            if '.png' in filename or '.jpg' in filename or '.jpeg' in filename:
                self.display['ImageList'][index].append(filename)

        # If the list of filenames remains empty (aka no images in folder), set the corresponding image to 0 (nothing)
        if not self.display['ImageList'][index]:
            self.display['Image'][index] = 0
            self.display['LayerRange'][index] = 1
            self.groupDisplayOptions.setEnabled(False)
        else:
            # Save the ranges in a list whose index corresponds with the tabs
            self.display['LayerRange'][index] = len(self.display['ImageList'][index])

    def update_image(self, index):
        """Updates the Image dictionary with the loaded images"""

        # Check if list isn't empty, otherwise set the corresponding image to 0 (nothing)
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
                    cv2.imread('%s/%s' % (self.display['ImageFolder'][index], self.display['ImageList'][index]
                    [self.display['SliderNames'][index_overlay].value() - 1]))
            except IndexError:
                self.update_status('Part contours not found.', 5000)
        else:
            self.display['Image'][index] = 0

    def update_layer_range(self, index):
        """Updates the layer spinbox's maximum acceptable range, tooltip, and the sliders"""
        self.spinLayer.setMaximum(self.display['LayerRange'][index])
        self.spinLayer.setToolTip('1 - %s' % self.display['LayerRange'][index])
        self.display['SliderNames'][index].setMaximum(self.display['LayerRange'][index])

    def update_status(self, string, duration=0):
        """Updates the status bar at the bottom of the Main Window with the received string argument
        Duration refers to how long the message will be displayed in milliseconds
        """
        self.statusBar.showMessage(string, duration)

    def update_progress(self, percentage):
        """Updates the progress bar at the bottom of the Main Window with the received percentage argument"""
        self.progressBar.setValue(int(percentage))

    def eventFilter(self, label, event):
        """Executes whenever the currently displayed label changes in size due to resizing the MainWindow
        All it does is resize the currently displayed image while maintaining the image's aspect ratio
        """
        if (event.type() == QEvent.Resize):
            self.update_display()
            return True
        return QtGui.QMainWindow.eventFilter(self, label, event)

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

        # Terminates running FolderMonitor QThread if running
        try:
            self.FM_instance.stop()
        except AttributeError:
            pass

        # Save configuration settings to config.json file
        with open('config.json', 'w+') as config:
            json.dump(self.config, config)

        # Delete the created image folder if the Clean Up checkbox is checked
        if self.checkCleanup.isChecked():
            try:
                shutil.rmtree('%s' % self.config['ImageFolder'])
            except (WindowsError, AttributeError):
                pass

if __name__ == '__main__':
    def main():
        application = QtGui.QApplication(sys.argv)
        interface = MainWindow()
        interface.show()
        sys.exit(application.exec_())


    main()
