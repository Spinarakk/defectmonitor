# Import external libraries
import json
import cv2
import numpy as np
from PyQt4.QtCore import QThread, SIGNAL


class ImageCorrection(QThread):
    """Module used to correct the raw images taken by the camera for various optical related issues
    Processed images to then be scanned for any particular defects using the DefectDetection module
    Applies the following OpenCV processes in order:
    Distortion Correction (D)
    Perspective Warp (P)
    Crop (C)
    CLAHE (E)
    Respective capital letters suffixed to the image array name indicate which processes have been applied
    """

    def __init__(self, image_folder, image_coat, image_scan):

        # Defines the class as a thread
        QThread.__init__(self)

        # Load configuration settings from config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Get the name of the calibration file as specified in the New Build dialog
        self.calibration_file_name = self.config['WorkingDirectory'] + '/' + self.config['CalibrationFile']

        # Load camera parameters from specified calibration file
        with open('%s' % self.calibration_file_name) as camera_parameters:
            self.camera_parameters = np.fromstring(camera_parameters.read(), dtype=float, sep=',')

        # Save respective values to be used in OpenCV functions
        self.perspective = self.camera_parameters[0:9].reshape(3, 3)
        self.intrinsic_c = self.camera_parameters[9:18].reshape(3, 3)
        self.intrinsic_d = self.camera_parameters[18:23].reshape(1, 5)
        self.output_resolution = self.camera_parameters[23:].reshape(1, 2).astype(np.int32)

        # Define lists containing the 2 image arrays, 2 phase strings, 3 processing tag strings and 3 status messages
        if bool(image_folder):
            self.image_folder = image_folder + '/processed'
            self.images = (image_coat, image_scan)
            self.phases = ('coat', 'scan')
            self.tags = ('DP', 'DPC', 'DPCE')
            self.status_messages = ('Fixing Distortion & Perspective...', 'Cropping images...',
                                    'Applying CLAHE algorithm...')
            self.progress_counter = 0.0

    def run(self):
        """This for loop loops through the three tags and two phases to produce six processed images
        For each image, depending on the tag, it'll be subjected to certain processes
        After which the image will be saved to disk and emitted back to the main function
        Progress and status updates found here as well
        """

        for tag_index, tag in enumerate(self.tags):
            for phase_index, phase in enumerate(self.phases):

                self.emit(SIGNAL("update_status(QString)"), self.status_messages[tag_index])

                self.image = self.distortion_fix(self.images[phase_index])
                self.image = self.perspective_fix(self.image)
                if tag is not 'DP':
                    self.image = self.crop(self.image)
                    if tag is not 'DPC':
                        self.image = self.clahe(self.image)

                self.progress_counter += 8.333
                self.emit(SIGNAL("update_progress(QString)"), str(int(round(self.progress_counter))))
                self.emit(SIGNAL("update_status(QString)"), self.status_messages[tag_index] +
                          ' Saving sample_%s_%s.png...' % (phase, tag))

                # Write the current processed image to disk named using appropriate tags, and send back to main function
                cv2.imwrite('%s/sample_%s_%s.png' % (self.image_folder, phase, tag), self.image)
                self.emit(SIGNAL("assign_images(PyQt_PyObject, QString, QString)"), self.image, phase, tag)

                self.progress_counter += 8.333
                self.emit(SIGNAL("update_progress(QString)"), str(int(round(self.progress_counter))))

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
        image = image[crop_boundary[0]: crop_boundary[1], crop_boundary[2]: crop_boundary[3]]

        # Rotate the image by creating and using a 2x3 rotation matrix
        rotation_matrix = cv2.getRotationMatrix2D((image.shape[1] / 2, image.shape[0] / 2), rotation_angle, 1.0)
        image_C = cv2.warpAffine(image, rotation_matrix, (image.shape[1], image.shape[0]))

        return image_C

    @staticmethod
    def clahe(image):
        """
        Applies a Contrast Limited Adaptive Histogram Equalization to the image
        Used to improve the contrast of the image to make it clearer/visible
        """

        # Algorithm requires the image to be in grayscale format to function
        # This line checks if the image is already grayscale or in bgr
        if (len(image.shape)==3):
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        clahe_filter = cv2.createCLAHE(8.0, (64, 64))
        image = clahe_filter.apply(image)
        image_E = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        return image_E


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
