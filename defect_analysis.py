import numpy as np
import cv2
import json
import copy

COLOUR_BLACK = np.array((0, 0, 0))
COLOUR_WHITE = np.array((255, 255, 255))
COLOUR_RED = np.array((0, 0, 255))
COLOUR_BLUE = np.array((255, 0, 0))


class DefectDetection:
    def __init__(self):
        
        # Load configuration settings from config.json file
        with open('config.json') as config:
            self.config = json.load(config)
        
        self.image = cv2.imread(self.config['DefectDetection']['Image'])
        self.image_overlay = cv2.imread(self.config['DefectDetection']['Overlay'])
        self.image_analyzed = self.image.copy()
        
        self.defects_on = {'Bright Spots': [], 'Blade Streaks': [], 'Blade Chatter': [], 'Contrast Differences': []}
        self.defects_off = {'Bright Spots': [], 'Blade Streaks': [], 'Blade Chatter': [], 'Contrast Differences': []}

        self.layer = self.config['DefectDetection']['Layer']
        self.phase = self.config['DefectDetection']['Phase']
        
        self.contour_color = np.array((128, 128, 0))
        self.image_previous = None


    # only works good on coats
    def analyze_coat(self):

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
            # if os._exists('defects'):
            #     os.mkdir('defects')
            # add argument [cv2.CV_IMWRITE_JPEG_QUALITY, x] to change quality of image
            # where x has a range from 0-100(higher = better quality), default is at 95
            cv2.imwrite('%s/defects/coat/layer_%s.jpg' % (self.config['ImageCapture']['Folder'], self.layer), self.image_analyzed)
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

    def detect_bright_spots(self):
        """Detects the spots in the image that are above a certain threshold"""
        image_defects = self.image.copy()
        eq = self.clahe(image_defects)
        retval = cv2.threshold(eq, 0, 255, cv2.THRESH_OTSU)[0]
        _, threshold = cv2.threshold(eq, retval*1.85, 255, cv2.THRESH_BINARY)
        image_defects[threshold == 255] = COLOUR_RED
        if self.defect_size(image_defects) > 0:
            coordinates_on, coordinates_off = self.find_coordinates(image_defects, self.contour_color)
            if len(coordinates_on) > 0:
                self.defects_on['Bright Spots'].append(coordinates_on)
            if len(coordinates_off) > 0:
                self.defects_off['Bright Spots'].append(coordinates_off)
        self.stack(self.image_analyzed, image_defects)

    def set_contour_color(self, color):
        self.contour_color = color

    def stack(self, image1, image2):
        mask = cv2.inRange(image2, COLOUR_RED, COLOUR_RED)
        if cv2.countNonZero(mask) > 0:
            image1[np.nonzero(mask)] = COLOUR_RED



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

    def detect_blade_streaks(self):
        """Detects the horizontal lines on the image, doesn't work as well in the darker areas"""
        
        defect = copy.copy(self.image)
        eq = self.clahe(defect)
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
        height = defect.shape[0]
        for x in range(0, len(lines)):
            for x1, y1, x2, y2 in lines[x]:
                # only draw horizontal lines that are not located at top or bottom of image
                if abs(y1 - y2) == 0 and 20 < y1 < height-20:
                    cv2.line(defect, (x1, y1), (x2, y2), COLOUR_RED, 2)
        if self.defect_size(defect) > 0:
            coordinates_on, coordinates_off = self.find_coordinates(defect, self.contour_color)
            if len(coordinates_on) > 0:
                self.defects_on['Blade Streaks'].append(coordinates_on)
            if len(coordinates_off) > 0:
                self.defects_off['Blade Streaks'].append(coordinates_off)
        self.stack(self.image_analyzed, defect)

    # Uses the retval produced by THRESH_OTSU as average intensity
    # and detects any area too bright or too dark compared to their average
    # Use this until detect_dark_spot() is fixed
    def detect_contrast(self):
        defect = copy.copy(self.image)
        h, w = defect.shape[:2]
        retval, dark, light = self.split_otsu()
        dark[:, w-20:] = [0, 0, 0]  # not counting the edge of build platform
        # Bright Spotss of outer ring
        _, outer = cv2.threshold(dark, retval * 1.32, 255, cv2.THRESH_BINARY)
        defect[np.where((outer == COLOUR_WHITE).all(axis=2))] = COLOUR_RED
        # shadows of outer ring
        _, shadow_outer = cv2.threshold(dark, retval * 0.7, 255, cv2.THRESH_BINARY_INV)
        kernel = cv2.getStructuringElement(cv2.MORPH_ERODE, (5, 5))
        cv2.erode(shadow_outer, kernel, dst=shadow_outer, iterations=5)
        cv2.bitwise_or(defect, shadow_outer, dst=shadow_outer)
        _, shadow_outer = cv2.threshold(shadow_outer, retval * 0.5, 255, cv2.THRESH_TOZERO_INV)
        defect[np.where((shadow_outer != COLOUR_BLACK).all(axis=2))] = COLOUR_RED
        defect[np.where((dark == COLOUR_WHITE).all(axis=2))] = COLOUR_RED
        # Bright Spotss of inner circle
        _, center = cv2.threshold(light, retval * 1.7, 255, cv2.THRESH_BINARY)
        defect[np.where((center == COLOUR_WHITE).all(axis=2))] = COLOUR_RED
        # shadows of inner circle
        _, shadow_inner = cv2.threshold(light, retval * 0.95, 255, cv2.THRESH_TOZERO_INV)
        defect[np.where((shadow_inner != COLOUR_BLACK).all(axis=2))] = COLOUR_RED
        if self.defect_size(defect) > 0:
            coordinates_on, coordinates_off = self.find_coordinates(defect, self.contour_color)
            if len(coordinates_on) > 0:
                self.defects_on['Contrast Differences'].append(coordinates_on)
            if len(coordinates_off) > 0:
                self.defects_off['Contrast Differences'].append(coordinates_off)
        self.stack(self.image_analyzed, defect)



    # TODO also picks up dark areas caused by uneven lighting
    def detect_darkspot_test(self):
        defect = copy.copy(self.image)
        eq = self.clahe(defect)
        retval = cv2.threshold(eq, 0, 255, cv2.THRESH_OTSU)[0]
        _, threshold = cv2.threshold(eq, retval*0.25, 255, cv2.THRESH_BINARY_INV)
        defect[threshold == 255] = COLOUR_RED
        self.stack(self.image_analyzed, defect)

    # should work better if able to mask out corners
    def detect_dosing_error(self):
        defect = copy.copy(self.image)
        retval = self.split_otsu()[0]
        width = defect.shape[1]
        _, threshold = cv2.threshold(defect, retval*0.6, 255, cv2.THRESH_BINARY_INV)
        threshold[:, :width/2] = [0, 0, 0]
        defect[np.where((threshold == COLOUR_WHITE).all(axis=2))] = COLOUR_RED
        pass
        self.stack(self.image_analyzed, defect)

    # detects vertical blade chatters
    def detect_blade_chatter(self):
        defect = copy.copy(self.image)
        gray = cv2.cvtColor(defect, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(12, 12))
        eq = clahe.apply(gray)
        templates = []
        for i in range(5):
            temp = cv2.imread('defect%s.png' % str(i+1), cv2.IMREAD_GRAYSCALE)
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
                    cv2.rectangle(defect, (pt[0], pt[1]), (pt[0] + w, pt[1] + h), (0, 0, 255), thickness=3)
                    prev = pt
        if self.defect_size(defect) > 0:
            coordinates_on, coordinates_off = self.find_coordinates(defect, self.contour_color)
            if len(coordinates_on) > 0:
                self.defects_on['Blade Chatter'].append(coordinates_on)
            if len(coordinates_off) > 0:
                self.defects_off['Blade Chatter'].append(coordinates_off)
        self.stack(self.image_analyzed, defect)

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

    def find_coordinates(self, defect, color):
        # creates a mask containing only the layer contours
        mask = cv2.inRange(self.image_overlay, color, color)
        # getting the part of defect image that overlaps with the layout
        roi = cv2.bitwise_and(defect, defect, mask=mask)
        # find all pixels that are red
        on_contour = cv2.inRange(roi, COLOUR_RED, COLOUR_RED)
        coordinates_on = self.detect_blob(on_contour)
        mask_inv = cv2.bitwise_not(mask)
        roi_inv = cv2.bitwise_and(defect, defect, mask=mask_inv)
        off_contour = cv2.inRange(roi_inv, COLOUR_RED, COLOUR_RED)
        coordinates_off = self.detect_blob(off_contour)
        return coordinates_on, coordinates_off

    def detect_blob(self, threshold_image):
        contours = cv2.findContours(threshold_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
        points = []
        for contour in contours:
            if cv2.contourArea(contour) > 50:
                (x, y) = cv2.minEnclosingCircle(contour)[0]
                center = (int(x), int(y))
                points.append(center)
        points.sort()
        return points

    @staticmethod
    def defect_size(image):
        return cv2.countNonZero(cv2.inRange(image, np.array([0, 0, 200]), np.array([100, 100, 255])))

    def split_colour(self, image, colour):
        """Returns two images, one of just the received colour and one of the background without the colour"""

        mask = cv2.inRange(image, colour, colour)
        foreground = cv2.bitwise_and(image, image, mask=mask)
        background = cv2.bitwise_and(image, image, mask=cv2.bitwise_not(mask))
        return foreground, background 
