# Import external libraries
import json
import time
import cv2
import pypylon
import serial
import serial.tools.list_ports

# Import related modules
import image_processing


class ImageCapture:
    """Module used to capture images from the connected Basler Ace acA3800-10gm GigE camera if attached"""

    def __init__(self):

        # Load configuration settings from config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # For current_phase, 0 corresponds to Coat, 1 corresponds to Scan
        self.current_layer = self.config['ImageCapture']['Layer']
        self.current_phase = self.config['ImageCapture']['Phase']
        self.single_layer = self.config['ImageCapture']['Single']
        self.phases = ['coat', 'scan']

        # Settings for combo box selections are saved and accessed as a list of strings which can be modified here
        self.pixel_format_list = ['Mono8', 'Mono12', 'Mono12Packed']

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
        """Grabs a list of all the available COM ports on the current computer
        Returns the COM port if attached triggering device is found, else False
        """

        # List all the available serial ports
        port_list = list(serial.tools.list_ports.comports())

        # Check the list for the port description that matches the trigger being used
        for port in port_list:
            if 'CH340' in port.description:

                # Open the COM port with a baud rate of 9600 and a 1 second timeout
                self.serial_trigger = serial.Serial(port.device, 9600, timeout=1)

                try:
                    # Read the serial line
                    self.serial_trigger_read = str(self.serial_trigger.readline())
                except (OSError, serial.SerialException):
                    return False

                self.serial_trigger.close()

                # The Arduino has been programmed to send back tildes by default
                if '~' in self.serial_trigger_read:
                    return port.device

        # Return false if the specific trigger device isn't found at all
        return False

    def apply_settings(self):
        """Applies the stored camera settings from the config.json file to the connected camera
        Some settings are saved as an index value as the pylon wrapper only accepts strings for some properties
        The strings are saved in their respective lists and the index is used to call the respective one
        """

        # These properties are changeable through the UI
        self.camera.properties['PixelFormat'] = self.pixel_format_list[self.config['CameraSettings']['PixelFormat']]
        self.camera.properties['ExposureTimeAbs'] = self.config['CameraSettings']['ExposureTimeAbs']
        self.camera.properties['GevSCPSPacketSize'] = self.config['CameraSettings']['PacketSize']
        self.camera.properties['GevSCPD'] = self.config['CameraSettings']['InterPacketDelay']
        self.camera.properties['GevSCFTD'] = self.config['CameraSettings']['FrameTransmissionDelay']

        # These properties are here to override the camera's 'default' and can be changed here
        self.camera.properties['TriggerSelector'] = 'AcquisitionStart'
        self.camera.properties['TriggerMode'] = 'Off'
        self.camera.properties['TriggerSource'] = 'Line1'
        self.camera.properties['TriggerActivation'] = 'RisingEdge'
        self.camera.properties['AcquisitionFrameRateEnable'] = 'False'
        self.camera.properties['AcquisitionFrameCount'] = 1

    def acquire_image_single(self, status, layer, phase):
        """Acquire a single image from the camera"""

        status.emit('Capturing single image...')

        # Acquire and open the camera and apply the entered settings to it
        self.acquire_camera()
        self.camera.open()
        self.apply_settings()

        # Grab the image from the camera, error checking in case image capture fails
        try:
            image = next(self.camera.grab_images(1))
        except RuntimeError:
            status.emit('Error grabbing image. Please try again.')
        else:
            # Save the raw image to the single folder
            cv2.imwrite('%s/raw/single/image_single_%s.png' %
                        (self.config['ImageCapture']['Folder'], str(self.single_layer).zfill(4)), image)

            status.emit('Processing captured image...')

            # # Process the image
            # image = image_processing.ImageCorrection().apply_fixes(image)
            #
            # # Save the processed image to the processed folder
            # cv2.imwrite('%s/processed/single/image_single_processed_%s.png' %
            #             (self.config['ImageCapture']['Folder'], str(self.single_layer).zfill(4)), image)

            # Increment the capture counter
            self.single_layer += 1
            status.emit('Image captured.')
        finally:
            # Close the camera and save any changed counters to the config.json file
            self.camera.close()
            self.save_settings()

    def acquire_image_run(self, status, layer, phase):
        """Acquire an images from the camera when trigger is detected, and sleep for a certain amount of time"""

        status.emit('Trigger detected. Capturing image...')

        # Acquire and open the camera and apply the entered settings to it
        self.acquire_camera()
        self.camera.open()
        self.apply_settings()

        # Grab the image from the camera, error checking in case image capture fails
        try:
            image = next(self.camera.grab_images(1))
        except RuntimeError:
            time.sleep(1)
            image = next(self.camera.grab_images(1))

        # Save the raw image to the single folder
        cv2.imwrite('%s/raw/%s/image_%s_%s.png' %
                    (self.config['ImageCapture']['Folder'], self.phases[self.current_phase],
                     self.phases[self.current_phase], str(int(self.current_layer)).zfill(4)), image)

        status.emit('Processing captured image...')

        # # Process the image
        # image = image_processing.ImageCorrection().apply_fixes(image)
        #
        # # Save the processed image to the processed folder
        # cv2.imwrite('%s/processed/%s/image_%s_processed_%s.png' %
        #             (self.config['ImageCapture']['Folder'], self.phases[self.current_phase],
        #              self.phases[self.current_phase], str(int(self.current_layer)).zfill(4)), image)

        # Loop used to delay triggering for additional images for however many seconds
        # Also displays remaining timeout on the status bar
        for seconds in range(self.config['ImageCapture']['TriggerTimeout'], 0, -1):
            status.emit('Image saved. %s second timeout...' % seconds)
            time.sleep(1)

        # Increment the layer (by 1) every second image, and toggle the phase
        self.current_layer += 0.5
        self.current_phase = (self.current_phase + 1) % 2

        # Close the camera and save any changed counters to the config.json file
        self.camera.close()
        self.save_settings()

    def save_settings(self):

        self.config['ImageCapture']['Layer'] = self.current_layer
        self.config['ImageCapture']['Phase'] = self.current_phase
        self.config['ImageCapture']['Single'] = self.single_layer

        with open('config.json', 'w+') as config:
            json.dump(self.config, config, indent=4, sort_keys=True)