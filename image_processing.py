# Import external libraries
import os
import time
import cv2
import numpy as np
import json

# Some global colours are defined here (represented as BGR)
COLOUR_RED = (0, 0, 255)
COLOUR_BLUE = (255, 0, 0)
COLOUR_GREEN = (0, 255, 0)
COLOUR_YELLOW = (0, 255, 255)
COLOUR_PURPLE = (255, 0, 255)
COLOUR_BLACK = (0, 0, 0)
COLOUR_WHITE = (255, 255, 255)


class ImageTransform:
    """Module containing methods used to transform or modify any images using a variety of OpenCV functions"""

    def __init__(self):

        # Load from the config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Checks whether to use the temporary results of the camera calibration, or the ones saved in the config file
        try:
            with open('calibration_results.json') as parameters:
                self.parameters = json.load(parameters)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.parameters = self.config['ImageCorrection']
        else:
            self.parameters = self.parameters['ImageCorrection']

    def apply_transformation(self, image, display_flag):
        """Applies the transformation processes to the received image using the transformation parameters"""

        if display_flag:
            self.transform = self.config['ImageCorrection']['TransformDisplay']
        else:
            self.transform = self.config['ImageCorrection']['TransformContours']

        # Grab the image's width and height (for clearer code purposes)
        self.width = image.shape[1]
        self.height = image.shape[0]

        # Apply all the following transformations
        image = self.flip(image)
        image = self.translate(image)
        image = self.rotate(image)
        image = self.stretch_nw(image)
        image = self.stretch_ne(image)
        image = self.stretch_sw(image)
        image = self.stretch_se(image)

        return image

    def distortion_fix(self, image):
        """Fixes the barrel/pincushion distortion commonly found in pinhole cameras"""

        return cv2.undistort(image, np.array(self.parameters['CameraMatrix']),
                             np.array(self.parameters['DistortionCoefficients']))

    def perspective_fix(self, image):
        """Fixes the perspective warp due to the off-centre position of the camera"""

        return cv2.warpPerspective(image, np.array(self.parameters['HomographyMatrix']),
                                   tuple(self.parameters['Resolution']))

    def crop(self, image):
        """Crops the image to a more desirable region of interest"""

        # Save value to be used to determine region of interest
        boundary = self.config['ImageCorrection']['CropBoundary']

        # Crop the image to a rectangle region of interest as dictated by the following values [H,W]
        return image[boundary[0]: boundary[1], boundary[2]: boundary[3]]

    def flip(self, image):
        """Flip the image around the horizontal or vertical axis"""

        if self.transform[3]:
            image = cv2.flip(image, 1)
        if self.transform[4]:
            image = cv2.flip(image, 0)

        return image

    def translate(self, image):
        """Translate the image in any of the four directions"""

        translation_matrix = np.float32([[1, 0, self.transform[1]], [0, 1, self.transform[0]]])
        return cv2.warpAffine(image, translation_matrix, (self.width, self.height))

    def rotate(self, image):
        """Rotate the image a set amount of degrees in the clockwise or anti-clockwise direction"""

        rotation_matrix = cv2.getRotationMatrix2D((self.width // 2, self.height // 2), self.transform[2], 1)
        return cv2.warpAffine(image, rotation_matrix, (self.width, self.height))

    def stretch_nw(self, image):
        """Stretches/Pulls the image in the north-west direction"""

        points1 = np.float32([[self.width, 0], [0, 0], [0, self.height]])
        points2 = np.float32([[self.width, self.transform[5] + self.transform[12]],
                              [self.transform[8], self.transform[5]],
                              [self.transform[8] + self.transform[13], self.height + self.transform[7]]])
        matrix = cv2.getAffineTransform(points1, points2)

        return cv2.warpAffine(image, matrix, (self.width, self.height))

    def stretch_ne(self, image):
        """Stretches/Pulls the image in the north-east direction"""

        points1 = np.float32([[0, 0], [self.width, 0], [self.width, self.height]])
        points2 = np.float32([[0, self.transform[10]],
                              [self.width + self.transform[6], 0],
                              [self.width + self.transform[6] + self.transform[15], self.height + self.transform[7]]])
        matrix = cv2.getAffineTransform(points1, points2)

        return cv2.warpAffine(image, matrix, (self.width, self.height))

    def stretch_sw(self, image):
        """Stretches/Pulls the image in the south-west direction"""

        points1 = np.float32([[0, 0], [0, self.height], [self.width, self.height]])
        points2 = np.float32([[self.transform[9], 0], [0, self.height], [self.width, self.height + self.transform[16]]])
        matrix = cv2.getAffineTransform(points1, points2)

        return cv2.warpAffine(image, matrix, (self.width, self.height))

    def stretch_se(self, image):
        """Stretches/Pulls the image in the south-east direction"""

        points1 = np.float32([[0, self.height], [self.width, self.height], [self.width, 0]])
        points2 = np.float32(
            [[0, self.height + self.transform[14]], [self.width, self.height], [self.width + self.transform[11], 0]])
        matrix = cv2.getAffineTransform(points1, points2)
        return cv2.warpAffine(image, matrix, (self.width, self.height))

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


class DefectDetector:
    """Module used to process the corrected images using OpenCV functions to detect a variety of different defects
    Defects to be analyzed are outlined in the README.txt file
    Throughout the code, image objects are named image_(purpose)_(modification *default=BGR)
    Therefore an image that will contain defect pixels that has been converted to gray would be image_defects_gray
    """

    def __init__(self):

        # Load from the build.json file
        with open('build.json') as build:
            self.build = json.load(build)

        # Load from the config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Store some important variable names to be used in later methods
        self.layer = str(self.build['DefectDetector']['Layer']).zfill(4)
        self.phase = self.build['DefectDetector']['Phase']
        self.part_colours = self.build['BuildInfo']['Colours']

        # This is the master defect dictionary which stores all the defect results for all the parts
        self.defects = dict()

        # Open all the reports and save their dictionaries to the master defect dictionary
        # These dictionaries will be overwritten with new data should the program process the same layer/part
        for name in self.part_colours.keys():
            with open('%s/reports/%s_report.json' % (self.build['ImageCapture']['Folder'], name)) as report:
                self.defects[name] = json.load(report)

            # The dictionary needs to be built up if it doesn't already exist
            if self.layer not in self.defects[name]:
                self.defects[name][self.layer] = dict()
                self.defects[name][self.layer]['scan'] = dict()
                self.defects[name][self.layer]['coat'] = dict()

        # Because blade streaks and blade chatter rely on number of occurrences rather than pixel size
        self.chatter_count = 0
        self.streak_count = 0

    def run_detector(self, status, progress, notification):
        """Initial run method that decides whether to run the coat or scan collection of detection processes"""

        # Assign the status, progress and notification signals as instance variables so other methods can use them
        self.status = status
        self.progress = progress
        self.notification = notification
        self.progress.emit(0)

        # Load the image to be analyzed into memory
        image = cv2.imread(self.build['DefectDetector']['Image'])

        # Grab the total number of pixels in the image
        self.total_pixels = image.size / 3

        # Create a blank black RGB image the same size as the raw image to draw the defects on
        image_blank = np.zeros(image.shape, np.uint8)

        # Different detection methods will be applied depending on the marked phase (coat, scan or single)
        if 'coat' in self.phase:
            self.analyze_coat(image, image_blank)
        elif 'scan' in self.phase:
            self.analyze_scan(image, image_blank)

        # Save all the reports to their respective json files
        for name in self.part_colours.keys():
            with open('%s/reports/%s_report.json' % (self.build['ImageCapture']['Folder'], name), 'w+') as report:
                json.dump(self.defects[name], report, sort_keys=True)

        self.progress.emit(100)

    def analyze_coat(self, image_coat, image_blank):
        """Analyzes the coat image for any potential defects as listed in the order below"""

        # TODO Remove timers when not needed
        t0 = time.time()

        # Blade streak defects will be drawn in red
        self.detect_blade_streak(image_coat, image_blank.copy())
        self.progress.emit(20)

        print('Blade Streak\n%s' % (time.time() - t0))

        # Blade chatter defects will be drawn in blue
        self.detect_blade_chatter(image_coat, image_blank.copy())
        self.progress.emit(40)

        print('Blade Chatter\n%s' % (time.time() - t0))

        # Bright spot defects will be drawn in green
        self.detect_shiny_patch(image_coat, image_blank.copy())
        self.progress.emit(60)

        print('Shiny Patch\n%s' % (time.time() - t0))

        # Contrast difference defects will be drawn in yellow
        self.detect_contrast_outlier(image_coat, image_blank.copy())
        self.progress.emit(80)

        print('Contrast Outlier\n%s' % (time.time() - t0))

        # Histogram comparison with the previous layer if the previous layer's image exists
        if os.path.isfile(self.build['DefectDetector']['ImagePrevious']):
            image_previous = cv2.imread(self.build['DefectDetector']['ImagePrevious'])
            self.compare_histogram(image_coat, image_previous)

        # Compare all the results against the threshold values to see if any are outside of the threshold

        print('Compare & Save\n%s\n' % (time.time() - t0))

    def analyze_scan(self, image_scan, image_blank):
        """Analyzes the scan image for any potential defects as listed in the order below"""

        # TODO remove timers if not needed
        t0 = time.time()

        # Blade streak defects will be drawn in red
        self.detect_blade_streak(image_scan, image_blank.copy())
        self.progress.emit(25)

        print('Blade Streak\n%s' % (time.time() - t0))

        # Blade chatter defects will be drawn in blue
        self.detect_blade_chatter(image_scan, image_blank.copy())
        self.progress.emit(50)

        print('Blade Chatter\n%s' % (time.time() - t0))

        # Scan pattern will be drawn in purple
        self.scan_detection(image_scan, image_blank.copy())
        self.progress.emit(75)

        print('Scan Detection\n%s' % (time.time() - t0))

        # Histogram comparison with the previous layer if the previous layer's image exists
        if os.path.isfile(self.build['DefectDetector']['ImagePrevious']):
            image_previous = cv2.imread(self.build['DefectDetector']['ImagePrevious'])
            self.compare_histogram(image_scan, image_previous)

        print('Compare & Save\n%s\n' % (time.time() - t0))

    def check_results(self):
        """Checks the results of the defect analysis and sends a notification if any don't meet the threshold values"""
        pass

    def detect_blade_streak(self, image, image_defects):
        """Detects any horizontal lines on the image, doesn't work as well in the darker areas"""

        # Apply CLAHE equalization to the raw image
        image = ImageTransform.clahe(image, gray_flag=True)

        # Add a gaussian blur to the CLAHE image
        image = cv2.GaussianBlur(image, (15, 15), 0)

        # Use a Sobel edge finder to find just the edges in the X plane (horizontal lines)
        image_edges = cv2.Sobel(image, cv2.CV_8UC1, 0, 1)

        # Remove any unclear or ambiguous results (that show up as noise), leaving only the distinct edges
        image_edges = cv2.threshold(image_edges, 20, 255, cv2.THRESH_BINARY)[1]
        image_edges = cv2.dilate(image_edges, np.ones((1, 20), np.uint8), iterations=1)
        image_edges = cv2.erode(image_edges, np.ones((1, 20), np.uint8), iterations=3)

        # Create a list consisting of 2 points that forms a line matching the variables
        lines = cv2.HoughLinesP(image_edges, 1, np.pi / 180, threshold=100, minLineLength=1000, maxLineGap=500)

        # Draw red lines (representing the blade streaks) on the blank image if lines were found
        if lines is not None:
            if lines.size > 0:
                for index in range(len(lines)):
                    for x1, y1, x2, y2 in lines[index]:
                        # Only draw horizontal lines that are not located near the top or bottom of image
                        if abs(y1 - y2) == 0 and 20 < y1 < image_defects.shape[0] - 20:
                            cv2.line(image_defects, (x1, y1), (x2, y2), COLOUR_RED, 2)
                            self.streak_count += 1

        # Save the found defects to the corresponding report
        self.report_defects(image_defects, COLOUR_RED, 'BS')

        # Save the image with the defects on it to the corresponding folder
        cv2.imwrite('%s/defects/%s/streaks/%sBS_%s.png' % (self.build['ImageCapture']['Folder'], self.phase, self.phase,
                                                           self.layer), image_defects)

    def detect_blade_chatter(self, image, image_defects):
        """Detects any vertical lines on the image that are caused as a result of blade chatter
        Done by matching any chatter against a pre-collected set of blade chatter templates"""

        # Apply CLAHE equalization to the raw image
        image = ImageTransform.clahe(image, gray_flag=True, cliplimit=3.0, tilegridsize=(12, 12))

        # Iterate through all the chatter templates in the template folder
        for filename in os.listdir('templates'):

            # Load the template image into memory in grayscale
            template = cv2.imread('templates/%s' % filename, 0)

            # Look for the template in the original image using matchTemplate
            result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

            # Find the coordinates of the results which are above a set threshold
            coordinates = np.where(result >= 0.4)
            coordinate_previous = [0, 0]

            # Draw a blue box around the matching points if found
            for coordinate in zip(*coordinates[::-1]):
                # This conditional prevents stacking of multiple boxes on the one spot due to a low threshold value
                if abs(coordinate[1] - coordinate_previous[1]) > 50:
                    cv2.rectangle(image_defects, (coordinate[0], coordinate[1]),
                                  (coordinate[0] + template.shape[1], coordinate[1] + template.shape[0]),
                                  COLOUR_BLUE, thickness=3)
                    coordinate_previous = coordinate
                    self.chatter_count += 1

        # Save the found defects to the corresponding report
        self.report_defects(image_defects, COLOUR_BLUE, 'BC')

        # Save the image with the defects on it to the corresponding folder
        cv2.imwrite('%s/defects/%s/chatter/%sBC_%s.png' % (self.build['ImageCapture']['Folder'], self.phase, self.phase,
                                                           self.layer), image_defects)

    def detect_shiny_patch(self, image, image_defects):
        """Detects any patches in the image that are above a certain contrast threshold, aka are too shiny"""

        # Apply CLAHE equalization to the raw image
        image = ImageTransform.clahe(image, gray_flag=True)

        # Otsu's Binarization is used to calculate a threshold value to be used to get a proper threshold image
        retval = cv2.threshold(image, 0, 255, cv2.THRESH_OTSU)[0]
        image_threshold = cv2.threshold(image, retval * 1.85, 255, cv2.THRESH_BINARY)[1]

        # Change the colour of the pixels in the blank image to green if they're above the threshold
        image_defects[image_threshold == 255] = COLOUR_GREEN

        self.report_defects(image_defects, COLOUR_GREEN, 'SP')

        # Save the image with the defects on it to the corresponding folder
        cv2.imwrite('%s/defects/%s/patches/%sSP_%s.png' % (self.build['ImageCapture']['Folder'], self.phase, self.phase,
                                                           self.layer), image_defects)

    def detect_contrast_outlier(self, image, image_defects):
        """Detects any areas of the image that are too bright or dark compared to the average contrast
        Use this until detect_dark_spots is fixed and working sufficiently"""

        # Otsu's Binarization is used to calculate a threshold value and image using the raw grayscale image
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        retval, image_threshold = cv2.threshold(image_gray, 0, 255, cv2.THRESH_OTSU)

        # Clean up the image threshold by removing any noise (opening/closing holes)
        kernel = cv2.getStructuringElement(cv2.MORPH_ERODE, (5, 5))
        image_threshold = cv2.erode(image_threshold, kernel, iterations=3)
        for index in range(7):
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * index + 1, 2 * index + 1))
            image_threshold = cv2.morphologyEx(image_threshold, cv2.MORPH_CLOSE, kernel, iterations=3)
            image_threshold = cv2.morphologyEx(image_threshold, cv2.MORPH_OPEN, kernel, iterations=3)

        # image_white is the section of image_defects that are white in the created threshold
        # image_black is the opposite
        image_white = cv2.bitwise_and(image, image, mask=image_threshold)
        image_black = cv2.bitwise_and(image, image, mask=cv2.bitwise_not(image_threshold))

        # Ignore the right edge of the build platform (defects there don't matter)
        image_black[:, image.shape[1] - 20:] = COLOUR_BLACK

        # Outer ring bright spots, set these in the defect image to yellow
        image_outer = cv2.threshold(image_black, retval * 1.32, 255, cv2.THRESH_BINARY)[1]
        image_defects[np.where((image_outer == COLOUR_WHITE).all(axis=2))] = COLOUR_YELLOW

        # Outer ring shadows
        image_outer_shadow = cv2.threshold(image_black, retval * 0.7, 255, cv2.THRESH_BINARY_INV)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_ERODE, (5, 5))
        image_outer_shadow = cv2.erode(image_outer_shadow, kernel, iterations=5)
        image_outer_shadow = cv2.bitwise_or(image_defects, image_outer_shadow)
        image_outer_shadow = cv2.threshold(image_outer_shadow, retval * 0.5, 255, cv2.THRESH_TOZERO_INV)[1]
        image_defects[np.where((image_outer_shadow != COLOUR_BLACK).all(axis=2))] = COLOUR_YELLOW
        image_defects[np.where((image_black == COLOUR_WHITE).all(axis=2))] = COLOUR_YELLOW

        # Inner ring bright spots
        image_inner = cv2.threshold(image_white, retval * 1.7, 255, cv2.THRESH_BINARY)[1]
        image_defects[np.where((image_inner == COLOUR_WHITE).all(axis=2))] = COLOUR_YELLOW

        # Inner ring shadows
        image_inner_shadow = cv2.threshold(image_white, retval * 0.95, 255, cv2.THRESH_TOZERO_INV)[1]
        image_defects[np.where((image_inner_shadow != COLOUR_BLACK).all(axis=2))] = COLOUR_YELLOW

        self.report_defects(image_defects, COLOUR_YELLOW, 'CO')

        # Save the image with the defects on it to the corresponding folder
        cv2.imwrite('%s/defects/%s/outliers/%sCO_%s.png' % (self.build['ImageCapture']['Folder'], self.phase, self.phase,
                                                           self.layer), image_defects)

    def scan_detection(self, image, image_defects):
        """Detects any scan patterns on the image and draws them as filled contours"""

        # Try to detect the edges using Laplacian after converting to grayscale and blurring the image
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.GaussianBlur(image, (27, 27), 0)
        image_edges = cv2.Laplacian(image, cv2.CV_64F)

        for index in range(3):
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * index + 1, 2 * index + 1))
            image_edges = cv2.morphologyEx(image_edges, cv2.MORPH_CLOSE, kernel)
            image_edges = cv2.morphologyEx(image_edges, cv2.MORPH_OPEN, kernel)

        # image_edges = cv2.morphologyEx(image_edges, cv2.MORPH_CLOSE, kernel, iterations=3)
        # image_edges = cv2.erode(image_edges, cv2.getStructuringElement(cv2.MORPH_ERODE, (5, 5)), iterations=1)
        image_edges = cv2.convertScaleAbs(image_edges)

        # Find the contours using the cleaned up image
        contours = cv2.findContours(image_edges, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)[1]
        contours_list = list()

        # Check if the contours are larger than a preset threshold
        for contour in contours:
            if cv2.contourArea(contour) > 1000:
                contours_list.append(contour)

        # Draw the contours on the defect image in purple
        cv2.drawContours(image_defects, contours_list, -1, COLOUR_PURPLE, thickness=cv2.FILLED)

        # Compare the detected scan pattern against the drawn contours
        if os.path.isfile(self.build['DefectDetector']['Contours']):
            image_contours = cv2.imread(self.build['DefectDetector']['Contours'])

            # Convert all the part colours from teal into purple so that it can be compared to the detected scan pattern
            mask = cv2.inRange(image_contours, (100, 100, 0), (255, 255, 0))
            image_contours[np.nonzero(mask)] = COLOUR_PURPLE

            # Use template matching to directly compare the two images and save the result to the combined report
            result = cv2.matchTemplate(image_defects, image_contours, cv2.TM_CCOEFF_NORMED)[0][0]
            self.defects['combined'][self.layer][self.phase]['OC'] = float(result)

        # Save the image with the defects on it to the corresponding folder
        cv2.imwrite('%s/defects/%s/pattern/%sOC_%s.png' % (self.build['ImageCapture']['Folder'], self.phase, self.phase,
                                                           self.layer), image_defects)

    def compare_histogram(self, image_current, image_previous):
        """Compares the histogram of each method and calculates the difference result"""

        hist_current = cv2.calcHist([image_current], [0], None, [256], [0, 256])
        hist_previous = cv2.calcHist([image_previous], [0], None, [256], [0, 256])

        # To be tested to see if this improves or does anything to the result
        # cv2.normalize(hist_current, hist_current)
        # cv2.normalize(hist_previous, hist_previous)

        # Lots of methods to compare histograms and to calculate histograms itself
        # To be further tested for the best options
        result = cv2.compareHist(hist_current, hist_previous, cv2.HISTCMP_KL_DIV)

        # Result of KL_DIV comparing a completely black image to a completely white image - 325853401.3861952
        # Converting the result to a percentage based on this complete non-match number
        # result = (325853401.3861952 - result) / 325853401.3861952 * 100

        # Save the result directly to the combined report
        self.defects['combined'][self.layer][self.phase]['HC'] = result

    def report_defects(self, image_defects, defect_colour, defect_type):
        """Report the size and coordinates of any defects that overlay any of the part contours and the background"""

        # Report the combined defects first by comparing to a blank image
        # This process will always happen regardless if a contour image exists or not
        image_blank = np.zeros(image_defects.shape, np.uint8)
        size, coordinates, occurrences = self.find_coordinates(image_defects, image_blank, COLOUR_BLACK, defect_colour)

        # Save the results to the defect dictionary
        if size > 0:
            self.defects['combined'][self.layer][self.phase][defect_type] = [size, occurrences] + coordinates
        else:
            self.defects['combined'][self.layer][self.phase][defect_type] = [0, 0]

        # Only report defects that intersect the part contours if the image exists
        if os.path.isfile(self.build['DefectDetector']['Contours']):
            image_contours = cv2.imread(self.build['DefectDetector']['Contours'])

            for part_name, part_colour in self.part_colours.items():
                # Skip the combined key as it has already been processed
                if 'combined' in part_name:
                    continue

                # Find the total size, coordinates and occurrences of the defect pixels that overlap the part
                size, coordinates, occurrences = self.find_coordinates(image_defects, image_contours,
                                                                       tuple(part_colour), defect_colour)

                # Convert the pixel size data into a percentage based on the total number of pixels in the image
                if 'SP' in defect_type or 'CO' in defect_type:
                    size = round(size / self.total_pixels * 100, 4)

                if size > 0:
                    # Add these to the defect dictionary for the current part, and the combined dictionary
                    self.defects[part_name][self.layer][self.phase][defect_type] = [size, occurrences] + coordinates
                else:
                    self.defects[part_name][self.layer][self.phase][defect_type] = [0, 0]

    def compare_threshold(self):
        """Compares the results to the threshold values to check if a notification needs to be raised or not"""

        # Grabs the data for clearer code purposes
        data = self.defects['combined'][self.layer][self.phase]

        if 'coat' in self.phase:
            # Grab the threshold values from the config.json file
            threshold = [self.config['Threshold']['Occurrences'], self.config['Threshold']['Occurrences'],
                         self.config['Threshold']['PixelSize'], self.config['Threshold']['PixelSize'],
                         self.config['Threshold']['HistogramCoat']]

            # Format the appropriate data into a list
            data_coat = [data['BS'][1], data['BC'][1], data['SP'][0], data['CO'][0], data['HC']]

        elif 'scan' in self.phase:
            threshold = [self.config['Threshold']['Occurrences'], self.config['Threshold']['Occurrences'],
                         self.config['Threshold']['HistogramScan'], self.config['Threshold']['Overlay']]
            data_scan = [data['BS'][1], data['BC'][1], data['HC'], data['OC']]

    @staticmethod
    def find_coordinates(image_defects, image_overlay, part_colour, defect_colour):
        """Determines the coordinates of any defects (coloured pixels) and whether they overlap with the part contours
        Because reporting the coordinates of every pixel will yield an incredibly long list...
        The centre coordinates of each 'defect blob' is reported instead"""

        # Create a mask of each part using their respective colour
        mask = cv2.inRange(image_overlay, part_colour, part_colour)

        # Because the colour causes some noise in the mask due to gradients, close and remove any white noise
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))

        # Overlay the defect image with the created mask of the part in question
        image_overlap = cv2.bitwise_and(image_defects, image_defects, mask=mask)

        # Find all the coloured defect pixels in the overlap image (outputs an image of the red pixels)
        image_overlap = cv2.inRange(image_overlap, defect_colour, defect_colour)

        # Find the number of overlapping pixels as outputted by the above function
        size = cv2.countNonZero(image_overlap)

        # Group any large blobs of red pixels and find the contours of them
        contours = cv2.findContours(image_overlap, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]

        # Initialize a few objects
        coordinates = list()
        occurrences = 0

        # For each contour found, if the size of the contour exceeds a certain amount, find its centre coordinates
        for contour in contours:
            if cv2.contourArea(contour) > 50:
                (x, y) = cv2.minEnclosingCircle(contour)[0]
                coordinates.append((int(x), int(y)))
                occurrences += 1

        return size, coordinates, occurrences

    @staticmethod
    def defect_size(image):
        """Returns the number of pixels that fall between the set range of colours"""
        return cv2.countNonZero(cv2.inRange(image, np.array([0, 0, 200]), np.array([100, 100, 255])))

    @staticmethod
    def overlay_defects(image, image_defects, defect_colour):
        """Applies any solid defect pixel colours (depending on the defect being overlaid) to the first image"""
        image_mask = cv2.inRange(image_defects, defect_colour, defect_colour)
        if cv2.countNonZero(image_mask) > 0:
            image[np.nonzero(image_mask)] = defect_colour
        return image
