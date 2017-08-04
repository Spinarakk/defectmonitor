# Import external libraries
import json
import cv2
import numpy as np
from PyQt4.QtCore import QThread, SIGNAL


class ImageCorrection(QThread):
    """Module used to correct the raw (or any sent) images taken by the camera for various optical related issues
    Processed images to then be scanned for any particular defects using the DefectDetection module
    Applies the following OpenCV processes in order:
    Distortion Correction (D)
    Perspective Warp (P)
    Crop (C)
    Following methods also available if required:
    Rotate (R)
    CLAHE (E)
    """

    def __init__(self, image):

        # Defines the class as a thread
        QThread.__init__(self)

        # Load configuration settings from config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Store received arguments as instance variables
        self.image = image

        # Initiate a list to store all the camera parameters
        self.camera_parameters = []

        # Load camera parameters from specified calibration file
        with open('%s' % self.config['CalibrationFile']) as camera_parameters:
            for line in camera_parameters.readlines():
                self.camera_parameters.append(line.split(' '))

        # Split camera parameters into their own respective values to be used in OpenCV functions
        self.camera_matrix = np.array(self.camera_parameters[1:4]).astype('float64')
        self.distortion_coefficients = np.array(self.camera_parameters[5]).astype('float64')
        self.homography_matrix = np.array(self.camera_parameters[7:10]).astype('float64')
        self.output_resolution = np.array(self.camera_parameters[11]).astype('int32')

        # Define lists containing the 2 image arrays, 2 phase strings, 3 processing tag strings and 3 status messages
        # if bool(image_folder):
        #     self.image_folder = image_folder + '/processed'
        #     self.images = (image_coat, image_scan)
        #     self.phases = ('coat', 'scan')
        #     self.tags = ('DP', 'DPC', 'DPCE')
        #     self.status_messages = ('Fixing Distortion & Perspective...', 'Cropping images...',
        #                             'Applying CLAHE algorithm...')
        #     self.progress_counter = 0.0

    def run(self):
        self.image_D = self.distortion_fix(self.image)
        self.image_DP = self.perspective_fix(self.image_D)
        self.image_DPC = self.crop(self.image_DP)
        self.image_DPCE = self.clahe(self.image_DPC)

    def distortion_fix(self, image):
        """Fixes the barrel/pincushion distortion commonly found in pinhole cameras"""

        # Store the camera's intrinsic values as a 2x2 matrix
        camera_matrix = self.camera_matrix
        camera_matrix[0, 2] = image.shape[1] / 2.0  # Half image width
        camera_matrix[1, 2] = image.shape[0] / 2.0  # Half image height

        # OpenCV distortion fix function
        try:
            image = cv2.undistort(image, camera_matrix, self.distortion_coefficients)
            return image
        except:
            print 'Image Distortion fix failed.'
            return False

    def perspective_fix(self, image):
        """Fixes the perspective warp due to the off-centre position of the camera"""

        try:
            image = cv2.warpPerspective(image, self.homography_matrix, tuple(self.output_resolution))
            return image
        except:
            print 'Image Perspective Fix failed.'
            return False

    def crop(self, image):
        """Crops the image to a more desirable region of interest"""

        # Save value to be used to determine region of interest
        crop_boundary = self.config['CropBoundary']

        # Crop the image to a rectangle region of interest as dictated by the following values [H,W]
        image = image[crop_boundary[0]: crop_boundary[1], crop_boundary[2]: crop_boundary[3]]

        return image

    def rotate(self, image):
        """Rotate the image"""

        # Save value to be used to determine rotation amount
        rotation_angle = self.config['RotationAngle']

        # Rotate the image by creating and using a 2x3 rotation matrix
        rotation_matrix = cv2.getRotationMatrix2D((image.shape[1] / 2, image.shape[0] / 2), rotation_angle, 1.0)
        image = cv2.warpAffine(image, rotation_matrix, (image.shape[1], image.shape[0]))

        return image

    @staticmethod
    def clahe(image):
        """
        Applies a Contrast Limited Adaptive Histogram Equalization to the image
        Used to improve the contrast of the image to make it clearer/visible
        """

        # Algorithm requires the image to be in grayscale colorspace to function
        # This line checks if the image is already grayscale or in RGB (BGR)
        rgb_flag = len(image.shape)
        if (rgb_flag == 3):
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # CLAHE filter functions
        clahe_filter = cv2.createCLAHE(8.0, (64, 64))
        image = clahe_filter.apply(image)

        # Convert the image back to RGB (BGR) as when converting to a pixmap, grayscale images don't work
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        return image


class DefectDetection(QThread):
    """Module used to process the corrected images using OpenCV to detect a variety of different defects
    Defects as outlined in the README.txt file
    PUT ALL OPENCV CODE TO BE TESTED HERE IN ONE OF THE FIVE METHODS
    TRY NOT TO MODIFY TOO MUCH OF THE CODE OUTSIDE OF THESE METHODS
    """

    def __init__(self, image_raw):
        # Defines the class as a thread
        QThread.__init__(self)

        # Save the received argument as an instance variable
        self.original_image = image_raw

    def run(self):
        self.emit(SIGNAL("update_progress(QString)"), '0')

        self.emit(SIGNAL("update_status(QString)"), 'Running OpenCV Process 1...')
        self.image_1 = self.test_code_1(self.original_image)
        self.emit(SIGNAL("update_progress(QString)"), '20')

        self.emit(SIGNAL("update_status(QString)"), 'Running OpenCV Process 2...')
        self.image_2 = self.test_code_2(self.original_image)
        self.emit(SIGNAL("update_progress(QString)"), '40')

        self.emit(SIGNAL("update_status(QString)"), 'Running OpenCV Process 3...')
        self.image_3 = self.test_code_3(self.original_image)
        self.emit(SIGNAL("update_progress(QString)"), '60')

        self.emit(SIGNAL("update_status(QString)"), 'Running OpenCV Process 4...')
        self.image_4 = self.test_code_4(self.original_image)
        self.emit(SIGNAL("update_progress(QString)"), '80')

        self.emit(SIGNAL("update_status(QString)"), 'Running OpenCV Process 5...')
        self.image_5 = self.test_code_5(self.original_image)
        self.emit(SIGNAL("update_progress(QString)"), '100')

        self.emit(SIGNAL("defect_processing_finished(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject, PyQt_PyObject, "
                         "PyQt_PyObject)"), self.image_1, self.image_2, self.image_3, self.image_4, self.image_5)

    @staticmethod
    def test_code_1(image):
        processed_image = cv2.bilateralFilter(image, 9, 75, 75)
        return processed_image

    @staticmethod
    def test_code_2(image):
        processed_image = cv2.erode(image, (5, 5))
        return processed_image

    @staticmethod
    def test_code_3(image):
        processed_image = cv2.blur(image, (10, 10))
        return processed_image

    @staticmethod
    def test_code_4(image):
        kernel = np.ones((5, 5), np.float32) / 25
        processed_image = cv2.filter2D(image, -1, kernel)
        return processed_image

    @staticmethod
    def test_code_5(image):
        rows, columns, _ = image.shape
        rotation_matrix = cv2.getRotationMatrix2D((columns / 2, rows / 2), 90, 1)
        processed_image = cv2.warpAffine(image, rotation_matrix, (columns, rows))
        return processed_image
