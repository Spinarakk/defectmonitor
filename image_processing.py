# Import external libraries
import os
import cv2
import numpy as np
import json

# Some global colours are defined here (represented as BGR)
COLOUR_RED = (0, 0, 255)
COLOUR_BLUE = (255, 0, 0)
COLOUR_GREEN = (0, 255, 0)
COLOUR_YELLOW = (0, 255, 255)
COLOUR_PINK = (203, 192, 255)
COLOUR_BLACK = (0, 0, 0)
COLOUR_WHITE = (255, 255, 255)


class ImageFix:
    """Module containing methods used to transform or modify any images using a variety of OpenCV functions"""

    def fix_image(self, image_name, parameters):
        """Fixes the received image for distortion, perspective and crops it to the correct size, and saves it"""

        # Load the image into memory
        image = cv2.imread(image_name)

        # Apply the following fixes
        image = self.distortion_fix(image, parameters['CameraMatrix'], parameters['DistortionCoefficients'])
        image = self.perspective_fix(image, parameters['HomographyMatrix'], parameters['HomographyResolution'])
        image = self.crop(image, parameters['CropOffset'], parameters['ImageResolution'])

        # Save the image using a modified image name
        cv2.imwrite(image_name.replace('R_', 'F_').replace('raw', 'fixed'), image)

    def convert_image(self, image_name, parameters, checkboxes, status, progress, naming_error):
        """Applies the distortion, perspective, crop and CLAHE processes to the received image
        Also subsequently saves each image after every process if the corresponding checkbox is checked"""

        # Load the image into memory
        image = cv2.imread(image_name)

        # Grab the folder names and the image name which will be used to construct the new modified names
        folder_name = os.path.dirname(image_name)
        image_name = os.path.basename(os.path.splitext(image_name)[0])

        # If the Alternate Naming Scheme for Crop Images checkbox is checked
        # Detect the phase and layer number from the image name itself and use those to save to the fixed folder instead
        if checkboxes[0]:
            # Phase check
            if 'coatR_' in image_name:
                phase = 'coat'
            elif 'scanR_' in image_name:
                phase = 'scan'
            elif 'snapshotR_' in image_name:
                phase = 'snapshot'
            else:
                # If the phase can't be determined due to incorrect naming, don't use alternate naming scheme
                checkboxes[0] = False
                naming_error.emit()

            # Layer check
            try:
                int(image_name[-4:])
            except ValueError:
                # If the layer number can't be determined due to incorrect naming, don't use alternate naming scheme
                checkboxes[0] = False
                naming_error.emit()

        # Apply the image processing techniques in order, subsequently saving the image and incrementing progress
        # Images are only saved if the corresponding checkbox is checked
        progress.emit(0)
        status.emit('Undistorting image...')
        image = self.distortion_fix(image, parameters['CameraMatrix'], parameters['DistortionCoefficients'])

        if checkboxes[3]:
            if checkboxes[1]:
                cv2.imwrite('%s/undistort/%s_D.png' % (folder_name, image_name), image)
            else:
                cv2.imwrite('%s/%s_D.png' % (folder_name, image_name), image)

        progress.emit(25)
        status.emit('Fixing perspective warp...')
        image = self.perspective_fix(image, parameters['HomographyMatrix'], parameters['HomographyResolution'])

        if checkboxes[4]:
            if checkboxes[1]:
                cv2.imwrite('%s/perspective/%s_DP.png' % (folder_name, image_name), image)
            else:
                cv2.imwrite('%s/%s_DP.png' % (folder_name, image_name), image)

        progress.emit(50)
        status.emit('Cropping image to size...')
        image = self.crop(image, parameters['CropOffset'], parameters['ImageResolution'])

        if checkboxes[5]:
            if checkboxes[0]:
                cv2.imwrite('%s/fixed/%s/%s.png' % (folder_name, phase, image_name.replace('R_', 'F_')), image)
            elif checkboxes[1]:
                cv2.imwrite('%s/crop/%s_DPC.png' % (folder_name, image_name), image)
            else:
                cv2.imwrite('%s/%s_DPC.png' % (folder_name, image_name), image)

        progress.emit(75)
        status.emit('Applying CLAHE equalization...')
        image = self.clahe(image)

        if checkboxes[6]:
            if checkboxes[1]:
                cv2.imwrite('%s/equalization/%s_DPCE.png' % (folder_name, image_name), image)
            else:
                cv2.imwrite('%s/%s_DPCE.png' % (folder_name, image_name), image)

        progress.emit(100)
        status.emit('Image conversion successful.')

    @staticmethod
    def distortion_fix(image, cmatrix, distco):
        """Fixes the barrel/pincushion distortion commonly found in pinhole cameras"""
        return cv2.undistort(image, np.array(cmatrix), np.array(distco))

    @staticmethod
    def perspective_fix(image, hmatrix, hres):
        """Fixes the perspective warp due to the off-centre position of the camera"""
        return cv2.warpPerspective(image, np.array(hmatrix), tuple(hres))

    @staticmethod
    def crop(image, offset, resolution):
        """Crops the image to a more desirable region of interest"""
        return image[offset[0]:offset[0] + resolution[0], offset[1]:offset[1] + resolution[1]]

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


class DefectProcessor:
    """Module used to process the corrected images using OpenCV functions to detect a variety of different defects
    Defects to be analyzed are outlined in the README.txt file and are named arbitrarily (not industry standards)
    """

    def run_processor(self, image_name, layer, phase, folder, part_colours, roi, status, progress):
        """Initial run method that decides whether to run the coat or scan collection of detection processes"""

        progress.emit(0)

        # Discern the previous layer number and convert them to strings
        layer_p = str(layer - 1).zfill(4)
        layer = str(layer).zfill(4)

        # Load or create the images to be analyzed into memory
        image = cv2.imread(image_name)                                          # Original image to be analyzed
        image_b = np.zeros(image.shape, np.uint8)                               # Blank black image to draw defects on
        image_c = cv2.imread('%s/contours/contours_%s.png' % (folder, layer))   # Corresponding part contours image
        image_p = cv2.imread(image_name.replace(layer, layer_p))                # Previous layer image

        # If the contours image exists, add the part names to a newly created defect dictionary to store defect results
        if type(image_c) is np.ndarray:
            self.defects = dict.fromkeys(part_colours.keys(), dict())
        else:
            # Otherwise create the master defect dictionary
            self.defects = dict()

        # Create the 'combined' dictionary key
        self.defects['combined'] = dict()

        # Open all the reports and save their dictionaries to the master defect dictionary
        # These dictionaries will be overwritten with new data should the program process the same layer and part
        for part_name in self.defects.keys():
            with open('%s/reports/%s_report.json' % (folder, part_name)) as report:
                self.defects[part_name] = json.load(report)

            # The dictionary needs to be built up if it doesn't already exist
            if layer not in self.defects[part_name]:
                self.defects[part_name][layer] = dict()

            if phase not in self.defects[part_name][layer]:
                self.defects[part_name][layer][phase] = dict()

        # (Coat + Scan) Blade streak defects will be drawn in red
        status.emit('Detecting blade streaks...')
        image_d = self.detect_blade_streak(image, image_b.copy())
        self.report_defects(image_d, image_c, layer, phase, folder, part_colours, roi, COLOUR_RED, 'BS')
        progress.emit(20 + 5 * int('scan' in phase))

        # (Coat + Scan) Blade chatter defects will be drawn in blue
        status.emit('Detecting blade chatter...')
        image_d = self.detect_blade_chatter(image, image_b.copy())
        self.report_defects(image_d, image_c, layer, phase, folder, part_colours, roi, COLOUR_BLUE, 'BC')
        progress.emit(40 + 10 * int('scan' in phase))

        if 'coat' in phase:
            # (Coat only) Shiny patch defects will be drawn in green
            status.emit('Detecting shiny patches...')
            image_d = self.detect_shiny_patch(image, image_b.copy())
            self.report_defects(image_d, image_c, layer, phase, folder, part_colours, roi, COLOUR_GREEN, 'SP')
            progress.emit(60)

            # (Coat only) Contrast outlier defects will be drawn in yellow
            status.emit('Detecting contrast outliers...')
            image_d = self.detect_contrast_outlier(image, image_b.copy())
            self.report_defects(image_d, image_c, layer, phase, folder, part_colours, roi, COLOUR_YELLOW, 'CO')
            progress.emit(80)

        elif 'scan' in phase:
            # (Scan only) Scan pattern will be drawn in pink
            status.emit('Detecting scan pattern...')
            image_d = self.detect_scan_pattern(image, image_b.copy())
            image_d = self.report_defects(image_d, image_c, layer, phase, folder, part_colours, roi, COLOUR_PINK, 'OC')
            progress.emit(75)

            if type(image_c) is np.ndarray:
                if roi[0]:
                    image_c = self.defect_roi(image_c, roi)
                self.defects['combined'][layer][phase]['OC'] = self.compare_overlay(image_d, image_c)

        # Histogram comparison with the previous layer if the previous layer's image exists
        if type(image_p) is np.ndarray:
            status.emit('Comparing against previous layer...')
            # Crop down both the current image and previous image to remove non-ROI parts if needed
            if roi[0]:
                image = self.defect_roi(image, roi)
                image_p = self.defect_roi(image_p, roi)

            # Save the result directly to the combined report
            self.defects['combined'][layer][phase]['HC'] = self.compare_histogram(image, image_p)

        # Save all the reports to their respective json files
        for part_name, data in self.defects.items():
            with open('%s/reports/%s_report.json' % (folder, part_name), 'w+') as report:
                json.dump(data, report, sort_keys=True)

        progress.emit(100)

    def report_defects(self, image_d, image_c, layer, phase, folder, part_colours, roi, defect_colour, defect_type):
        """Report the size and coordinates of any defects that overlay any of the part contours and the background"""

        # Crop down the defect image to remove non-ROI parts if needed
        if roi[0]:
            image_d = self.defect_roi(image_d, roi)

        # Create a defect type dictionary to convert from shorthand to full name
        types = {'BS': 'streaks', 'BC': 'chatter', 'SP': 'patches', 'CO': 'outliers', 'OC': 'pattern'}

        # Save the defect image to the corresponding folder
        cv2.imwrite('%s/defects/%s/%s/%s%s_%s.png' % (folder, phase, types[defect_type], phase, defect_type, layer),
                    image_d)

        # Return the image back to the caller if the scan pattern image only needs to be cropped and saved
        if 'OC' in defect_type:
            return image_d

        # Only report defects that intersect the part contours if the image exists
        for name, colour in part_colours.items():
            if 'combined' in name or type(image_c) is np.ndarray:
                # Find the total size, coordinates and occurrences of the defect pixels that overlap the part
                if 'combined' in name:
                    result, size_part = self.find_coordinates(image_d, np.zeros(image_d.shape, np.uint8),
                                                              tuple(colour), defect_colour)
                    size_part = image_d.size / 3
                else:
                    result, size_part = self.find_coordinates(image_d, image_c, tuple(colour), defect_colour)

                # Convert the pixel size data into a percentage based on the total number of pixels in the image
                if 'SP' in defect_type or 'CO' in defect_type:
                    result[0] = round(result[0] / size_part * 100, 4)

                # Add these to the defect dictionary for the current part, and the combined dictionary
                self.defects[name][layer][phase][defect_type] = result
            else:
                continue

    @staticmethod
    def detect_blade_streak(image, image_defects):
        """Detects any horizontal lines on the image, doesn't work as well in the darker areas"""

        # Apply CLAHE equalization to the raw image
        image = ImageFix.clahe(image, gray_flag=True)

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

        return image_defects

    @staticmethod
    def detect_blade_chatter(image, image_defects):
        """Detects any vertical lines on the image that are caused as a result of blade chatter
        Done by matching any chatter against a pre-collected set of blade chatter templates"""

        # Apply CLAHE equalization to the raw image
        image = ImageFix.clahe(image, gray_flag=True, cliplimit=3.0, tilegridsize=(12, 12))

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

        return image_defects

    @staticmethod
    def detect_shiny_patch(image, image_defects):
        """Detects any patches in the image that are above a certain contrast threshold, aka are too shiny"""

        # Apply CLAHE equalization to the raw image
        image = ImageFix.clahe(image, gray_flag=True)

        # Otsu's Binarization is used to calculate a threshold value to be used to get a proper threshold image
        retval = cv2.threshold(image, 0, 255, cv2.THRESH_OTSU)[0]
        image_threshold = cv2.threshold(image, retval * 1.85, 255, cv2.THRESH_BINARY)[1]

        # Change the colour of the pixels in the blank image to green if they're above the threshold
        image_defects[image_threshold == 255] = COLOUR_GREEN

        return image_defects

    @staticmethod
    def detect_contrast_outlier(image, image_defects):
        """Detects any areas of the image that are too bright or dark compared to the average contrast
        Use this until detect_dark_spots is fixed and working sufficiently"""

        # Otsu's Binarization is used to calculate a threshold value and image using the raw grayscale image
        retval, image_threshold = cv2.threshold(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), 0, 255, cv2.THRESH_OTSU)

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

        return image_defects

    @staticmethod
    def detect_scan_pattern(image, image_defects):
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

        # Draw the contours on the defect image in pink
        cv2.drawContours(image_defects, contours_list, -1, COLOUR_PINK, thickness=cv2.FILLED)

        return image_defects

    @staticmethod
    def compare_histogram(image_current, image_previous):
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

        # Return the result to be saved to the combined report
        return result

    @staticmethod
    def compare_overlay(image_defects, image_contours):
        """Compares the detected scan pattern against the drawn contours and calculates the difference result"""

        # Convert all the part contour colours to pink so that it can be compared to the detected scan pattern
        mask = cv2.inRange(image_contours, (100, 100, 0), (255, 255, 0))
        image_contours[np.nonzero(mask)] = COLOUR_PINK

        # Use template matching to directly compare the two images and return the result
        result = float(cv2.matchTemplate(image_defects, image_contours, cv2.TM_CCOEFF_NORMED)[0][0])
        return result

    @staticmethod
    def defect_roi(image, roi):
        """Crops the image (specifically the found defects image) to the specified ROI and adds black to the rest"""
        image_roi = np.zeros(image.shape, np.uint8)
        image_roi[roi[2]:roi[4], roi[1]:roi[3]] = image[roi[2]:roi[4], roi[1]:roi[3]]
        return image_roi

    @staticmethod
    def find_coordinates(image_defects, image_overlay, part_colour, defect_colour):
        """Determines the coordinates of any defects (coloured pixels) and whether they overlap with the part contours
        Because reporting the coordinates of every pixel will yield an incredibly long list...
        The centre coordinates of each 'defect blob' is reported instead"""

        # Create a mask of the part in question part using its respective colour
        mask = cv2.inRange(image_overlay, part_colour, part_colour)

        # Because the colour causes some noise in the mask due to gradients, close and remove any white noise
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))

        # Calculate the size of the part contours in the mask
        size_part = cv2.countNonZero(mask)

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

        return [size, occurrences] + coordinates, size_part
