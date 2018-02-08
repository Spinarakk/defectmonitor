# Import external libraries
import time
import cv2
import pypylon
import serial
import serial.tools.list_ports


class ImageCapture:
    """Module used to capture images from the connected Basler Ace acA3800-10gm GigE camera if attached
    Also contains methods to look for an attached camera and trigger, and to apply settings to said camera
    """

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

    def apply_settings(self, settings):
        """Applies the stored camera settings from the received settings dictionary to the connected camera
        Some settings are saved as an index value as the pylon wrapper only accepts strings for some properties
        The strings are saved in their respective lists and the index is used to call the respective one
        """

        # Settings for combo box selections are saved and accessed as a list of strings which can be modified here
        self.pixel_format_list = ['Mono8', 'Mono12', 'Mono12Packed']

        # These properties are changeable through the UI
        self.camera.properties['PixelFormat'] = self.pixel_format_list[settings['PixelFormat']]
        self.camera.properties['GainRaw'] = settings['Gain']
        self.camera.properties['BlackLevelRaw'] = settings['BlackLevel']
        self.camera.properties['ExposureTimeAbs'] = settings['ExposureTime']
        self.camera.properties['GevSCPSPacketSize'] = settings['PacketSize']
        self.camera.properties['GevSCPD'] = settings['InterPacketDelay']
        self.camera.properties['GevSCFTD'] = settings['FrameDelay']

        # These properties are here to override the camera's 'defaults' and can be changed here
        self.camera.properties['TriggerSelector'] = 'AcquisitionStart'
        self.camera.properties['TriggerMode'] = 'Off'
        self.camera.properties['TriggerSource'] = 'Line1'
        self.camera.properties['TriggerActivation'] = 'RisingEdge'
        self.camera.properties['AcquisitionFrameRateEnable'] = 'False'
        self.camera.properties['AcquisitionFrameCount'] = 1

    def setup_camera(self, layer, settings, status_camera):
        """Acquire and open the camera and apply the received settings to it
        Contains error checking at every camera stage to make sure that the camera is able to be used
        """

        if not self.acquire_camera():
            status_camera.emit('Error 1')
            print('Layer: %s\nCamera failed to be acquired.' % layer)
            return False

        try:
            self.camera.open()
        except:
            status_camera.emit('Error 2')
            print('Layer: %s\nCamera failed to be opened.' % layer)
            return False
        else:
            self.apply_settings(settings)

        return True

    def capture_snapshot(self, layer, folder, settings, status_camera, name):
        """Capture and save a snapshot image from the camera"""

        status_camera.emit('Capturing')

        # Setup the camera while checking for any errors
        self.setup_camera(layer, settings, status_camera)

        # Grab the image from the camera, error checking in case image capture fails
        try:
            image = next(self.camera.grab_images(1))
        except RuntimeError:
            # Emit error messages, close the camera and return a false result
            status_camera.emit('Error 3')
            print('Layer: %s\nImage failed to be captured.' % layer)
            self.camera.close()
            return False
        else:
            # Construct the image name using the received layer and folder
            image_name = '%s/snapshotR_%s.png' % (folder, layer)

            # Save the raw image to the snapshot folder
            cv2.imwrite(image_name, image)

            # Emit a status message and the image name to the Main Window, which will continue to fix the image
            status_camera.emit('Image Saved')
            name.emit(image_name)

            # Close the camera and return a true result
            self.camera.close()
            return True

    def capture_run(self, layer, phase, folder, settings, status_camera, status_trigger, name):
        """Capture and  an image from the camera when trigger is detected, and sleep for a certain amount of time"""

        status_camera.emit('Capturing...')
        status_trigger.emit('Detected')

        # Setup the camera while checking for any errors
        self.setup_camera(layer, settings, status_camera)

        # Grab the image from the camera, error checking in case image capture fails
        try:
            image = next(self.camera.grab_images(1))
        except RuntimeError:
            # Emit error messages, close the camera and return a false result
            status_camera.emit('Error 3')
            print('Layer: %s\nImage failed to be captured.' % layer)
            self.camera.close()
            return False
        else:
            # Construct the image name using the received layer, phase and folder
            image_name = '%s/%s/%sR_%s.png' % (folder, phase, phase, layer)

            # Save the raw image to the corresponding folder
            cv2.imwrite(image_name, image)

            # Emit a status message and the image name to the Main Window, which will continue to process the image
            status_camera.emit('Image Saved')

            # Do not process the first scan image however
            if int(layer) >= 1:
                name.emit(image_name)

            # Loop used to delay triggering for additional images for however many seconds
            # Also displays remaining timeout on the status bar
            for seconds in range(settings['TriggerTimeout'], 0, -1):
                status_trigger.emit('Timeout: %ss' % seconds)
                time.sleep(1)

            # Close the camera and return a true result
            self.camera.close()
            return True
