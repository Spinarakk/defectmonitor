# Import external libraries
import os
import json
import cv2
import numpy as np

# Some global colours are defined here
COLOUR_BLACK = np.array((0, 0, 0))
COLOUR_WHITE = np.array((255, 255, 255))
COLOUR_RED = np.array((0, 0, 255))
COLOUR_BLUE = np.array((255, 0, 0))


class ImageTransform:
    """Module containing methods used to transform or modify any images using a variety of OpenCV functions"""

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

    @staticmethod
    def transform(image, transform):

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
    def clahe(image, gray_flag=False, cliplimit=8.0, tilegridsize=(64, 64)):
        """Applies a Contrast Limited Adaptive Histogram Equalization to the image
        Used to improve the contrast of the image to make it clearer/visible
        The gray flag is used to indicate if the image is to be converted back to BGR or not
        """

        # Equalization algorithm requires the image to be in grayscale colour space to function
        # This line checks if the image is already grayscale or in RGB (BGR)
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # CLAHE filter functions
        clahe_filter = cv2.createCLAHE(cliplimit, tilegridsize)
        image = clahe_filter.apply(image)

        # Convert the image back to BGR as when converting to a QPixmap, grayscale images don't work
        if not gray_flag:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        return image


class DefectDetection:
    """Module used to process the corrected images using OpenCV functions to detect a variety of different defects
    Defects to be analyzed are outlined in the README.txt file"""

    def __init__(self):

        # Load configuration settings from config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        self.image = cv2.imread(self.config['DefectDetection']['Image'])
        self.image_overlay = cv2.imread(self.config['DefectDetection']['Overlay'])
        self.image_analyzed = self.image.copy()

        self.defects = dict()

        self.defects_on = {'Bright Spots': [], 'Blade Streaks': [], 'Blade Chatter': [], 'Contrast Differences': []}
        self.defects_off = {'Bright Spots': [], 'Blade Streaks': [], 'Blade Chatter': [], 'Contrast Differences': []}

        self.layer = self.config['DefectDetection']['Layer']
        self.phase = self.config['DefectDetection']['Phase']

        self.part_colours = self.config['BuildInfo']['Colours']

        for part_name in self.part_colours:
            self.defects[part_name] = {'Bright Spots': [], 'Blade Streaks': [], 'Blade Chatter': [], 'Contrast Differences': []}

        self.contour_color = np.array((128, 128, 0))
        self.image_previous = None

    def analyze_coat(self):
        """Analyzes the coat image for any potential defects as listed below"""

        self.detect_bright_spots()
        self.detect_blade_streaks()
        self.detect_blade_chatter()
        self.detect_contrast()

        if self.image_previous is not None:
            self.compare_histogram()
        self.image_previous = self.image_analyzed
        cv2.add(self.image_analyzed, self.image_overlay, dst=self.image_analyzed)

        report = open('report.txt', 'a+')
        report.writelines('Layer %s:\n'
                          '-----------\n' % self.layer)
        if not self.defects_on and not self.defects_off:
            report.write('No defects found \n')
        else:
            cv2.imwrite('%s/defects/coat/layer_%s.jpg' % (self.config['ImageCapture']['Folder'], self.layer),
                        self.image_analyzed)
            if self.defects_on:
                report.write('Possible overlapping defects: \n')
                for key in self.defects_on:
                    if len(self.defects_on[key]) > 0:
                        report.write('\t%s at position(s): %s \n' % (key, self.defects_on[key][0]))
            if self.defects_off:
                report.write('Other possible defects: \n')
                for key in self.defects_off:
                    if len(self.defects_off[key]) > 0:
                        report.write('\t%s at position(s): %s \n' % (key, self.defects_off[key][0]))
            report.write('Total defect size (pixels): %s \n' % self.defect_size(self.image_analyzed))
        report.write('\n\n')
        report.close()

    def analyze_scan(self):
        pass

    def detect_bright_spots(self):
        """Detects any spots in the image that are above a certain contrast threshold, aka are too bright"""

        image_defects = self.image.copy()
        image_clahe = ImageTransform.clahe(image_defects, gray_flag=True)

        # Otsu's Binarization is used to calculate a threshold value to be used to get a proper threshold image
        retval = cv2.threshold(image_clahe, 0, 255, cv2.THRESH_OTSU)[0]
        image_threshold = cv2.threshold(image_clahe, retval * 1.85, 255, cv2.THRESH_BINARY)[1]

        # Change the colour of the pixels in the original image to red if they're above the threshold
        image_defects[image_threshold == 255] = COLOUR_RED

        # Check if the size of the defects (number of pixels) is above a set threshold
        if self.defect_size(image_defects) > 0:
            # For each part, find the coordinates of the defect pixels that overlap the part
            for part_name, colour in self.part_colours.items():
                self.defects[part_name]['Bright Spots'] = \
                    self.find_coordinates(image_defects, self.image_overlay, colour)
            # Also find the coordinates of the defect pixels that don't overlap any parts
            self.defects['Background']['Bright Spots'] = \
                self.find_coordinates(image_defects, self.image_overlay, colour, overlap_flag=False)

        self.overlay_defects(self.image_analyzed, image_defects)

    def detect_blade_streaks(self):
        """Detects any horizontal lines on the image, doesn't work as well in the darker areas"""

        image_defects = self.image.copy()
        eq = self.clahe(image_defects)
        cv2.GaussianBlur(eq, (15, 15), 0, dst=eq)
        # Sobelx edge finder
        #                                 y  x
        edge = cv2.Sobel(eq, cv2.CV_8UC1, 0, 1)
        # taking out the unclear ones
        cv2.threshold(edge, 20, 255, cv2.THRESH_BINARY, dst=edge)
        kernel = np.ones((1, 20), np.uint8)  # HORIZONTAL kernel
        cv2.dilate(edge, kernel, iterations=1, dst=edge)
        cv2.erode(edge, kernel, iterations=3, dst=edge)
        # a list consisting 2 points that forms a line matching the variables
        lines = cv2.HoughLinesP(edge, 1, np.pi / 180, threshold=100, minLineLength=1000, maxLineGap=500)
        height = image_defects.shape[0]
        for x in range(0, len(lines)):
            for x1, y1, x2, y2 in lines[x]:
                # only draw horizontal lines that are not located at top or bottom of image
                if abs(y1 - y2) == 0 and 20 < y1 < height - 20:
                    cv2.line(image_defects, (x1, y1), (x2, y2), COLOUR_RED, 2)
        if self.defect_size(image_defects) > 0:
            coordinates_on, coordinates_off = self.find_coordinates(image_defects, self.contour_color)
            if len(coordinates_on) > 0:
                self.defects_on['Blade Streaks'].append(coordinates_on)
            if len(coordinates_off) > 0:
                self.defects_off['Blade Streaks'].append(coordinates_off)
        self.overlay_defects(self.image_analyzed, image_defects)

    def detect_blade_chatter(self):
        """Detects any vertical lines on the image that are caused as a result of blade chatter"""

        image_defects = self.image.copy()

        gray = cv2.cvtColor(image_defects, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(12, 12))
        eq = clahe.apply(gray)
        templates = []
        for i in range(5):
            temp = cv2.imread('defect%s.png' % str(i + 1), cv2.IMREAD_GRAYSCALE)
            templates.append(temp)
        for templ in templates:
            h, w = templ.shape
            result = cv2.matchTemplate(eq, templ, cv2.TM_CCOEFF_NORMED)
            #                      threshold value
            #                             v
            points = np.where(result >= 0.4)
            prev = [0, 0]
            # draws box around where the matches were found
            for pt in zip(*points[::-1]):
                # prevents stacking of multiple boxes on one spot due to low threshold
                if abs(pt[1] - prev[1]) > 50:
                    cv2.rectangle(image_defects, (pt[0], pt[1]), (pt[0] + w, pt[1] + h), (0, 0, 255), thickness=3)
                    prev = pt
        if self.defect_size(image_defects) > 0:
            coordinates_on, coordinates_off = self.find_coordinates(image_defects, self.contour_color)
            if len(coordinates_on) > 0:
                self.defects_on['Blade Chatter'].append(coordinates_on)
            if len(coordinates_off) > 0:
                self.defects_off['Blade Chatter'].append(coordinates_off)
        self.overlay_defects(self.image_analyzed, image_defects)

    # Uses the retval produced by THRESH_OTSU as average intensity
    # and detects any area too bright or too dark compared to their average
    # Use this until detect_dark_spot() is fixed
    def detect_contrast(self):
        """Detects any areas of the image that are too bright or dark compared to the average contrast
        Use this until detect_darkspots is fixed and working sufficiently"""

        image_defects = self.image.copy()

        width = image_defects.shape[1]

        # The return value as produced by the otsu thresholding is used as the average light intensity
        retval, dark, light = self.split_otsu()
        dark[:, width - 20:] = [0, 0, 0]  # not counting the edge of build platform
        # Bright Spots of outer ring
        _, outer = cv2.threshold(dark, retval * 1.32, 255, cv2.THRESH_BINARY)
        image_defects[np.where((outer == COLOUR_WHITE).all(axis=2))] = COLOUR_RED
        # shadows of outer ring
        _, shadow_outer = cv2.threshold(dark, retval * 0.7, 255, cv2.THRESH_BINARY_INV)
        kernel = cv2.getStructuringElement(cv2.MORPH_ERODE, (5, 5))
        cv2.erode(shadow_outer, kernel, dst=shadow_outer, iterations=5)
        cv2.bitwise_or(image_defects, shadow_outer, dst=shadow_outer)
        _, shadow_outer = cv2.threshold(shadow_outer, retval * 0.5, 255, cv2.THRESH_TOZERO_INV)
        image_defects[np.where((shadow_outer != COLOUR_BLACK).all(axis=2))] = COLOUR_RED
        image_defects[np.where((dark == COLOUR_WHITE).all(axis=2))] = COLOUR_RED
        # Bright Spotss of inner circle
        _, center = cv2.threshold(light, retval * 1.7, 255, cv2.THRESH_BINARY)
        image_defects[np.where((center == COLOUR_WHITE).all(axis=2))] = COLOUR_RED
        # shadows of inner circle
        _, shadow_inner = cv2.threshold(light, retval * 0.95, 255, cv2.THRESH_TOZERO_INV)
        image_defects[np.where((shadow_inner != COLOUR_BLACK).all(axis=2))] = COLOUR_RED
        if self.defect_size(image_defects) > 0:
            coordinates_on, coordinates_off = self.find_coordinates(image_defects, self.contour_color)
            if len(coordinates_on) > 0:
                self.defects_on['Contrast Differences'].append(coordinates_on)
            if len(coordinates_off) > 0:
                self.defects_off['Contrast Differences'].append(coordinates_off)
        self.overlay_defects(self.image_analyzed, image_defects)

    def set_contour_color(self, color):
        self.contour_color = color

    def overlay_defects(self, image, image_defects):

        mask = cv2.inRange(image_defects, COLOUR_RED, COLOUR_RED)
        if cv2.countNonZero(mask) > 0:
            image[np.nonzero(mask)] = COLOUR_RED

    def split_otsu(self):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        # retval: value used in OTSU method, average brightness of image
        retval, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_ERODE, (5, 5))
        cv2.erode(threshold, kernel, dst=threshold, iterations=3)
        for i in range(7):
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * i + 1, 2 * i + 1))
            threshold = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, kernel, iterations=3)
            threshold = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel, iterations=3)
        light = cv2.bitwise_and(self.image, self.image, mask=threshold)
        threshold_inv = cv2.bitwise_not(threshold)
        dark = cv2.bitwise_and(self.image, self.image, mask=threshold_inv)
        return retval, dark, light

    @staticmethod
    def clahe(image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        clahe_filter = cv2.createCLAHE(8.0, (64, 64))
        image = clahe_filter.apply(image)
        return image

    # should work better if able to mask out corners
    def detect_dosing_error(self):
        image_defects = self.image.copy()
        retval = self.split_otsu()[0]
        width = image_defects.shape[1]
        _, threshold = cv2.threshold(image_defects, retval * 0.6, 255, cv2.THRESH_BINARY_INV)
        threshold[:, :width / 2] = [0, 0, 0]
        image_defects[np.where((threshold == COLOUR_WHITE).all(axis=2))] = COLOUR_RED
        pass
        self.overlay_defects(self.image_analyzed, image_defects)

    # compares the difference of brightness of two images
    # checks sudden change in brightness between two layers
    def compare_histogram(self):
        #                                         channels      size    range(from 0-255)
        #                                            v           v        v
        hist1 = cv2.calcHist([self.image_previous], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([self.image], [0], None, [256], [0, 256])
        # returns a number between 0 and 1, with 1 being 100% similar
        result = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        # 95% similarity is currently a good line
        if result < 0.95:
            pass

    @staticmethod
    def find_coordinates(image_defects, image_overlay, part_colour, overlap_flag=True):
        """Determines the coordinates of any defects (red pixels) and whether they overlap with the part contours
        Because reporting the coordinates of every pixel will yield an incredibly long list...
        The centre coordinates of each 'defect blob' is reported instead"""

        if overlap_flag:
            # Create a mask of each part using their respective colour
            mask = cv2.inRange(image_overlay, part_colour, part_colour)
            # Because the colour causes some noise in the mask due to gradients, close and remove any white noise
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
        else:
            # Create a mask of the black background without the parts on it
            mask = cv2.inRange(image_overlay, (0, 0, 0), (0, 0, 0))

        # Overlay the defect image with the created mask of the part in question
        image_overlap = cv2.bitwise_and(image_defects, image_defects, mask=mask)

        # Find all the defect red pixels in the overlap image (outputs an image of the red pixels)
        image_overlap = cv2.inRange(image_overlap, COLOUR_RED, COLOUR_RED)

        # Group any large blobs of red pixels and find the contours of them
        contours = cv2.findContours(image_overlap, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]

        # For each contour found, if the size of the contour exceeds a certain amount, find its centre coordinates
        coordinates = list()
        for contour in contours:
            if cv2.contourArea(contour) > 50:
                (x, y) = cv2.minEnclosingCircle(contour)[0]
                coordinates.append((int(x), int(y)))

        return coordinates

    @staticmethod
    def defect_size(image):
        """Returns the number of pixels that fall between the set range of colours"""
        return cv2.countNonZero(cv2.inRange(image, np.array([0, 0, 200]), np.array([100, 100, 255])))

    @staticmethod
    def split_colour(image, colour):
        """Returns two images, one of just the received colour and one of the background without the colour"""

        mask = cv2.inRange(image, colour, colour)
        foreground = cv2.bitwise_and(image, image, mask=mask)
        background = cv2.bitwise_and(image, image, mask=cv2.bitwise_not(mask))
        return foreground, background

    # TODO To be fixed, improved, tested and implemented
    def detect_darkspots(self):
        """Also picks up dark areas caused by uneven or bad lighting"""
        image_defects = self.image.copy()
        eq = self.clahe(image_defects)
        retval = cv2.threshold(eq, 0, 255, cv2.THRESH_OTSU)[0]
        _, threshold = cv2.threshold(eq, retval * 0.25, 255, cv2.THRESH_BINARY_INV)
        image_defects[threshold == 255] = COLOUR_RED
        self.overlay_defects(self.image_analyzed, image_defects)

        # # checks if the defect overlaps with scan
        # # change color= if uses different color for layer contour
        # def slice_overlap(self, defect, color=(128, 128, 0)):
        #     # creates a mask containing only the scan lines
        #     mask = cv2.inRange(self.layer, color, color)
        #     # getting the part of defect image that overlaps with the layout
        #     overlay = cv2.bitwise_and(defect, defect, mask=mask)
        #     # find all pixels that are red
        #     found = cv2.inRange(overlay, COLOR_RED, COLOR_RED)
        #     return cv2.countNonZero(found) > 10


class DefectDetasection:
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
        image_clahe = ImageTransform.clahe(image_defects)
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




