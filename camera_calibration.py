# Import external libraries
import os
import time
import math
import json
import cv2
import numpy as np
from PyQt4.QtCore import QThread, SIGNAL

# Import related modules
import image_processing


class Calibration(QThread):
    """Module used to calibrate the connected Basler Ace acA3800-10gm GigE camera if attached
    User specifies a folder of checkboard images taken using the camera and outputs the camera parameters to a text file
    If no camera is found, or simulation flag is raised, default calibration settings will be used
    Default calibration settings stored in camera_parameters.txt
    """

    def __init__(self, calibration_folder, save_chess_flag=False, save_undistort_flag=False):

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

        # Flags are for whether to save the processed images to a folder
        self.calibration_folder = calibration_folder
        self.save_chess_flag = save_chess_flag
        self.save_undistort_flag = save_undistort_flag

        # Initialize a few lists to store pertinent data
        self.images_calibration = []
        self.images_valid = []
        self.image_points = []
        self.object_points = []

        # Create two folders inside the received calibration folder to store chessboard corner and undistorted images
        if self.save_chess_flag:
            try:
                os.mkdir('%s/corners' % self.calibration_folder)
            except WindowsError:
                pass

        if self.save_undistort_flag:
            try:
                os.mkdir('%s/undistorted' % self.calibration_folder)
            except WindowsError:
                pass

        # Load the calibration image names
        for image_calibration in os.listdir(self.calibration_folder):
            if 'image_calibration' in str(image_calibration):
                self.images_calibration.append(str(image_calibration))

        # Count the number of calibration images to use as a progress indicator
        self.progress_step = 100.0 / self.images_calibration.__len__()
        self.progress = 0

    def run(self):

        # Load required images into memory
        # First image used to calculate homography in the chamber
        # Second image used to test calibration and homography results
        image_homography = cv2.imread('%s/calibration/image_homography.png' % self.working_directory)
        image_sample = cv2.imread('%s/calibration/image_sample.png' % self.working_directory)

        # Determine resolution of working images
        resolution = (image_sample.shape[1], image_sample.shape[0])

        # Termination Criteria
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        self.multiplier = image_sample.shape[1] / 10 / self.ratio

        self.points_destination = np.zeros((self.height * self.width, 3), np.float32)
        self.points_destination[:, :2] = self.multiplier * np.mgrid[1:(self.width + 1), 1:(self.height + 1)].T.reshape(
            self.width * self.height, 2)

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
            rms, self.camera_matrix, self.distortion_coefficients, _, _ = \
                cv2.calibrateCamera(self.object_points, self.image_points, resolution, None, None, flags=
                cv2.CALIB_FIX_PRINCIPAL_POINT | cv2.CALIB_FIX_K4 | cv2.CALIB_FIX_K5 | cv2.CALIB_FIX_K3)

            # Convert the rms into a numpy array so it can be saved
            self.rms = np.array([(rms)]).astype('float')

            # Refine the camera matrix based on a free scaling parameter, enable as necessary
            # camera_matrix, _ = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_coefficients, resolution, 1, resolution)

            # Modify the distortion coefficients as necessary if distortion effect is too great
            # self.distortion_coefficients[0][1:] = 0
            # self.distortion_coefficients[0][0] *= 0.9

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

            retval = self.find_homography(image_homography)

            # If the homography matrix was successfully found
            if retval:
                # Save the camera_parameters to a text file camera_parameters.txt with appropriate headers
                with open('camera_parameters.txt', 'a+') as camera_parameters:
                    # Wipe the file before appending stuff
                    camera_parameters.truncate()

                    # Append the data
                    np.savetxt(camera_parameters, self.camera_matrix, header='Camera Matrix (3x3)')
                    np.savetxt(camera_parameters, self.distortion_coefficients, header='Distortion Coefficients (1x5)')
                    np.savetxt(camera_parameters, self.homography_matrix, header='Homography Matrix (3x3)')
                    np.savetxt(camera_parameters, self.resolution_output, fmt='%d', header='Output Resolution (1x2)')
                    np.savetxt(camera_parameters, self.rms, header='Re-projection Error (Root Mean Square)')

                self.emit(SIGNAL("update_status(QString)"), 'Parameters saved to camera_parameters.txt.')
        else:
            self.emit(SIGNAL("update_status(QString)"),
                      'No valid chessboard images found. Check images or chessboard dimensions.')

    def find_draw_corners(self, image_name, index):

        self.emit(SIGNAL("update_status(QString)"), 'Finding corners in %s...' % image_name)

        # Load the image into memory
        image = cv2.imread('%s/%s' % (self.calibration_folder, image_name))

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
            corners = self.ratio * corners.reshape(1, self.width * self.height, 2)

            self.image_points.append(corners)
            self.object_points.append(self.points_destination)

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
        cv2.imwrite('%s/corners/%s' % (self.calibration_folder, image_name), image)

    def find_homography(self, image):

        self.emit(SIGNAL("update_status(QString)"), 'Determining homography matrix...')

        # Set the number of chessboard corners in the homography image here
        width = 9
        height = 7

        # Determine the resolution of the image after downscaling
        resolution_scaled = (image.shape[1] / self.ratio, image.shape[0] / self.ratio)

        # Downscale and convert the image to grayscale
        image_scaled = cv2.resize(image, resolution_scaled, interpolation=cv2.INTER_AREA)
        image_scaled = cv2.cvtColor(image_scaled, cv2.COLOR_BGR2GRAY)

        # Detect the corners of the chessboard
        retval, corners = cv2.findChessboardCorners(image_scaled, (width, height))

        # If chessboard corners were found
        if retval:
            # Refine the found corner coordinates
            cv2.cornerSubPix(image_scaled, corners, (10, 10), (-1, -1), self.criteria)

            # Multiply back to the original resolution
            corners = self.ratio * corners.reshape(1, width * height, 2)

            # Undistort the found corners to be used for homography
            points_source = cv2.undistortPoints(corners, self.camera_matrix, self.distortion_coefficients,
                                                P=self.camera_matrix)

            # Create a matrix of points on the original image to match homography with
            points_destination = np.zeros((height * width, 3), np.float32)
            points_destination[:, :2] = self.multiplier * np.mgrid[1: (width + 1), 1: (height + 1)].T.reshape(
                width * height, 2)
            points_destination = points_destination.reshape(1, width * height, 3).astype(np.float32)

            # Calculate the homography matrix using the source and destination points
            homography_matrix, _ = cv2.findHomography(points_source, points_destination)

            # Perform a perspective transform on the original image
            points_corners = np.array([[(0, 0)], [(0, image.shape[0])], [(image.shape[1], image.shape[0])],
                                       [(image.shape[1], image.shape[0])]], dtype=float)
            points_transform = cv2.perspectiveTransform(points_corners, homography_matrix)

            # Create a translation offset to move the perspective warped image to the centre
            points_offset = np.array([[1, 0, -points_transform[:, 0][:, 0].min()],
                                      [0, 1, -points_transform[:, 0][:, 1].min()], [0, 0, 1]])

            # Modify the homography matrix with the translation matrix using dot product
            self.homography_matrix = np.dot(points_offset, homography_matrix)

            # Figure out the final resolution to crop the image to
            width_output = int(points_transform[:, 0][:, 0].max() - points_transform[:, 0][:, 0].min())
            height_output = int(points_transform[:, 0][:, 1].max() - points_transform[:, 0][:, 1].min())
            self.resolution_output = np.array([(width_output, height_output)])

            self.emit(SIGNAL("update_status(QString)"), 'Homography matrix found.')

            return 1
        else:
            self.emit(SIGNAL("update_status(QString)"), 'Corner detection failed. Check homography image.')
            return 0
