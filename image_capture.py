# Import external libraries
import os
import json
import time
import cv2
import pypylon
import serial
from PyQt4.QtCore import QThread, SIGNAL

# Import related modules
import image_processing


class ImageCapture(QThread):
    """Module used to capture images from the connected Basler Ace acA3800-10gm GigE camera if attached
    Images are acquired through either method depending on the raised flags
    If single, only one image is acquired, saved and emitted back to the function caller
    If run, the while loop waits indefinitely till a serial trigger is detected
    It then acquires and saves the image, then sleeps for a predefined time until the next trigger is allowed
    """

    def __init__(self, single_flag=False, run_flag=False):

        # Defines the class as a thread
        QThread.__init__(self)

        # Load configuration settings from config.json file
        self.acquire_settings()

        # Store received arguments as instance variables
        self.single_flag = single_flag
        self.run_flag = run_flag

        # For CurrentPhase, 0 corresponds to Coat, 1 corresponds to Scan
        self.current_layer = self.config['CurrentLayer']
        self.current_phase = self.config['CurrentPhase']
        self.capture_count = self.config['CaptureCount']
        self.phases = ['coat', 'scan']

        # Settings for combo box selections are saved and accessed as a list of strings which can be modified here
        self.pixel_format_list = ['Mono8', 'Mono12', 'Mono12Packed']

    def run(self):

        self.emit(SIGNAL("update_status(QString)"), 'Capturing Image(s)...')
        self.acquire_settings()
        self.acquire_camera()

        self.image_folder = self.config['ImageFolder']

        # Opens up the camera and sends it the stored settings to be used for capturing images
        # Put in a try loop in case the camera cannot be opened for some reason (like another program using it)
        try:
            self.camera.open()
            self.apply_settings()
        except:
            # If camera can't be opened, send a status update and initiate the stop method
            self.emit(SIGNAL("update_status(QString)"), 'Camera in use by other application.')
            self.stop()

        # Single Flag
        if self.single_flag:
            self.emit(SIGNAL("update_status(QString)"), 'Capturing single image...')
            self.acquire_image_single()
        else:
            self.acquire_trigger()

        # Run Flag
        while self.run_flag:
            self.emit(SIGNAL("update_status(QString)"), 'Waiting for trigger.')
            self.acquire_image_run()

        # Close the camera when done to allow other applications to use it
        self.camera.close()

        # Set the following values as the current values to be able to restore same state if run again
        self.config['CurrentLayer'] = self.current_layer
        self.config['CurrentPhase'] = self.current_phase

        # Save configuration settings to config.json file
        with open('config.json', 'w+') as config:
            json.dump(self.config, config)

    def acquire_camera(self):
        """Accesses the pypylon wrapper and checks the ethernet ports for a connected camera
        Returns camera information if found and creates the camera variable, else False
        """

        # Check for available cameras
        self.available_camera = pypylon.factory.find_devices()

        if bool(self.available_camera):
            # Create a camera variable that acts as the camera itself
            self.camera = pypylon.factory.create_device(self.available_camera[0])
            return self.camera.device_info
        else:
            return False

    def acquire_trigger(self):
        """Accesses a range of COM ports on the computer for an attached USB2 device
        Returns accessed COM port if found and creates the serial trigger variable, else False
        """

        # Create a list of ports as COM1, COM2 etc.
        ports = ['COM%s' % i for i in xrange(1, 10)]

        # Checks through all the COM ports for an available connected trigger device
        for port in ports:
            try:
                # Open the COM port with a baud rate of 9600 and a 1 second timeout
                self.serial_trigger = serial.Serial(port, 9600, timeout=1)

                # Read the serial line
                self.serial_trigger_read = self.serial_trigger.readline().strip()

                # The Arduino has been programmed to send back tildes by default
                if '~' in self.serial_trigger_read:
                    return port
                else:
                    self.serial_trigger.close()
            except (OSError, serial.SerialException, serial.SerialTimeoutException):
                # Move on to the next COM port
                pass

        # Returns false if the for loop iterates through all the COM ports and can't find an attached device
        return False

    def acquire_settings(self):
        """Load the camera settings which are saved to the config.json file"""

        with open('config.json') as config:
            self.config = json.load(config)

    def apply_settings(self):
        """Applies the stored camera settings from the config.json file to the connected camera
        The settings are saved as an index value as the pylon wrapper only accepts strings for some properties
        The strings are saved in their respective lists and the index is used to call the respective one
        """

        # These properties are changeable through the UI
        self.camera.properties['PixelFormat'] = self.pixel_format_list[self.config['PixelFormat']]
        self.camera.properties['ExposureTimeAbs'] = self.config['ExposureTimeAbs']
        self.camera.properties['GevSCPSPacketSize'] = self.config['PacketSize']
        self.camera.properties['GevSCPD'] = self.config['InterPacketDelay']
        self.camera.properties['GevSCFTD'] = self.config['FrameTransmissionDelay']

        # These properties are here to override the camera's 'default' and can be changed here
        self.camera.properties['TriggerSelector'] = 'AcquisitionStart'
        self.camera.properties['TriggerMode'] = 'Off'
        self.camera.properties['TriggerSource'] = 'Line1'
        self.camera.properties['TriggerActivation'] = 'RisingEdge'
        self.camera.properties['AcquisitionFrameRateEnable'] = 'False'
        self.camera.properties['AcquisitionFrameCount'] = 1

    def acquire_image_single(self):
        """Acquire a single image from the camera"""

        # Grab the image from the camera, error checking in case image capture fails
        try:
            image = next(self.camera.grab_images(1))
        except RuntimeError:
            self.emit(SIGNAL("update_status(QString)"), 'Error grabbing image. Try again.')
            self.camera.close()
        else:
            # Send the image, the current layer and the phase back to the ImageCapture dialog window
            self.emit(SIGNAL("image_correction(PyQt_PyObject, QString, QString)"),
                      image, str(self.config['CaptureCount']), 'single')

            # Update the capture counter which will be saved to the config.json file
            self.config['CaptureCount'] += 1
            self.emit(SIGNAL("update_status(QString)"), 'Image captured.')

    def acquire_image_run(self):
        """Acquire multiple images from the camera when trigger is detected"""

        # Read from the serial interface
        self.trigger = self.serial_trigger.readline().strip()

        # Arduino has been programmed to return a 'TRIG' if reed switch has been triggered
        if self.trigger == 'TRIG':

            self.emit(SIGNAL("update_status(QString)"), 'Trigger Detected. Capturing image...')

            # Grab the image from the camera, error checking in case image capture fails
            try:
                image = next(self.camera.grab_images(1))
            except RuntimeError:
                time.sleep(1)
                image = next(self.camera.grab_images(1))

            # Send the image, the current layer and the phase back to the ImageCapture dialog window
            self.emit(SIGNAL("image_correction(PyQt_PyObject, QString, QString)"),
                      image, str(int(self.current_layer)), self.phases[self.current_phase])

            # Emit a signal that resets the internal countdown saying that an image has been successfully captured
            self.emit(SIGNAL("reset_time_idle()"))

            # Loop used to disallow triggering for additional images for however many seconds
            # Also displays remaining timeout on the status bar
            for seconds in range(self.config['TriggerTimeout'], 0, -1):
                # If statement used to suppress the status update if the Stop button is pressed
                if self.run_flag:
                    self.emit(SIGNAL("update_status(QString)"), 'Image saved. %s second timeout...' % seconds)
                time.sleep(1)

            # Increment the layer (by 1) every second image, and toggle the phase
            self.current_layer += 0.5
            self.current_phase = (self.current_phase + 1) % 2

            # Reset the serial input buffer to prevent triggers within the timeout window causing another image save
            self.serial_trigger.reset_input_buffer()

    def correction(self, image, phase=None, layer=None, count=None):
        """Executes if the Apply Correction checkbox has been checked"""

        # Apply the image processing techniques in order
        image = image_processing.ImageCorrection(None, None, None).distortion_fix(image)
        image = image_processing.ImageCorrection(None, None, None).perspective_fix(image)
        image = image_processing.ImageCorrection(None, None, None).crop(image)
        image = image_processing.ImageCorrection(None, None, None).clahe(image)

        # Save the processed image in the processed folder with an appended file name
        if bool(count):
            # Create a file name for the corrected image
            image_name = '%s/processed/image_capture_%s_processed.png' % (self.image_folder, str(int(count)).zfill(4))
            cv2.imwrite(image_name, image)
            self.emit(SIGNAL("display_image(QString)"), image_name)
        else:
            image_name = '%s/processed/image_%s_%s_processed.png' % (self.image_folder, self.phases[phase],
                                                                     str(int(layer)).zfill(4))
            cv2.imwrite(image_name, image)
            self.emit(SIGNAL("display_image(QString)"), image_name)

        self.emit(SIGNAL("display_image(QString)"), image_name)

    def stop(self):
        """Method that happens if the Stop button is pressed, which terminates the QThread"""

        # Toggle the relevant flags to stop running loops
        self.single_flag = False
        self.run_flag = False
