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

    def __init__(self, queue1, storage_folder, simulation=False):

        # Defines the class as a thread
        QThread.__init__(self)

        # Loads configuration settings from respective .json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Save respective values to be used in this method
        self.queue1 = queue1
        self.storage_folder = storage_folder
        self.simulation = simulation
        self.start_layer = self.config['StartLayer']
        self.start_phase = self.config['StartPhase']

        # Determine the current layer number of the current scan or coat image being captured
        push_offset = 1
        self.push_counter = 2 * self.start_layer

        if self.start_phase == 'coat':
            self.push_counter += push_offset

    def run(self):

        # self.emit(SIGNAL("update_status(QString)"), 'Pylon %s' % pypylon.pylon_version.version)

        # At the current moment, because simulations are being run, this entire module only does the following
        if self.simulation:
            self.emit(SIGNAL("update_status(QString)"), 'Acquiring Images...')
            self.acquire_image(self.simulation)
        else:
            self.acquire_cameras()
            if bool(self.camera1):
                self._camera_settings()
                self.acquire_image()

    def acquire_cameras(self):
        self.available_cameras = pypylon.factory.find_devices()

        if not bool(self.available_cameras):
            self.emit(SIGNAL("update_status(QString)"), 'No cameras available...')
            return False
        else:
            self.camera1 = pypylon.factory.create_device(self.available_cameras[0])
            self.camera1.open()
            self.emit(SIGNAL("update_status(QString)"), 'Acquired %s.' % self.camera1.device_info)

    def acquire_image(self, simulation=False):
        """Acquire images from the camera(s)
        If simulation flag is true, images are read from the samples folder
        """

        if simulation:
            self.raw_image_scan = cv2.imread('samples/sample_scan.png')
            self.emit(SIGNAL("update_status(QString)"), 'Acquired scan image.')
            self.emit(SIGNAL("update_progress(QString)"), '50')

            self.raw_image_coat = cv2.imread('samples/sample_coat.png')
            self.emit(SIGNAL("update_status(QString)"), 'Acquired coat image.')
            self.emit(SIGNAL("update_progress(QString)"), '100')
        else:
            raw_image = next(self.camera1.grab_images)

        # Emit the read images back to main_window.py for processing
        self.emit(SIGNAL("initialize_3(PyQt_PyObject, PyQt_PyObject)"), self.raw_image_scan, self.raw_image_coat)
        self.emit(SIGNAL("update_layer(QString, QString)"), str(self.start_layer), str(self.start_phase))

        while True:
            if simulation:
                break
            time.sleep(0.1)
            trigger = self.serial_trig.readline().strip()

            if trigger == 'TRIG':
                image = next(self.camera1.grab_images(1))
                print self.push_counter
                if self.push_counter % 2:
                    save_folder = self.storage_folder['coat']
                    self.start_phase = 'coat'
                    layer = str((self.push_counter - 1) / 2).zfill(5)
                    cv2.imwrite(save_folder + '/' + layer + '.png', image)

                else:
                    save_folder = self.storage_folder['scan']
                    self.start_phase = 'scan'
                    layer = str(self.push_counter / 2).zfill(5)
                    cv2.imwrite(save_folder + '/' + layer + '.png', image)

                self.push_image(image, self.start_phase)
                self.emit(SIGNAL("update_layer(QString)"), '%s_%s' % (layer, self.start_phase))
                self.config['StartPhase'] = self.start_phase
                self.config['StartLayer'] = layer

                with open('config.json', 'w+') as config:
                    json.dump(self.config, config)

                if self.stop:
                    self.queue1.put_nowait((None, None))
                    break

    def push_image(self, image, phase):

        self.queue1.put_nowait((image, self.push_counter, phase))
        self.push_counter += 1


    
    def _serial_interface(self):
        ports = ['com%s' % number for number in xrange(1, 10)]
        for port in ports:
            try:
                ser = serial.Serial(port, 9600)
                self.serial_trig = ser
                init_read = self.serial_trig.readline().strip()
                if '~' in init_read:
                    self.emit(SIGNAL("update_status(QString)"), 'Hardware trigger detected.')
                    return True
                else:
                    ser.close()
            except (OSError, serial.SerialException, serial.SerialTimeoutException):
                pass

        return False
    
    def _camera_settings(self):
        if bool(self.available_cameras):
            self.camera1.properties['PixelFormat'] = 'Mono12'  # 12 bit (4096 level) monochrome
            # self.camera2.properties['PixelFormat'] = 'Mono8'
            self.camera1.properties['AcquisitionMode'] = 'SingleFrame'
            # self.camera2.properties['AcquisitionMode'] = 'SingleFrame'
            self.camera1.properties['TriggerSelector'] = 'AcquisitionStart'  # Select AcquisitionStart Trigger
            # self.camera2.properties['TriggerSelector'] = 'AcquisitionStart'
            self.camera1.properties['TriggerMode'] = 'Off'  # software acquisition
            # self.camera2.properties['TriggerMode']= 'Off'
            self.camera1.properties['AcquisitionFrameRateEnable'] = 'False'
            # self.camera2.properties['AcquisitionFrameRateEnable'] = 'False'
            self.camera1.properties['TriggerSelector'] = 'FrameStart'  # Select FrameStart Trigger
            # self.camera2.properties['TriggerSelector']= 'FrameStart'
            # trig_present = self._serial_interface()
            # if not trig_present:
            #     self.stop = True
            #     print 'No triggering device found',
            #     return False

            # if hwfstrig:
            #     self.camera1.properties['TriggerMode'] = 'On'  # For hardware frame start triggering
            # self.camera2.properties['TriggerMode']= 'On'
            self.camera1.properties['TriggerSource'] = 'Line1'
            # self.camera2.properties['TriggerSource'] = 'Line1'
            self.camera1.properties['TriggerActivation'] = 'RisingEdge'
            # self.camera2.properties['TriggerActivation'] = 'RisingEdge'
            self.camera1.properties['ExposureMode'] = 'Timed'
            # self.camera2.properties['ExposureMode'] = 'Timed'
            self.camera1.properties['ExposureTimeAbs'] = 23000.0
            # self.camera2.properties['ExposureTimeAbs']=35000.0
            self.camera1.properties['AcquisitionFrameCount'] = 1  # Number of frames to grab
            # self.camera2.properties['AcquisitionFrameCount'] = 1
            self.camera1.properties['GevSCPSPacketSize'] = 500
            # self.camera2.properties['GevSCPSPacketSize'] = 500
            self.camera1.properties['GevSCPD'] = 6900  # Inter-packet delay
            # self.camera2.properties['GevSCPD'] = 6900
            self.camera1.properties['GevSCFTD'] = 1000  # Frame transfer delay
            # self.camera2.properties['GevSCFTD'] = 1000
            self._camera_calibration()
        else:
            self.stop = True
            return False
        