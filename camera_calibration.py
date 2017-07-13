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

        # Save the received argument as an instance variable
        self.calibration_folder = calibration_folder

        print self.calibration_folder

        self.calibration_images = []

        # Load the calibration images
        for calibration_image in os.listdir(self.calibration_folder):
            if 'calibration_image' in str(calibration_image):
                self.calibration_images.append(str(self.calibration_folder + '\\' + calibration_image))

        print self.calibration_images

        #self.calibration_image = cv2.imread('%s/calibration_image.png' % self.calibration_folder, 0)

    def run(self):
        # try:
        #     self.emit(SIGNAL("update_status(QString)"), 'Calibrating from image...')
        #     self.emit(SIGNAL("update_progress(QString)"), '10')
        #     retval = self.start_calibration(self.calibration_image)
        #     if retval:
        #         self.emit(SIGNAL("update_status(QString)"), 'Calibration successful.')
        #         self.emit(SIGNAL("update_progress(QString)"), '100')
        #         self.emit(SIGNAL("successful()"))
        #         os.system("notepad.exe camera_parameters.txt")
        #     else:
        #         self.emit(SIGNAL("update_status(QString)"), 'Calibration failed.')
        # except:
        #     self.emit(SIGNAL("update_status(QString"), 'Calibration image not found.')
        self.counter = 1

        for calibration_image in self.calibration_images:
            self.calibration2(cv2.imread(calibration_image))

        print self.objpoints
        print self.imgpoints

        cv2.waitKey(0)

    def start_calibration(self, image):
        """Perform the OpenCV calibration process"""

        c_mult = image.shape[1] / 10 / self.ratio
        original_image = image.copy()
        res = (original_image.shape[1], original_image.shape[0])
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
        ret, intr_c, intr_d, r_vec, t_vec = cv2.calibrateCamera(world_pts, det_corners, res, None, None,
                                                                flags=cv2.CALIB_FIX_PRINCIPAL_POINT | cv2.CALIB_FIX_K4
                                                                | cv2.CALIB_FIX_K5 | cv2.CALIB_FIX_K3)


        intr_d[0][1:] = 0
        intr_d[0][0] *= 0.9



        points_source = cv2.undistortPoints(det_corners, intr_c, intr_d, P=intr_c)
        flat_image = cv2.undistort(original_image, intr_c, intr_d)


        points_destination = points_destination.reshape(1, self.width * self.height, 3).astype(np.float32)

        flat_image = cv2.cvtColor(flat_image, cv2.COLOR_GRAY2BGR)
        cv2.drawChessboardCorners(flat_image, (9, 7), points_source, 1)  # sum_sqdiff = 0


        homography_matrix, _ = cv2.findHomography(points_source, points_destination)


        tfm_pts = cv2.perspectiveTransform(
            np.array([[(0, 0)], [(0, res[1])], [(res[0], res[1])], [(res[0], res[1])]], dtype=float), homography_matrix)
        offset = np.array([[1, 0, -tfm_pts[:, 0][:, 0].min()], [0, 1, -tfm_pts[:, 0][:, 1].min()],
                           [0, 0, 1]])  # establish translation offset matrix
        homography_matrix = np.dot(offset, homography_matrix)  # Modify homography with translation matrix
        out_h = int(tfm_pts[:, 0][:, 1].max() - tfm_pts[:, 0][:, 1].min())
        out_w = int(tfm_pts[:, 0][:, 0].max() - tfm_pts[:, 0][:, 0].min())
        outres = np.array([(out_w, out_h)])

        calibrate_params = [homography_matrix, intr_c, intr_d, outres]



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

    def calibration2(self, image):
        # termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        objp = np.zeros((6 * 7, 3), np.float32)
        objp[:, :2] = np.mgrid[0:7, 0:6].T.reshape(-1, 2)

        # Arrays to store object points and image points from all the images.
        self.objpoints = []  # 3d point in real world space
        self.imgpoints = []  # 2d points in image plane.

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findChessboardCorners(gray, (7, 6), None)

        if ret == True:
            self.objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1), criteria)
            self.imgpoints.append(corners2)

            image2 = cv2.drawChessboardCorners(image, (7, 6), corners2, ret)
            cv2.imshow('image %s' % self.counter, image2)
            self.counter += 1

