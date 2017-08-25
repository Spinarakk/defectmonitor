# Import external libraries
import os
import time
import math
import json
import cv2
import numpy as np
from PyQt4.QtCore import QThread, SIGNAL


class Calibration(QThread):
    """Module used to calibrate the connected Basler Ace acA3800-10gm GigE camera if attached
    User specifies a folder of checkboard images taken using the camera and outputs the camera parameters to a text file
    Default calibration settings stored in camera_parameters.txt
    """

    def __init__(self, calibration_folder, save_chess_flag=False, save_undistort_flag=False):

        # Defines the class as a thread
        QThread.__init__(self)

        with open('config.json') as config:
            self.config = json.load(config)

        # Save respective values to be used in Calibration functions
        self.ratio = self.config['CameraCalibration']['DownscalingRatio']
        self.width = self.config['CameraCalibration']['Width']
        self.height = self.config['CameraCalibration']['Height']

        # Flags are for whether to save the processed images to a folder
        self.calibration_folder = calibration_folder
        self.save_chess_flag = save_chess_flag
        self.save_undistort_flag = save_undistort_flag

        # Initialize a few lists to store pertinent data

        self.images_calibration = list()
        self.images_valid = list()

        # Create a copy of the ImageCorrection key of the config.json file to store the calibration results
        self.results = dict()
        self.results['ImageCorrection'] = self.config['ImageCorrection'].copy()

        # Image points are points in the 2D image plane
        # They are represented by the corners of the squares on the chessboard as found by findChessboardCorners
        self.image_points_list = list()
        # Object Points are the points in the 3D real world space
        # They are represented as a series of points as relative to each other, and are created like (0,0), (1,0)...
        self.object_points_list = list()

        # Create two folders inside the received calibration folder to store chessboard corner and undistorted images
        if self.save_chess_flag:
            if not os.path.exists('%s/corners' % self.calibration_folder):
                os.makedirs('%s/corners' % self.calibration_folder)
        if self.save_undistort_flag:
            if not os.path.exists('%s/undistorted' % self.calibration_folder):
                os.makedirs('%s/undistorted' % self.calibration_folder)

        # Load the calibration image names
        for image_calibration in os.listdir(self.calibration_folder):
            if 'image_calibration' in str(image_calibration):
                self.images_calibration.append(str(image_calibration))

        # Count the number of calibration images to use as a progress indicator
        self.progress_step = 100.0 / self.images_calibration.__len__()
        self.progress = 0

    def run(self):

        # Load homography images into memory
        image_homography = cv2.imread(self.config['CameraCalibration']['HomographyImage'], 0)

        # Termination Criteria
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # Initiate object points, like (0,0,0), (1,0,0), (2,0,0)...
        self.object_points = np.zeros((self.height * self.width, 3), np.float32)
        self.object_points[:, :2] = np.mgrid[0:self.width, 0:self.height].T.reshape(-1, 2)

        # Reset the progress bar
        self.emit(SIGNAL("update_progress(QString)"), '0')

        # Go through and find the corners for all the valid images in the folder
        for index, image_calibration in enumerate(self.images_calibration):
            valid_image = self.find_draw_corners(image_calibration, index)
            self.images_valid.append(valid_image)
            self.progress += self.progress_step
            self.emit(SIGNAL("update_progress(QString)"), str(int(math.ceil(self.progress))))

        # Check if there's at least one successful chessboard image before continuing to find camera matrix
        if 1 in self.images_valid:

            # Calibrate the camera and output the camera matrix and distortion coefficients
            # RMS is the root mean square re-projection error
            self.emit(SIGNAL("update_status(QString)"), 'Calculating camera parameters...')
            rms, self.camera_matrix, self.distortion_coefficients, _, _ = \
                cv2.calibrateCamera(self.object_points_list, self.image_points_list, self.resolution, None, None, flags=
                cv2.CALIB_FIX_PRINCIPAL_POINT | cv2.CALIB_ZERO_TANGENT_DIST)

            # Save the calibration results to the results dictionary
            self.results['ImageCorrection']['RMS'] = rms
            self.results['ImageCorrection']['CameraMatrix'] = self.camera_matrix.tolist()
            self.results['ImageCorrection']['DistortionCoefficients'] = self.distortion_coefficients.tolist()

            # If the Save Undistorted Images checkbox is checked
            if self.save_undistort_flag:
                # Reset the progress bar and recalculate the progress step
                self.emit(SIGNAL("update_progress(QString)"), '0')
                self.progress_step = 100.0 / self.images_valid.count(1)
                self.progress = 0

                for index, image_calibration in enumerate(self.images_calibration):
                    # Only undistort on the images that were valid
                    if self.images_valid[index]:
                        self.undistort_image(image_calibration)
                        self.progress += self.progress_step
                        self.emit(SIGNAL("update_progress(QString)"), str(int(math.ceil(self.progress))))

            # If the homography matrix was successfully found, save the results to a temporary .json file
            if self.find_homography(image_homography):
                with open('%s/calibration_results.json' % self.config['WorkingDirectory'], 'w+') as results:
                    json.dump(self.results, results, indent=4, sort_keys=True)

                self.emit(SIGNAL("update_status(QString)"), 'Calibration completed successfully.')
        else:
            self.emit(SIGNAL("update_status(QString)"),
                      'No valid chessboard images found. Check images or chessboard dimensions.')

    def find_draw_corners(self, image_name, index):

        self.emit(SIGNAL("update_status(QString)"), 'Finding corners in %s...' % image_name)

        # Load the image into memory
        image = cv2.imread('%s/%s' % (self.calibration_folder, image_name))

        self.resolution = (image.shape[1], image.shape[0])

        # Determine the resolution of the image after downscaling
        resolution_scaled = (image.shape[1] / self.ratio, image.shape[0] / self.ratio)

        # Downscale and convert the image to grayscale
        image_scaled = cv2.resize(image, resolution_scaled, interpolation=cv2.INTER_AREA)
        image_scaled = cv2.cvtColor(image_scaled, cv2.COLOR_BGR2GRAY)

        # Detect the corners of the chessboard
        retval, corners = cv2.findChessboardCorners(image_scaled, (self.width, self.height))

        # If chessboard corners were found
        if retval:
            # Refine the found corner coordinates
            cv2.cornerSubPix(image_scaled, corners, (10, 10), (-1, -1), self.criteria)

            # Multiply back to the original resolution
            corners *= self.ratio

            # Store the found image points (corners) and their corresponding object points in a list
            self.image_points_list.append(corners)
            self.object_points_list.append(self.object_points)

            # If the Save Chessboard Image checkbox is checked
            if self.save_chess_flag:
                # Draw the chessboard corners onto the original calibration image
                cv2.drawChessboardCorners(image, (self.width, self.height), corners, 1)

                # Change the name and folder of the calibration image and save it to that folder
                image_name = image_name.replace('.png', '_corners.png')
                self.emit(SIGNAL("update_status(QString)"), 'Saving %s...' % image_name)
                cv2.imwrite('%s/corners/%s' % (self.calibration_folder, image_name), image)

            self.emit(SIGNAL("change_colour(QString, QString)"), str(index), '1')

            return 1
        else:
            self.emit(SIGNAL("update_status(QString)"), 'Failed to detect corners in %s.' % image_name)
            self.emit(SIGNAL("change_colour(QString, QString)"), str(index), '0')
            time.sleep(0.5)
            return 0

    def undistort_image(self, image_name):

        self.emit(SIGNAL("update_status(QString)"), 'Undistorting %s...' % image_name)

        # Load the image into memory
        image = cv2.imread('%s/%s' % (self.calibration_folder, image_name))

        # Undistort the image using the calculated camera matrix and distortion coefficients
        image = cv2.undistort(image, self.camera_matrix, self.distortion_coefficients)

        # Change the name and folder of the calibration image and save it to that folder
        image_name = image_name.replace('.png', '_undistorted.png')
        self.emit(SIGNAL("update_status(QString)"), 'Saving %s...' % image_name)
        cv2.imwrite('%s/undistorted/%s' % (self.calibration_folder, image_name), image)

    def find_homography(self, image):

        self.emit(SIGNAL("update_status(QString)"), 'Determining homography matrix...')

        # Set the number of chessboard corners in the homography image here
        width = 9
        height = 7

        # Determine the resolution of the image after downscaling
        resolution_scaled = (image.shape[1] / self.ratio, image.shape[0] / self.ratio)

        # Downscale the image
        image_scaled = cv2.resize(image, resolution_scaled, interpolation=cv2.INTER_AREA)

        # Detect the corners of the chessboard
        retval, corners = cv2.findChessboardCorners(image_scaled, (width, height))

        # If chessboard corners were found
        if retval:
            # Refine the found corner coordinates
            cv2.cornerSubPix(image_scaled, corners, (10, 10), (-1, -1), self.criteria)

            # Multiply back to the original resolution
            corners *= self.ratio

            # Undistort the found corners to be used for homography
            image_points = cv2.undistortPoints(corners, self.camera_matrix, self.distortion_coefficients,
                                                P=self.camera_matrix)

            # Create a matrix of points on the original image to match homography with
            object_points = np.zeros((height * width, 3), np.float32)
            object_points[:, :2] = image.shape[1] / 20 * np.mgrid[0:width, 0:height].T.reshape(-1, 2)

            # Calculate the homography matrix using the image and object points
            homography_matrix, _ = cv2.findHomography(image_points, object_points, cv2.RANSAC, 5.0)

            # Perform a perspective transform on the original image
            points_corners = np.float32([[(0, 0)], [(0, image.shape[0])], [(image.shape[1], image.shape[0])],
                                       [(image.shape[1], 0)]]).reshape(-1, 1, 2)
            points_transform = cv2.perspectiveTransform(points_corners, homography_matrix)

            # Create a translation offset to move the perspective warped image to the centre
            points_offset = np.array([[1, 0, -points_transform[:, 0][:, 0].min()],
                                      [0, 1, -points_transform[:, 0][:, 1].min()], [0, 0, 1]])

            # Modify the homography matrix with the translation matrix using dot product
            self.results['ImageCorrection']['HomographyMatrix'] = np.dot(points_offset, homography_matrix).tolist()

            # Figure out the final resolution to crop the image to
            width_output = int(points_transform[:, 0][:, 0].max() - points_transform[:, 0][:, 0].min())
            height_output = int(points_transform[:, 0][:, 1].max() - points_transform[:, 0][:, 1].min())
            self.results['ImageCorrection']['Resolution'] = (width_output, height_output)

            self.emit(SIGNAL("update_status(QString)"), 'Homography matrix found.')

            return 1
        else:
            self.emit(SIGNAL("update_status(QString)"), 'Corner detection failed. Check homography image.')
            return 0
