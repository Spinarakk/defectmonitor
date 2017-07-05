"""
image_capture.py
Module to capture images from the camera, and change camera settings
Also calibrates the camera and acquires its intrinsic values
"""
import json
import time

import cv2
import pypylon
import serial

from PyQt4.QtCore import QThread, SIGNAL

class ImageCapture(QThread):

    def __init__(self, save_folder, single_mode=False, simulation=False):
        """Note: Current setup assumes that all builds and runs will start from """

        # Defines the class as a thread
        QThread.__init__(self)

        # Loads configuration settings from respective .json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Save respective values to be used in this method
        self.save_folder = save_folder
        self.single_mode = single_mode
        self.simulation = simulation

        # Note: For the CurrentPhase, 0 corresponds to Coat, 1 corresponds to Scan
        self.current_layer = self.config['CurrentLayer']
        self.current_phase = self.config['CurrentPhase']
        self.capture_count = self.config['CaptureCount']
        self.phases = ['coat', 'scan']

        # Settings for combo box selections are saved as a list of strings which can be modified here
        self.pixel_format_list = ['Mono8', 'Mono12', 'Mono12Packed']
        self.trigger_selector_list = ['AcquisitionStart', 'FrameStart']
        self.trigger_mode_list = ['Off', 'On']
        self.trigger_source_list = ['TriggerSoftware', 'Line1', 'Action1']
        self.trigger_activation_list = ['RisingEdge', 'FallingEdge']

    def run(self):
        """Runs the following methods in order"""
        if not self.simulation:
            self.emit(SIGNAL("update_status(QString)"), 'Capturing Image(s)...')
            self.acquire_settings()
            self.acquire_camera()
            self.acquire_trigger()
        self.capture_images()

    def acquire_camera(self):
        """Accesses the pypylon wrapper and checks the ethernet ports for a connected camera
        Returns True if found, else False
        Also creates the camera variable
        """

        self.available_camera = pypylon.factory.find_devices()
        self.camera = pypylon.factory.create_device(self.available_camera[0])

        if bool(self.available_camera):
            return self.camera.device_info
        else:
            return False

    def acquire_trigger(self):
        """Accesses the COM ports on the computer for an attachhed USB2 device
        Queries a range of ports until it finds one, then reports the serial trigger back
        """

        # Creates a list of COM1, COM2 etc.
        ports = ['COM%s' % i for i in xrange(1, 10)]

        for port in ports:
            try:
                # 9600 is the baud rate
                self.serial_trigger = serial.Serial(port, 9600)
                self.serial_trigger_read = self.serial_trigger.readline().strip()
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
        """Applies the stored camera settings to the connected camera
        Because the settings are saved as an index value, and the pylon wrapper only accepts strings for some properties
        The strings are saved in their respective lists and the index is used to call the respective one
        """
        self.camera.properties['PixelFormat'] = self.pixel_format_list[self.config['PixelFormat']]
        self.camera.properties['TriggerSelector'] = self.trigger_selector_list[self.config['TriggerSelector']]
        self.camera.properties['TriggerMode'] = self.trigger_mode_list[self.config['TriggerMode']]
        self.camera.properties['TriggerSource'] = self.trigger_source_list[self.config['TriggerSource']]
        self.camera.properties['TriggerActivation'] = self.trigger_activation_list[self.config['TriggerActivation']]
        self.camera.properties['ExposureTimeAbs'] = self.config['ExposureTimeAbs']
        self.camera.properties['AcquisitionFrameCount'] = self.config['AcquisitionFrameCount']

    def capture_images(self):
        """Acquire images from the camera(s)
        If simulation flag is true, images are read from the samples folder
        If single mode flag is true, only one image is captured and saved
        Otherwise, the while loop runs indefinitely and captures images when the trigger device is triggered
        """

        if self.simulation:

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
            self.emit(SIGNAL("update_layer(QString, QString)"), str(self.start_layer), str(self.start_phase))
        else:
            # Opens up the camera and sends it the stored settings to be used for capturing images
            self.camera.open()
            self.apply_settings()

            if self.single_mode:

                # Grab the image from the camera
                image = next(self.camera.grab_images(1))

                # Emit the captured image back to wherever uses it
                #self.emit(SIGNAL("initialize_3(PyQt_PyObject)"), image)

                # Save the image to the selected save folder
                cv2.imwrite(str(self.save_folder) + '/image_capture_' + str(self.config['CaptureCount']) + '.png', image)

                # Update the image capture counter and save it to the config.json file
                self.config['CaptureCount'] += 1
                with open('config.json', 'w+') as config:
                    json.dump(self.config, config)

                self.camera.close()

                self.emit(SIGNAL("update_status(QString)"), 'Image Captured.')

            else:
                # This block of code runs when the Run button is pressed and continuous indefinitely
                while True:

                    # Slows down the loop slightly
                    time.sleep(0.1)

                    self.trigger = self.serial_trigger.readline().strip()

                    if self.trigger == 'TRIG':
                        try:
                            image = next(self.camera.grab_images(1))
                        except(RuntimeError):
                            time.sleep(2)
                            image = next(self.camera.grab_images(1))

                        # Save the image to the selected save folder
                        cv2.imwrite(str(self.save_folder) + '/image_' + self.phases[self.current_phase] +
                                    '_' + str(int(self.current_layer)) + '.png', image)

                        # Increment the layer every second image, and toggle the phase
                        self.current_layer += 0.5
                        self.current_phase = (self.current_phase + 1) % 2

                        # Disallow additional pictures for 3 seconds and reset the trigger flag
                        time.sleep(3)

    def terminate(self):
        """This block happens if the Stop button is pressed, which terminates the QThread
        Writes the saved config values to the config.json file
        """
        self.camera.close()

        self.config['CurrentLayer'] = self.current_layer
        self.config['CurrentPhase'] = self.current_phase

        with open('config.json', 'w+') as config:
            json.dump(self.config, config)