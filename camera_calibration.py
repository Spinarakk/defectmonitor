# Import external libraries
import os
import time
import json
import cv2
import numpy as np

# Import related modules
import image_processing


class Calibration:
    """Module used to calibrate the Basler Ace acA3800-10gm GigE camera using images taken by the camera
    User specifies a folder of chessboard images taken using the camera and outputs the camera intrinsics and parameters
    """

    def __init__(self):

        # Load from the config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Create a copy of the ImageCorrection key of the config.json file to store the calibration results
        self.results = dict()
        self.results['ImageCorrection'] = self.config['ImageCorrection'].copy()

        # Image points are points in the 2D image plane
        # They are represented by the corners of the squares on the chessboard as found by findChessboardCorners
        self.points_2d = list()

        # Object Points are the points in the 3D real world space
        # They are represented as a series of points as relative to each other, and are created like (0,0), (1,0)...
        self.points_3d = list()

    def calibrate(self, image_list, status, progress, colour):

        # Assign the status, progress and signals as instance variables so other methods can use them
        self.status = status
        self.progress = progress
        self.colour = colour

        # Reset the progress bar
        self.progress.emit(0)

        # Initialize a list to store valid image flags
        image_list_valid = list()

        # Count the number of calibration images to use as a progress indicator
        increment = 100 / len(image_list)
        progress = 0

        # Go through and find the corners for all the valid images in the folder
        for index, image_name in enumerate(image_list):
            image_list_valid.append(self.find_draw_corners(image_name, index))

            # UI Progress and Status Messages
            progress += increment
            self.progress.emit(round(progress))

        # Check if there's at least one successful chessboard image before continuing to find camera matrix
        if 1 in image_list_valid:
            self.status.emit('Calculating camera parameters...')

            # Calibrate the camera and output the camera matrix and distortion coefficients
            # RMS is the root mean square re-projection error
            rms, camera_matrix, distortion_coefficients, _, _ = \
                cv2.calibrateCamera(self.points_3d, self.points_2d, self.resolution, None, None,
                                    flags=cv2.CALIB_FIX_PRINCIPAL_POINT | cv2.CALIB_ZERO_TANGENT_DIST)

            # Save the calibration results to the results dictionary
            self.results['ImageCorrection']['RMS'] = rms
            self.results['ImageCorrection']['CameraMatrix'] = camera_matrix.tolist()
            self.results['ImageCorrection']['DistortionCoefficients'] = distortion_coefficients.tolist()

            # If the Save Undistorted Images checkbox is checked
            if self.config['CameraCalibration']['Undistort']:
                # Reset the progress bar and recalculate the increment
                self.progress.emit(0)
                increment = 100 / image_list_valid.count(1)
                progress = 0

                for index, image_name in enumerate(image_list):
                    # Only undistort on the images that were valid
                    if image_list_valid[index]:
                        self.undistort_image(image_name, camera_matrix, distortion_coefficients)

                        # UI Progress and Status Messages
                        progress += increment
                        self.progress.emit(round(progress))

            # If the homography matrix was successfully found
            if self.find_homography(camera_matrix, distortion_coefficients):

                # Save the results to a temporary .json file
                with open('calibration_results.json', 'w+') as results:
                    json.dump(self.results, results, indent=4, sort_keys=True)

                # If the Apply to Test Image checkbox is checked, apply the recently calculated camera parameters
                # On the received test image (with corresponding progress indicators)
                if self.config['CameraCalibration']['Apply']:
                    self.status.emit('Processing test image...')
                    self.progress.emit(0)
                    image_test = cv2.imread(self.config['CameraCalibration']['TestImage'])
                    image_test = image_processing.ImageFix().distortion_fix(image_test)
                    cv2.imwrite(self.config['CameraCalibration']['TestImage'].replace('.png', '_D.png'), image_test)
                    self.progress.emit(25)
                    image_test = image_processing.ImageFix().perspective_fix(image_test)
                    self.progress.emit(50)
                    cv2.imwrite(self.config['CameraCalibration']['TestImage'].replace('.png', '_DP.png'), image_test)
                    image_test = image_processing.ImageFix().crop(image_test)
                    self.progress.emit(75)
                    cv2.imwrite(self.config['CameraCalibration']['TestImage'].replace('.png', '_DPC.png'), image_test)
                    self.status.emit('Test image successfully fixed.')
                    self.progress.emit(100)

                    # Open the image in the native image viewer for the user to view the results of the calibration
                    os.startfile(self.config['CameraCalibration']['TestImage'].replace('.png', '_DPC.png'))

                self.status.emit('Calibration completed successfully.')
                return True
            else:
                self.status.emit('Homography corner detection failed. Check chessboard dimensions.')
                return False
        else:
            self.status.emit('No valid chessboard images found. Check images or chessboard dimensions.')

    def find_draw_corners(self, image_name_full, index):
        """Find the corners in the chessboard and draw the corner points if the flag is raised"""

        # Grab just the image name without the directory path
        image_name = os.path.splitext(os.path.basename(image_name_full))[0]
        self.status.emit('Finding corners in %s...' % image_name)

        # Grab certain values to be used in Calibration functions
        width = self.config['CameraCalibration']['Width']
        height = self.config['CameraCalibration']['Height']
        ratio = self.config['CameraCalibration']['DownscalingRatio']

        # Load the image into memory and save the resolution of the image
        image = cv2.imread(image_name_full, 0)
        self.resolution = image.shape[:2][::-1]

        # Determine the resolution of the image after downscaling (if necessary) and downscale it
        image_scaled = cv2.resize(image, (image.shape[1] // ratio, image.shape[0] // ratio),
                                  interpolation=cv2.INTER_AREA)

        # Detect the corners of the chessboard
        retval, corners = cv2.findChessboardCorners(image_scaled, (width, height))

        # If chessboard corners were found
        if retval:
            # Refine the found corner coordinates using the following termination criteria
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            cv2.cornerSubPix(image_scaled, corners, (10, 10), (-1, -1), criteria)

            # Multiply found corner points back to the original resolution
            corners *= ratio

            # Initiate object points, like (0,0,0), (1,0,0), (2,0,0)...
            object_points = np.zeros((height * width, 3), np.float32)
            object_points[:, :2] = np.mgrid[0:width, 0:height].T.reshape(-1, 2)

            # Store the found image points (corners) and their corresponding object points in a list
            self.points_2d.append(corners)
            self.points_3d.append(object_points)

            # If the Save Chessboard Image checkbox is checked
            if self.config['CameraCalibration']['Chessboard']:
                # Create a 'corners' folder in the current image's root directory if it doesn't exist
                folder = '%s/corners' % os.path.dirname(image_name_full)
                if not os.path.isdir(folder):
                    os.makedirs(folder)

                # Draw the chessboard corners onto the original calibration image
                cv2.drawChessboardCorners(image, (width, height), corners, 1)

                # Save the image to the corners folder
                self.status.emit('Saving %s...' % image_name)
                cv2.imwrite('%s/%s_corners.png' % (folder, image_name), image)

            # Emit the index of the current image and a bool value if the findChessboardCorners was successful or not
            self.colour.emit(index, True)
            return 1
        else:
            # If chessboard corners couldn't be found, return a 0 indicating a non-valid image
            self.status.emit('Failed to detect corners in %s.' % image_name)
            self.colour.emit(index, False)
            time.sleep(0.5)
            return 0

    def undistort_image(self, image_name_full, camera_matrix, distortion_coefficients):
        """Use the distortion coefficients to undistort the calibration images"""

        # Grab just the image name without the directory path
        image_name = os.path.splitext(os.path.basename(image_name_full))[0]
        self.status.emit('Undistorting %s...' % image_name)

        # Create an 'undistorted' folder in the current image's root directory if it doesn't exist
        folder = '%s/undistorted' % os.path.dirname(image_name_full)
        if not os.path.isdir(folder):
            os.makedirs(folder)

        # Load the image into memory and undistort it using the calculated camera matrix and distortion coefficients
        image = cv2.imread(image_name_full)
        image = cv2.undistort(image, camera_matrix, distortion_coefficients)

        # Change the name and folder of the calibration image and save it to that folder
        self.status.emit('Saving %s...' % image_name)
        cv2.imwrite('%s/%s_undistorted.png' % (folder, image_name), image)

    def find_homography(self, camera_matrix, distortion_coefficients):
        """Use the homography image and the found camera matrix to calculate the homography matrix"""

        self.status.emit('Determining homography matrix...')

        # Grab certain values to be used in Calibration functions
        width = self.config['CameraCalibration']['WidthHI']
        height = self.config['CameraCalibration']['HeightHI']
        ratio = self.config['CameraCalibration']['DownscalingRatio']

        # Load the homography image into memory in grayscale
        image = cv2.imread(self.config['CameraCalibration']['HomographyImage'], 0)

        # Determine the resolution of the image after downscaling and downscale it
        image_scaled = cv2.resize(image, (image.shape[1] // ratio, image.shape[0] // ratio),
                                  interpolation=cv2.INTER_AREA)

        # Detect the corners of the chessboard
        retval, corners = cv2.findChessboardCorners(image_scaled, (width, height))

        # If chessboard corners were found
        if retval:
            # Refine the found corner coordinates using the following termination criteria
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            cv2.cornerSubPix(image_scaled, corners, (10, 10), (-1, -1), criteria)

            # Multiply back to the original resolution
            corners *= ratio

            cv2.drawChessboardCorners(image, (width, height), corners, 1)
            cv2.imwrite('asdf.png', image)

            # Undistort the found corners to be used for homography
            image_points = cv2.undistortPoints(corners, camera_matrix, distortion_coefficients, P=camera_matrix)

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
            self.results['ImageCorrection']['HomographyResolution'] = (width_output, height_output)

            self.status.emit('Homography matrix found.')
            return True
        else:
            return False
