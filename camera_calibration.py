# app_setup
##Import modules
import os
import cv2
import numpy as np

base_files = os.listdir('.')


class Calibrate:
    def __init__(self):
        self.valid = False
        self.calibrate_params = []
        self.old_params = []

    def run(self):
        old_params = self._check_existing()
        if old_params[-1] == 0:
            self.old_params = False
            # calibrate_params = self._start_calibration()
        else:
            self.calibrate_params = old_params[:-1]
            self.old_params = True

        return

    def calibrate_from_file(self):
        calibration_image = 'calibrate10x8.png'
        if calibration_image in base_files:
            image = cv2.imread(calibration_image, 0)
            self.calibrate_params = self.start_calibration(image)
        else:
            return False
            # while not self.valid:
            #     calibrate_params = self._start_calibration()
            #     self.valid = self._validate_calibration(calibrate_params)
            #     if self.valid:
            #         self._save_calibration(calibrate_params)
            # self.calibrate_params = calibrate_params

    def _check_existing(self):
        for f in base_files:
            if f == 'calib_params.dat':
                f_id = open(f, 'r')  # open stored homography file
                h = np.fromstring(f_id.read(), dtype=float, sep=',')  # read and convert to array
                f_id.close()
                perspective = h[0:9].reshape(3, 3)  # Convert to array
                intrinsic_c = h[9:18].reshape(3,3)
                intrinsic_d = h[18:23]
                output_res = h[23:]
                # TODO get chessboard corners and calculate reprojection error with stored params
                return (perspective, intrinsic_c, intrinsic_d,output_res, 1)
            else:
                pass
                # return [0]

    def start_calibration(self, image):
        calibrate_params = []
        ratio = 2
        x_c = 9  # chessboard dimensions
        y_c = 7
        c_mult = image.shape[1] / 10 / ratio
        original_image = image.copy()
        res = (original_image.shape[1], original_image.shape[0])
        new_res = (image.shape[1] / ratio, image.shape[0] / ratio)
        image = cv2.resize(image, new_res, interpolation=cv2.INTER_AREA)
        image = cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
        # Populate projection points matrix with values
        prj_pts = np.zeros((x_c * y_c, 3), np.float32)
        prj_pts[:, :2] = c_mult * np.mgrid[1:(x_c + 1), 1:(y_c + 1)].T.reshape(x_c * y_c, 2)
        world_pts = prj_pts.reshape(1, x_c * y_c, 3).astype(np.float32)
        # prj_pts = prj_pts.reshape(1, x_c * y_c, 3).astype(np.float32)

        # Set subpixel refinement criteria
        spr_criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # Detect corners of chessboard calibration image
        _, det_corners = cv2.findChessboardCorners(image, (x_c, y_c))  # , flags=cv2.CALIB_CB_ADAPTIVE_THRESH)
        cv2.cornerSubPix(image, det_corners, (10, 10), (-1, -1), spr_criteria)
        det_corners = ratio * det_corners.reshape(1, x_c * y_c, 2)
        ret, intr_c, intr_d, r_vec, t_vec = cv2.calibrateCamera(world_pts, det_corners, res, None, None,
                                                                flags=cv2.CALIB_FIX_PRINCIPAL_POINT | cv2.CALIB_FIX_K4 | cv2.CALIB_FIX_K5 | cv2.CALIB_FIX_K3)
        # image_pts = cv2.projectPoints(prj_pts, r_vec, t_vec, intr_c, intr_d)
        intr_d[0][1:] = 0
        intr_d[0][0] *= 0.9

        # new_corners = cv2.undistortPoints(det_corners, intr_c, intr_d, P=intr_c)
        # ret, intr_c, intr_d, r_vec, t_vec = cv2.calibrateCamera(world_pts, new_corners, res, intr_c, intr_d)
        # print intr_d
        # full_intr_c = intr_c
        # full_intr_c[:2,:] *= ratio

        new_corners = cv2.undistortPoints(det_corners, intr_c, intr_d, P=intr_c)
        flat_image = cv2.undistort(original_image, intr_c, intr_d)
        tl, tr, bl, br = [new_corners[0, :][0], new_corners[0, :][x_c - 1], new_corners[0, :][-(x_c)],
                          new_corners[0, :][-1]]
        # prj_pts[:, 0] += int(tl[0])  # translate projection points by distance to top left point
        # prj_pts[:, 1] += int(tl[1])

        prj_pts = prj_pts.reshape(1, x_c * y_c, 3).astype(np.float32)

        flat_image = cv2.cvtColor(flat_image, cv2.COLOR_GRAY2BGR)
        cv2.drawChessboardCorners(flat_image, (9, 7), new_corners, 1)  # sum_sqdiff = 0
        # for i in xrange(x_c * y_c):
        #     dist = self.calc_sqdiff(image_pts[0][i][0], image_pts[0][i][1], prj_pts[0][i][0], prj_pts[0][i][1])
        #     sum_sqdiff += dist

        h, _ = cv2.findHomography(new_corners, prj_pts)
        # h[0, 2] *= ratio
        # h[1, 2] *= ratio
        # h[2, 0] /= ratio
        # h[2, 1] /= ratio

        tfm_pts = cv2.perspectiveTransform(np.array([[(0,0)],[(0,res[1])],[(res[0],res[1])],[(res[0],res[1])]],dtype=float), h)
        offset = np.array([[1, 0, -tfm_pts[:,0][:,0].min()], [0, 1, -tfm_pts[:,0][:,1].min()], [0, 0, 1]])  # establish translation offset matrix
        h = np.dot(offset, h)  # Modify homography with translation matrix
        out_h= int(tfm_pts[:,0][:,1].max()-tfm_pts[:,0][:,1].min())
        out_w= int(tfm_pts[:,0][:,0].max()-tfm_pts[:,0][:,0].min())
        outres = np.array([(out_w, out_h)])

        calibrate_params = [h, intr_c, intr_d, outres]

        warp_image = cv2.warpPerspective(flat_image, h, tuple(outres[0]))



        cv2.imwrite('warped.png', warp_image)
        cv2.imwrite('flat.png', flat_image)
        self._save_calibration(calibrate_params)

        return calibrate_params

    @staticmethod
    def calc_sqdiff(x1, y1, x2, y2):
        return (x2 - x1) ** 2 + (y2 - y1) ** 2

    @staticmethod
    def _validate_calibration(reprojection_error):
        if reprojection_error < 5.0:
            valid = True
        else:
            valid = False
        return valid

    def _save_calibration(self, calibrate_params):
        f_id = open('calib_params.dat', 'w')
        for array in calibrate_params:
            array = array.reshape(array.shape[0] * array.shape[1], 1)
            for element in array:
                f_id.write('%s,' % element[0])
        f_id.close()

        return 1


def main():
    c = Calibrate()
    # c.start_calibration()
    # c.run()
    c.calibrate_from_file()


if __name__ == '__main__':
    main()
