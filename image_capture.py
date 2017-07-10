# Import external libraries
import os
import json
import time
import cv2
import pypylon
import serial
from PyQt4.QtCore import QThread, SIGNAL


class ImageCapture(QThread):
    """Tertiary module used to capture images
    Images are acquired through one of three methods depending on the raised flags
    If simulation_flag, images are acquired from a set samples folder and emitted back to the function caller
    If single, only one image is acquired, saved and emitted back to the function caller
    If run, the while loop waits indefinitely till a serial trigger is detected
    It then acquires and saves the image, then sleeps for a predefined time until the next trigger is allowed
    """

    def __init__(self, save_folder, simulation_flag=False, single_flag=False, run_flag=False):

        # Defines the class as a thread
        QThread.__init__(self)

        # Loads configuration settings from respective .json file
        self.acquire_settings()

        # Save respective values and flags to be used in this method
        self.save_folder = save_folder
        self.simulation_flag = simulation_flag
        self.single_flag = single_flag
        self.run_flag = run_flag

        # Checks if the save folder location has a scan, coat and single folder
        # If not, create them
        try:
            os.mkdir('%s\coat' % self.save_folder)
        except:
            pass
        try:
            os.mkdir('%s\scan' % self.save_folder)
        except:
            pass
        try:
            os.mkdir('%s\single' % self.save_folder)
        except:
            pass

        # For the CurrentPhase, 0 corresponds to Coat, 1 corresponds to Scan
        self.current_layer = self.config['CurrentLayer']
        self.current_phase = self.config['CurrentPhase']
        self.capture_count = self.config['CaptureCount']
        self.phases = ['coat', 'scan']

        # Settings for combo box selections are saved as a list of strings which can be modified here
        self.pixel_format_list = ['Mono8', 'Mono12', 'Mono12Packed']

    def run(self):

        # Simulation Flag
        if self.simulation_flag:
            self.acquire_image_simulation()
        else:
            self.emit(SIGNAL("update_status(QString)"), 'Capturing Image(s)...')
            self.acquire_settings()
            self.acquire_camera()
            self.acquire_trigger()

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

            # Run Flag
            while self.run_flag:
                self.emit(SIGNAL("update_status(QString)"), 'Waiting for trigger.')
                self.acquire_image_run()

            # Close the camera when done using it
            self.camera.close

            # Save the current layer and current phase to the config.json file so it can be continued
            self.config['CurrentLayer'] = self.current_layer
            self.config['CurrentPhase'] = self.current_phase

            with open('config.json', 'w+') as config:
                json.dump(self.config, config)

    def acquire_camera(self):
        """Accesses the pypylon wrapper and checks the ethernet ports for a connected camera
        Returns True if found, else False
        Also creates the camera variable
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
        """Accesses the COM ports on the computer for an attached USB2 device
        Queries a range of ports until it finds one, then reports the serial trigger back
        """

        # Creates a list of COM1, COM2 etc.
        ports = ['COM%s' % i for i in xrange(1, 10)]

        # Checks through all the COM ports for an available connected trigger device
        for port in ports:
            try:
                # Open the COM port
                # 9600 is the baud rate
                self.serial_trigger = serial.Serial(port, 9600, timeout=1)
                self.serial_trigger_read = self.serial_trigger.readline().strip()

                # The Arduino has been programmed to send back tildes by default
                if '~' in self.serial_trigger_read:
                    return port
                else:
                    self.serial_trigger.close()
            except (OSError, serial.SerialException, serial.SerialTimeoutException):
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

    def acquire_image_simulation(self):
        """Acquire image(s) from a specified folder (samples)"""

        self.emit(SIGNAL("update_status(QString)"), 'Acquiring Images...')

        # Load the sample scan and coat images
        self.raw_image_scan = cv2.imread('samples/sample_scan.png')
        self.emit(SIGNAL("update_status(QString)"), 'Acquired scan image.')
        self.emit(SIGNAL("update_progress(QString)"), '50')

        self.raw_image_coat = cv2.imread('samples/sample_coat.png')
        self.emit(SIGNAL("update_status(QString)"), 'Acquired coat image.')
        self.emit(SIGNAL("update_progress(QString)"), '100')

        # Emit the read images back to main_window.py for processing
        self.emit(SIGNAL("initialize_3(PyQt_PyObject, PyQt_PyObject)"), self.raw_image_scan, self.raw_image_coat)
        #self.emit(SIGNAL("update_layer(QString, QString)"), str(self.start_layer), str(self.start_phase))

    def acquire_image_single(self):
        """Acquire single image from the camera"""

        # Grab the image from the camera
        image = next(self.camera.grab_images(1))

        # Emit the captured image back to wherever uses it
        # self.emit(SIGNAL("initialize_3(PyQt_PyObject)"), image)



        # Save the image to the selected save folder
        file_name = str(self.save_folder) + '/single/image_capture_' + str(self.config['CaptureCount']) + '.png'
        cv2.imwrite(str(self.save_folder) + '/single/image_capture_' + str(self.config['CaptureCount']) + '.png', image)

        self.emit(SIGNAL("send_image(PyQt_PyObject, QString)"), image, str(file_name))

        # Update the capture counter which will be saved to the config.json file
        self.config['CaptureCount'] += 1
        self.emit(SIGNAL("update_status(QString)"), 'Image saved.')

    def acquire_image_run(self):
        """Acquire multiple images from the camera when trigger is detected"""

        # Read from the serial interface
        self.trigger = self.serial_trigger.readline().strip()

        if self.trigger == 'TRIG':

            self.emit(SIGNAL("update_status(QString)"), 'Trigger Detected. Capturing image.')

            try:
                image = next(self.camera.grab_images(1))
            except RuntimeError:
                time.sleep(2)
                image = next(self.camera.grab_images(1))

            # Save the image to the selected save folder in the respective scan or coat folder
            cv2.imwrite(str(self.save_folder) + '/' + self.phases[self.current_phase] + '/image_' +
                        self.phases[self.current_phase] + '_' + str(int(self.current_layer)) + '.png', image)

            self.emit(SIGNAL("send_image(PyQt_PyObject)"), image)

            # If used to suppress the status update if the Stop button is pressed
            if self.run_flag:
                self.emit(SIGNAL("update_status(QString)"), 'Image saved. Timeout in progress...')

            # Increment the layer every second image, and toggle the phase
            self.current_layer += 0.5
            self.current_phase = (self.current_phase + 1) % 2

            # Disallow triggering for additional images for however many seconds and reset the trigger flag
            time.sleep(self.config['TriggerTimeout'])
            self.serial_trigger.reset_input_buffer()

    def stop(self):
        """This block happens if the Stop button is pressed, which terminates the QThread"""

        # Toggle the relevant flags to stop running loops
        self.single_flag = False
        self.run_flag = False