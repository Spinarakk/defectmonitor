# Import external libraries
import os
import json
import cv2
import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class ImageCorrection:
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

    def __init__(self, test_flag=False):

        # Load configuration settings from config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Checks whether to use the temporary results of the camera calibration, or the ones saved in the config file
        if test_flag:
            with open('%s/calibration_results.json' % self.config['WorkingDirectory']) as camera_parameters:
                self.parameters = json.load(camera_parameters)
                self.parameters = self.parameters['ImageCorrection']
        else:
            self.parameters = self.config['ImageCorrection']

    def apply_fixes(self, image):
        """Applies the distortion, perspective and crop processes to the received image"""

        image = self.distortion_fix(image)
        image = self.perspective_fix(image)
        image = self.crop(image)

        return image

    def distortion_fix(self, image):
        """Fixes the barrel/pincushion distortion commonly found in pinhole cameras"""

        # Store the camera's intrinsic values as a 2x2 matrix
        camera_matrix = np.array(self.parameters['CameraMatrix'])
        camera_matrix[0, 2] = image.shape[1] / 2.0  # Half image width
        camera_matrix[1, 2] = image.shape[0] / 2.0  # Half image height

        # OpenCV distortion fix function
        try:
            image = cv2.undistort(image, camera_matrix, np.array(self.parameters['DistortionCoefficients']))
            return image
        except:
            print('Image Distortion fix failed.')
            return False

    def perspective_fix(self, image):
        """Fixes the perspective warp due to the off-centre position of the camera"""

        try:
            image = cv2.warpPerspective(image, np.array(self.parameters['HomographyMatrix']), tuple(self.parameters['Resolution']))
            return image
        except:
            print('Image Perspective Fix failed.')
            return False

    def crop(self, image):
        """Crops the image to a more desirable region of interest"""

        # Save value to be used to determine region of interest
        crop_boundary = self.config['ImageCorrection']['CropBoundary']

        # Crop the image to a rectangle region of interest as dictated by the following values [H,W]
        image = image[crop_boundary[0]: crop_boundary[1], crop_boundary[2]: crop_boundary[3]]

        return image

    def transform(self, image, transform):

        width = image.shape[1]
        height = image.shape[0]

        # Flip
        if transform[3]:
            image = cv2.flip(image, 1)
        if transform[4]:
            image = cv2.flip(image, 0)

        # Translation
        translation_matrix = np.float32([[1, 0, transform[1]], [0, 1, transform[0]]])
        image = cv2.warpAffine(image, translation_matrix, (width, height))

        # Rotation
        rotation_matrix = cv2.getRotationMatrix2D((width / 2, height / 2), transform[2], 1)
        image = cv2.warpAffine(image, rotation_matrix, (width, height))

        # Stretching
        # Top Left Corner
        points1 = np.float32([[width, 0], [0, 0], [0, height]])
        points2 = np.float32([[width, transform[5] + transform[12]],
                              [transform[8], transform[5]],
                              [transform[8] + transform[13], height + transform[7]]])
        matrix = cv2.getAffineTransform(points1, points2)
        image = cv2.warpAffine(image, matrix, (width, height))
        # Top Right Corner
        points1 = np.float32([[0, 0], [width, 0], [width, height]])
        points2 = np.float32([[0, transform[10]],
                              [width + transform[6], 0],
                              [width + transform[6] + transform[15], height + transform[7]]])
        matrix = cv2.getAffineTransform(points1, points2)
        image = cv2.warpAffine(image, matrix, (width, height))
        # Bottom Left Corner
        points1 = np.float32([[0, 0], [0, height], [width, height]])
        points2 = np.float32([[transform[9], 0], [0, height], [width, height + transform[16]]])
        matrix = cv2.getAffineTransform(points1, points2)
        image = cv2.warpAffine(image, matrix, (width, height))
        # Bottom Right Corner
        points1 = np.float32([[0, height], [width, height], [width, 0]])
        points2 = np.float32([[0, height + transform[14]], [width, height], [width + transform[11], 0]])
        matrix = cv2.getAffineTransform(points1, points2)
        image = cv2.warpAffine(image, matrix, (width, height))

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
        self.emit(pyqtSignal("update_progress(QString)"), '0')

        self.emit(pyqtSignal("update_status(QString)"), 'Running OpenCV Process 1...')
        self.image_1 = self.test_code_1(self.original_image)
        self.emit(pyqtSignal("update_progress(QString)"), '20')

        self.emit(pyqtSignal("update_status(QString)"), 'Running OpenCV Process 2...')
        self.image_2 = self.test_code_2(self.original_image)
        self.emit(pyqtSignal("update_progress(QString)"), '40')

        self.emit(pyqtSignal("update_status(QString)"), 'Running OpenCV Process 3...')
        self.image_3 = self.test_code_3(self.original_image)
        self.emit(pyqtSignal("update_progress(QString)"), '60')

        self.emit(pyqtSignal("update_status(QString)"), 'Running OpenCV Process 4...')
        self.image_4 = self.test_code_4(self.original_image)
        self.emit(pyqtSignal("update_progress(QString)"), '80')

        self.emit(pyqtSignal("update_status(QString)"), 'Running OpenCV Process 5...')
        self.image_5 = self.test_code_5(self.original_image)
        self.emit(pyqtSignal("update_progress(QString)"), '100')

        self.emit(pyqtSignal("defect_processing_finished(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject, PyQt_PyObject, "
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
