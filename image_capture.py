# Import external libraries
import json
import time
import cv2
import pypylon
import serial
import serial.tools.list_ports


class ImageCapture:
    """Module used to capture images from the connected Basler Ace acA3800-10gm GigE camera if attached"""

    def acquire_camera(self):
        """Accesses the pypylon wrapper and checks the ethernet ports for a connected camera
        Creates the camera object and returns camera information if found, else False is returned
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
        Returns the COM port if attached triggering device is found, else False is returned
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

        with open('build.json') as build:
            self.build = json.load(build)

        with open('config.json') as config:
            self.config = json.load(config)

        # For current_phase, 0 corresponds to Coat, 1 corresponds to Scan
        self.current_layer = self.build['ImageCapture']['Layer']
        self.current_phase = self.build['ImageCapture']['Phase']
        self.snapshot_layer = self.build['ImageCapture']['Snapshot']
        self.phases = ['coat', 'scan']

        # Settings for combo box selections are saved and accessed as a list of strings which can be modified here
        self.pixel_format_list = ['Mono8', 'Mono12', 'Mono12Packed']

        # These properties are changeable through the UI
        self.camera.properties['PixelFormat'] = self.pixel_format_list[self.config['CameraSettings']['PixelFormat']]
        self.camera.properties['GainRaw'] = self.config['CameraSettings']['Gain']
        self.camera.properties['BlackLevelRaw'] = self.config['CameraSettings']['BlackLevel']
        self.camera.properties['ExposureTimeAbs'] = self.config['CameraSettings']['ExposureTime']
        self.camera.properties['GevSCPSPacketSize'] = self.config['CameraSettings']['PacketSize']
        self.camera.properties['GevSCPD'] = self.config['CameraSettings']['InterPacketDelay']
        self.camera.properties['GevSCFTD'] = self.config['CameraSettings']['FrameDelay']

        # These properties are here to override the camera's 'default' and can be changed here
        self.camera.properties['TriggerSelector'] = 'AcquisitionStart'
        self.camera.properties['TriggerMode'] = 'Off'
        self.camera.properties['TriggerSource'] = 'Line1'
        self.camera.properties['TriggerActivation'] = 'RisingEdge'
        self.camera.properties['AcquisitionFrameRateEnable'] = 'False'
        self.camera.properties['AcquisitionFrameCount'] = 1

    def acquire_image_snapshot(self, status_camera, name):
        """Acquire a snapshot image from the camera"""

        status_camera.emit('Capturing')

        # Acquire and open the camera and apply the entered settings to it
        self.acquire_camera()
        self.camera.open()
        self.apply_settings()

        # Grab the image from the camera, error checking in case image capture fails
        try:
            image = next(self.camera.grab_images(1))
        except RuntimeError:
            status_camera.emit('Error')
        else:
            # Construct the image name using the current layer
            image_name = '%s/raw/snapshot/snapshotR_%s.png' % (self.build['BuildInfo']['Folder'],
                                                           str(self.snapshot_layer).zfill(4))

            # Save the raw image to the snapshot folder
            cv2.imwrite(image_name, image)

            # Increment the capture counter
            self.snapshot_layer += 1

            # Emit a status message and the image name to the Main Window, which will continue to process the image
            status_camera.emit('Image Saved')
            name.emit(image_name)
        finally:
            # Close the camera and save any changed counters to the build.json file
            self.camera.close()
            self.save_settings()

    def acquire_image_run(self, status_camera, status_trigger, name):
        """Acquire an image from the camera when trigger is detected, and sleep for a certain amount of time"""

        status_camera.emit('Capturing...')
        status_trigger.emit('Detected')

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

        # Construct the image name using the current layer and phase
        image_name = '%s/raw/%s/%sR_%s.png' % (self.build['BuildInfo']['Folder'], self.phases[self.current_phase],
                                               self.phases[self.current_phase], str(int(self.current_layer)).zfill(4))

        # Save the raw image to the appropriate folder
        cv2.imwrite(image_name, image)

        # Emit a status message and the image name to the Main Window, which will continue to process the image
        status_camera.emit('Image Saved')

        # Do not process the first scan image however
        if self.current_layer >= 1:
            name.emit(image_name)

        # Loop used to delay triggering for additional images for however many seconds
        # Also displays remaining timeout on the status bar
        for seconds in range(self.config['CameraSettings']['TriggerTimeout'], 0, -1):
            status_trigger.emit('Timeout: %ss' % seconds)
            time.sleep(1)

        # Increment the layer (by 1) every second image, and toggle the phase
        self.current_layer += 0.5
        self.current_phase = (self.current_phase + 1) % 2

        # Close the camera and save any changed counters to the build.json file
        self.camera.close()
        self.save_settings()

    def save_settings(self):
        """Save the current build's layer numbers to the build.json file"""

        self.build['ImageCapture']['Layer'] = self.current_layer
        self.build['ImageCapture']['Phase'] = self.current_phase
        self.build['ImageCapture']['Snapshot'] = self.snapshot_layer

        with open('build.json', 'w+') as build:
            json.dump(self.build, build, indent=4, sort_keys=True)
