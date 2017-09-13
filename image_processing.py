# Import external libraries
import os
import json
import cv2
import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

COLOUR_BLACK = np.array((0, 0, 0))
COLOUR_WHITE = np.array((255, 255, 255))
COLOUR_RED = np.array((0, 0, 255))
COLOUR_BLUE = np.array((255, 0, 0))


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
        """Applies a Contrast Limited Adaptive Histogram Equalization to the image
        Used to improve the contrast of the image to make it clearer/visible
        """

        # Algorithm requires the image to be in grayscale colorspace to function
        # This line checks if the image is already grayscale or in RGB (BGR)
        if (len(image.shape) == 3):
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # CLAHE filter functions
        clahe_filter = cv2.createCLAHE(8.0, (64, 64))
        image = clahe_filter.apply(image)

        # Convert the image back to RGB (BGR) as when converting to a pixmap, grayscale images don't work
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        return image


class DefectDetection:
    """Module used to process the corrected images using OpenCV to detect a variety of different defects
    Defects as outlined in the README.txt file
    Mainly analyzes the received image for the follow defects:
    Bright Spots
    Blade Streaks
    Blade Chatter
    Contrast Differences
    """

    def __init__(self):

        # Load configuration settings from config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Initialize some dictionaries to store the results
        # Defects on refers to the defects that intersect the overlay, Defects off is the opposite
        self.defects_on = {'Bright Spots': [], 'Blade Streaks': [], 'Blade Chatter': [], 'Contrast Differences': []}
        self.defects_off = {'Bright Spots': [], 'Blade Streaks': [], 'Blade Chatter': [], 'Contrast Differences': []}

    def analyze_coat(self):
        # Load the original image and the corresponding overlay into memory
        self.image = cv2.imread(self.config['DefectDetection']['Image'])
        self.image_overlay = cv2.imread(self.config['DefectDetection']['Overlay'])

        # Save respective values to be used in defect detection
        self.layer = self.config['DefectDetection']['Layer']
        self.phase = self.config['DefectDetection']['Phase']

        self.detect_bright_spots(self.image)
        self.detect_blade_streaks(self.image)
        self.detect_blade_chatter(self.image)
        self.detect_contrast(self.image)

    def detect_brightspots(self, image):
        image_defects = image.copy()
        image_clahe = ImageCorrection.clahe(image_defects)
        image_clahe = cv2.cvtColor(image_clahe, cv2.COLOR_BGR2GRAY)
        retval = cv2.threshold(image_clahe, 0, 255, cv2.THRESH_OTSU)[0]
        _, threshold = cv2.threshold(image_clahe, retval * 1.85, 255, cv2.THRESH_BINARY)
        image_defects[threshold == 255] = COLOUR_RED

        if self.defect_size(image_defects) > 0:
            coordinates_on, coordinates_off = self.find_coordinates

    def detect_blade_streaks(self):
        pass

    def detect_blade_chatter(self):
        pass

    def detect_contrast(self):
        pass

    @staticmethod
    def find_coordinates(defects, overlay, colour):
        mask = cv2.inRange(overlay, colour, colour)
        roi = cv2.bitwise_and(defects, defects, mask=mask)


    @staticmethod
    def detect_blob(threshold):
        contours = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
        coordinates = list()
        for contour in contours:
            if cv2.contourArea(contour) > 50:
                (x, y) = cv2.minEnclosingCircle(contour)[0]
                coordinates.append((int(x), int(y)))
        return coordinates.sort()

    @staticmethod
    def defect_size(image):
        return cv2.countNonZero(cv2.inRange(image, np.array([0, 0, 200]), np.array([100, 100, 255])))

    @staticmethod
    def split_otsu(image):
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        retval, threshold = cv2.threshold(image_gray, 0, 255, cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_ERODE, (5, 5))
        cv2.erode(threshold, kernel, dst=threshold, iterations=3)

        for index in range(7):
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * index + 1, 2 * index + 1))
            threshold = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, kernel, iterations=3)
            threshold = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel, iterations=3)

        dark = cv2.bitwise_and(image, image, mask=cv2.bitwise_not(threshold))
        light = cv2.bitwise_and(image, image, mask=threshold)

        return retval, dark, light


    @staticmethod
    def split_colour(image, colour):
        """Returns two images, one of just the received colour and one of the background without the colour"""

        mask = cv2.inRange(image, colour, colour)
        mask_inverse = cv2.bitwise_not(mask)

        foreground = cv2.bitwise_and(image, image, mask=mask)
        background = cv2.bitwise_and(image, image, mask=mask_inverse)

        return background, foreground




