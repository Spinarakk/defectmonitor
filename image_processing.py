"""
image_processing.py
Module containing mostly OpenCV code used to process the images for initial analysis or for defect identification.
"""
import cv2
import json

from Queue import Queue
from PyQt4.QtCore import QThread, SIGNAL, Qt

class ImageCorrection(QThread):
    """
    Prepares the source/captured images by fixing various optical related problems
    Processed images to then be scanned for any particular defects
    Applies the following OpenCV processes in order:
    Distortion Correction (D)
    Perspective Warp (P)
    Crop (C)
    CLAHE (E)
    Respective capital letters suffixed to the image array name indicate which processes have been applied
    """

    def __init__(self, queue1, queue2, calibration_parameters):

        # Defines the class as a thread
        QThread.__init__(self)

        # Loads configuration settings from respective .json file
        with open('config.json') as config:
            self.config = json.load(config)

        self.queue1 = queue1
        self.queue2 = queue2

        # Save respective values to be used in OpenCV functions
        self.perspective = calibration_parameters[0]
        self.intrinsic_c = calibration_parameters[1]
        self.intrinsic_d = calibration_parameters[2]
        self.output_resolution = calibration_parameters[3]

    def run(self):
        pass

    def distortion_fix(self, image):
        """Fixes the barrel/pincushion distortion commonly found in pinhole cameras"""

        # Store the camera's intrinsic values as a 2x2 matrix
        camera_matrix = self.intrinsic_c
        camera_matrix[0, 2] = image.shape[1] / 2.0  # Half image width
        camera_matrix[1, 2] = image.shape[0] / 2.0  # Half image height

        # OpenCV distortion fix function
        try:
            image_D = cv2.undistort(image, camera_matrix, self.intrinsic_d)
            return image_D
        except:
            print 'Image Distortion fix failed.'
            return False

    def perspective_fix(self, image):
        """Fixes the perspective warp due to the off-centre position of the camera"""

        try:
            image_P = cv2.warpPerspective(image, self.perspective, tuple(self.output_resolution[0]))
            return image_P
        except:
            print 'Image Perspective Fix failed.'
            return False

    def crop(self, image):
        """Crops the image to a more desirable region of interest"""

        # Save respective values to be used to determine region of interest
        rotation_angle = self.config['RotationAmt']
        crop_boundary = self.config['CropBoundary']

        # Crop the image to a rectangle region of interest as dictated by the following values [H,W]
        image = image[crop_boundary[0] : crop_boundary[1], crop_boundary[2] : crop_boundary[3]]

        # Rotate the image by creating and using a 2x3 rotation matrix
        rotation_matrix = cv2.getRotationMatrix2D((image.shape[1] / 2, image.shape[0] / 2), rotation_angle, 1.0)
        image_C = cv2.warpAffine(image, rotation_matrix, (image.shape[1], image.shape[0]))

        return image_C

    def CLAHE(self, image):
        """
        Applies a Contrast Limited Adaptive Histogram Equalization to the image
        Used to improve the contrast of the image to make it clearer/visible
        """

        # CLAHE requires the image to be grayscale to function
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        CLAHE_filter = cv2.createCLAHE(8.0, (64, 64))
        image = CLAHE_filter.apply(image)
        image_E = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        return image_E


class DefectDetection(QThread):
    """
    Processes the prepared images using OpenCV to detect a variety of different defects
    Defects to be detected and a brief explanation:

    """
    def __init__(self):
        QThread.__init__(self)