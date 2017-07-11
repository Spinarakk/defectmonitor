# Import external libraries
import os
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

        ratio = 2
        board_width = 9  # chessboard dimensions
        board_height = 7

        c_mult = image.shape[1] / 10 / ratio
        original_image = image.copy()
        # res = (original_image.shape[1], original_image.shape[0])
        # new_res = (image.shape[1] / ratio, image.shape[0] / ratio)
        #
        # image = cv2.resize(image, new_res, interpolation=cv2.INTER_AREA)
        # self.emit(SIGNAL("update_progress(QString)"), '20')
        # image = cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
        # self.emit(SIGNAL("update_progress(QString)"), '30')

        # Populate projection points matrix with values
        prj_pts = np.zeros((board_width * board_height, 3), np.float32)
        prj_pts[:, :2] = c_mult * np.mgrid[1:(board_width + 1), 1:(board_height + 1)].T.reshape(
            board_width * board_height, 2)

        world_pts = prj_pts.reshape(1, board_width * board_height, 3).astype(np.float32)

        # Set subpixel refinement criteria
        spr_criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # Detect corners of chessboard calibration image
        _, det_corners = cv2.findChessboardCorners(image,
                                                   (board_width, board_height))  # , flags=cv2.CALIB_CB_ADAPTIVE_THRESH)
        self.emit(SIGNAL("update_progress(QString)"), '40')

        cv2.cornerSubPix(image, det_corners, (10, 10), (-1, -1), spr_criteria)
        det_corners = ratio * det_corners.reshape(1, board_width * board_height, 2)
        ret, intr_c, intr_d, r_vec, t_vec = cv2.calibrateCamera(world_pts, det_corners, res, None, None,
                                                                flags=cv2.CALIB_FIX_PRINCIPAL_POINT | cv2.CALIB_FIX_K4
                                                                | cv2.CALIB_FIX_K5 | cv2.CALIB_FIX_K3)

        intr_d[0][1:] = 0
        intr_d[0][0] *= 0.9



        new_corners = cv2.undistortPoints(det_corners, intr_c, intr_d, P=intr_c)
        flat_image = cv2.undistort(original_image, intr_c, intr_d)
        # tl, tr, bl, br = [new_corners[0, :][0], new_corners[0, :][board_width - 1], new_corners[0, :][-(board_width)],
        #                   new_corners[0, :][-1]]
        # prj_pts[:, 0] += int(tl[0])  # translate projection points by distance to top left point
        # prj_pts[:, 1] += int(tl[1])
        self.emit(SIGNAL("update_progress(QString)"), '50')
        prj_pts = prj_pts.reshape(1, board_width * board_height, 3).astype(np.float32)

        flat_image = cv2.cvtColor(flat_image, cv2.COLOR_GRAY2BGR)
        cv2.drawChessboardCorners(flat_image, (9, 7), new_corners, 1)  # sum_sqdiff = 0
        # for i in xrange(board_width * board_height):
        #     dist = self.pythag(image_pts[0][i][0], image_pts[0][i][1], prj_pts[0][i][0], prj_pts[0][i][1])
        #     sum_sqdiff += dist

        h, _ = cv2.findHomography(new_corners, prj_pts)
        # h[0, 2] *= ratio
        # h[1, 2] *= ratio
        # h[2, 0] /= ratio
        # h[2, 1] /= ratio
        self.emit(SIGNAL("update_progress(QString)"), '60')
        tfm_pts = cv2.perspectiveTransform(
            np.array([[(0, 0)], [(0, res[1])], [(res[0], res[1])], [(res[0], res[1])]], dtype=float), h)
        offset = np.array([[1, 0, -tfm_pts[:, 0][:, 0].min()], [0, 1, -tfm_pts[:, 0][:, 1].min()],
                           [0, 0, 1]])  # establish translation offset matrix
        h = np.dot(offset, h)  # Modify homography with translation matrix
        out_h = int(tfm_pts[:, 0][:, 1].max() - tfm_pts[:, 0][:, 1].min())
        out_w = int(tfm_pts[:, 0][:, 0].max() - tfm_pts[:, 0][:, 0].min())
        outres = np.array([(out_w, out_h)])

        calibrate_params = [h, intr_c, intr_d, outres]
        self.emit(SIGNAL("update_progress(QString)"), '70')

        self.emit(SIGNAL("update_progress(QString)"), '80')
        sleep(0.5)

        self.emit(SIGNAL("update_progress(QString)"), '90')
        sleep(0.5)

        # Writes the calibration settings to a text file to be read later
        with open('camera_parameters2.txt', 'w+') as parameter_txt:
            for array in calibrate_params:
                array = array.reshape(array.shape[0] * array.shape[1], 1)
                for element in array:
                    parameter_txt.write('%s,' % element[0])

        return 1

    @staticmethod
    def pythag(x1, y1, x2, y2):
        return (x2 - x1) ** 2 + (y2 - y1) ** 2

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

