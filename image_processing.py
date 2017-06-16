import cv2
import json

from Queue import Queue
from PyQt4.QtCore import QThread, SIGNAL, Qt

class PreProcessing(QThread):
    """Image Pre-Processing:
    Fixes the source images to then be further processed for defects.
    Applies the following OpenCV processes in order
    Distortion Correction (D)
    Perspective Warp (P)
    Crop (C)
    CLAHE (E)

    Respective capital letters suffixed to the image array indicate which processes have been applied
    """

    def __init__(self, queue1, queue2, calibration_parameters):

        QThread.__init__(self)

        with open('config.json') as config:
            self.config = json.load(config)

        self.queue1 = queue1
        self.queue2 = queue2


        self.perspective = calibration_parameters[0]
        self.intrinsic_c = calibration_parameters[1]
        self.intrinsic_d = calibration_parameters[2]
        self.output_resolution = calibration_parameters[3]

    def distortion_fix(self, image):
        """Fixes the barrel/pincushion distortion commonly found in pinhole cameras"""

        camera_matrix = self.intrinsic_c
        camera_matrix[0, 2] = image.shape[1] / 2.0  # Half image width
        camera_matrix[1, 2] = image.shape[0] / 2.0  # Half image height

        try:
            image_D = cv2.undistort(image, camera_matrix, self.intrinsic_d)
            return image_D
        except:
            print 'Image Distortion fix failed.'
            return False

    def perspective_fix(self, image):
        try:
            image_P = cv2.warpPerspective(image, self.perspective, tuple(self.output_resolution[0]))
            return image_P
        except:
            print 'Image Perspective Fix failed.'
            return False

    def crop(self, image):
        rotation_angle = self.config['RotationAmt']
        crop_boundary = self.config['CropBoundary']

        image = image[crop_boundary[0]:crop_boundary[1], crop_boundary[2]:crop_boundary[3]]
        rotation_matrix = cv2.getRotationmatrix2D((image.shape[1] / 2, image.shape[0] / 2), rotation_angle, 1.0)

        image = cv2.warpAffine(image, rotation_matrix, (image.shape[1], image.shape[0]))

        image_C = image[30:-20, :]

        return image_C

    def CLAHE(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        CLAHE_filter = cv2.createCLAHE(8.0, (64, 64))
        image = CLAHE_filter.apply(image)
        image_E = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        return image_E
