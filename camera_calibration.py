# Import external libraries
import os
import json
import cv2
import numpy as np
from PyQt4.QtCore import QThread, SIGNAL
from time import sleep


class Calibration(QThread):
    """Module used to calibrate the connected Basler Ace acA3800-10gm GigE camera if attached
    User specifies a folder of checkboard images taken using the camera and outputs the camera parameters to a text file
    If no camera is found, or simulation flag is raised, default calibration settings will be used
    Default calibration settings stored in camera_parameters.txt
    """

    def __init__(self, calibration_folder):

        # Defines the class as a thread
        QThread.__init__(self)

        # Load configuration settings from config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Save respective values to be used in Calibration functions
        self.ratio = self.config['DownscalingRatio']
        self.width = self.config['CalibrationWidth']
        self.height = self.config['CalibrationHeight']
        self.working_directory = self.config['WorkingDirectory']

        self.calibration_folder = calibration_folder

        # Initialize a few lists to store pertinent data
        self.images_calibration = []
        self.images_valid = []
        self.image_points = []
        self.object_points = []

        # Create two folders inside the received calibration folder to store chessboard corner and undistorted images
        try:
            os.mkdir('%s/corners' % self.calibration_folder)
        except WindowsError:
            pass

        try:
            os.mkdir('%s/undistorted' % self.calibration_folder)
        except WindowsError:
            pass

        # Load the calibration image names
        for image_calibration in os.listdir(self.calibration_folder):
            if 'image_calibration' in str(image_calibration):
                self.images_calibration.append(str(image_calibration))

    def run(self):
        # try:
        #     self.emit(SIGNAL("update_status(QString)"), 'Calibrating from image...')
        #     self.emit(SIGNAL("update_progress(QString)"), '10')
        #     retval = self.start_calibration(self.image_calibration)
        #     if retval:
        #         self.emit(SIGNAL("update_status(QString)"), 'Calibration successful.')
        #         self.emit(SIGNAL("update_progress(QString)"), '100')
        #         self.emit(SIGNAL("successful()"))
        #         os.system("notepad.exe camera_parameters.txt")
        #     else:
        #         self.emit(SIGNAL("update_status(QString)"), 'Calibration failed.')
        # except:
        #     self.emit(SIGNAL("update_status(QString"), 'Calibration image not found.')


        image_homography = cv2.imread('%s/calibration/image_homography.png' % self.working_directory)
        image_sample = cv2.imread('%s/calibration/image_sample.png' % self.working_directory)

        # Termination Criteria
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        self.multiplier = image_sample.shape[1] / 10 / self.ratio

        self.points_destination = np.zeros((self.height * self.width, 3), np.float32)
        self.points_destination[:, :2] = self.multiplier * np.mgrid[1: (self.width + 1), 1: (self.height + 1)].T.reshape(
            self.width * self.height, 2)

        for index, image_calibration in enumerate(self.images_calibration):
            valid_image = self.find_draw_corners(image_calibration, index)
            self.images_valid.append(valid_image)

        print self.images_valid

    def find_draw_corners(self, image_name, index):

        # Load the image into memory
        image = cv2.imread('%s/%s' % (self.calibration_folder, image_name))

        # Determine the resolution of the image and the resolution after downscaling
        resolution = (image.shape[1], image.shape[0])
        resolution_scaled = (image.shape[1] / self.ratio, image.shape[0] / self.ratio)

        image_scaled = cv2.resize(image, resolution_scaled, interpolation=cv2.INTER_AREA)
        image_scaled = cv2.cvtColor(image_scaled, cv2.COLOR_BGR2GRAY)

        retval, corners = cv2.findChessboardCorners(image_scaled, (self.width, self.height))

        # If chessboard corners were found
        if retval:
            # Refine the found corner coordinates
            cv2.cornerSubPix(image_scaled, corners, (10, 10), (-1, -1), self.criteria)
            # Multiply back to the original resolution
            corners = self.ratio * corners.reshape(1, self.width * self.height, 2)
            # Draw the chessboard corners onto the original calibration image
            cv2.drawChessboardCorners(image, (self.width, self.height), corners, 1)

            self.image_points.append(corners)
            self.object_points.append(self.points_destination)

            # Change the name and folder of the calibration image
            image_name = image_name.replace('.png', '_corners.png')
            cv2.imwrite('%s/corners/%s' % (self.calibration_folder, image_name), image)

            self.emit(SIGNAL("change_colour(QString, QString)"), str(index), '1')

            return 1
        else:
            self.emit(SIGNAL("change_colour(QString, QString)"), str(index), '0')
            return 0

    def start_calibration(self, image):
        """Perform the OpenCV calibration process"""

        c_mult = image.shape[1] / 10 / self.ratio
        original_image = image.copy()
        original_resolution = (original_image.shape[1], original_image.shape[0])
        new_res = (image.shape[1] / self.ratio, image.shape[0] / self.ratio)

        image = cv2.resize(image, new_res, interpolation=cv2.INTER_AREA)

        image = cv2.fastNlMeansDenoising(image, None, 10, 7, 21)


        # Populate projection points matrix with values
        points_destination = np.zeros((self.width * self.height, 3), np.float32)
        points_destination[:, :2] = c_mult * np.mgrid[1:(self.width + 1), 1:(self.height + 1)].T.reshape(
            self.width * self.height, 2)

        world_pts = points_destination.reshape(1, self.width * self.height, 3).astype(np.float32)

        # Set subpixel refinement criteria
        spr_criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # Detect corners of chessboard calibration image
        _, det_corners = cv2.findChessboardCorners(image,
                                                   (self.width, self.height))  # , flags=cv2.CALIB_CB_ADAPTIVE_THRESH)


        cv2.cornerSubPix(image, det_corners, (10, 10), (-1, -1), spr_criteria)

        det_corners = self.ratio * det_corners.reshape(1, self.width * self.height, 2)


        return_value, camera_matrix, distortion_coefficients, rotation_vectors, translation_vectors = \
            cv2.calibrateCamera(world_pts, det_corners, original_resolution, None, None, flags=cv2.CALIB_FIX_PRINCIPAL_POINT |
                                cv2.CALIB_FIX_K4| cv2.CALIB_FIX_K5 | cv2.CALIB_FIX_K3)


        distortion_coefficients[0][1:] = 0
        distortion_coefficients[0][0] *= 0.9



        points_source = cv2.undistortPoints(det_corners, camera_matrix, distortion_coefficients, P=camera_matrix)

        flat_image = cv2.undistort(original_image, camera_matrix, distortion_coefficients)


        points_destination = points_destination.reshape(1, self.width * self.height, 3).astype(np.float32)

        flat_image = cv2.cvtColor(flat_image, cv2.COLOR_GRAY2BGR)
        cv2.drawChessboardCorners(flat_image, (9, 7), points_source, 1)  # sum_sqdiff = 0


        homography_matrix, _ = cv2.findHomography(points_source, points_destination)


        tfm_pts = cv2.perspectiveTransform(
            np.array([[(0, 0)], [(0, original_resolution[1])], [(original_resolution[0], original_resolution[1])], [(original_resolution[0], original_resolution[1])]], dtype=float), homography_matrix)
        offset = np.array([[1, 0, -tfm_pts[:, 0][:, 0].min()], [0, 1, -tfm_pts[:, 0][:, 1].min()],
                           [0, 0, 1]])  # establish translation offset matrix
        homography_matrix = np.dot(offset, homography_matrix)  # Modify homography with translation matrix
        out_h = int(tfm_pts[:, 0][:, 1].max() - tfm_pts[:, 0][:, 1].min())
        out_w = int(tfm_pts[:, 0][:, 0].max() - tfm_pts[:, 0][:, 0].min())
        outres = np.array([(out_w, out_h)])

        calibrate_params = [homography_matrix, camera_matrix, distortion_coefficients, outres]



        # Writes the calibration settings to a text file to be read later
        with open('camera_parameters2.txt', 'w+') as parameter_txt:
            for array in calibrate_params:
                array = array.reshape(array.shape[0] * array.shape[1], 1)
                for element in array:
                    parameter_txt.write('%s,' % element[0])

        return 1


    @staticmethod
    def _validate_calibration(reprojection_error):
        if reprojection_error < 5.0:
            valid = True
        else:
            valid = False
        return valid
