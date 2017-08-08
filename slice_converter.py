# Import external libraries
import os
import re
import math
import gc
import json
import cv2
import numpy as np
from collections import OrderedDict
from PyQt4.QtCore import QThread, SIGNAL

class SliceConverter(QThread):
    """Module used to convert any slice files from .cls or .cli format into ASCII format
    Output can then be used to draw contours using OpenCV
    Currently only supports converting .cls files
    Future implementation will look to either shifting or adding .cli slice conversion

    Currently takes in a .cls or .cli file and parses it, saving it as a .txt file after conversion
    """

    def __init__(self, file_name, polygons_flag, contours_flag):

        # Defines the class as a thread
        QThread.__init__(self)

        # Load configuration settings from config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Save respective values to be used to draw contours and polygons
        # Get the resolution of the cropped images using the crop boundaries
        self.image_resolution = ((self.config['CropBoundary'][1] - self.config['CropBoundary'][0]),
                                 (self.config['CropBoundary'][3] - self.config['CropBoundary'][2]))
        self.platform_dimensions = self.config['PlatformDimensions']
        self.boundary_offset = self.config['BoundaryOffset']
        self.scale_factor = 192.0 / 36.0

        # Store the received arguments as local instance variables
        self.file_name = str(file_name)
        self.file_name_processed = str(file_name)
        self.polygons_flag = polygons_flag
        self.contours_flag = contours_flag

        self.slice_parsed = dict()
        self.part_contours = dict()

    def run(self):

        # Check if the sent file name is in .cls or .cli format
        if '.cls' in self.file_name:
            # Look for an already converted contours file
            if os.path.isfile(self.file_name.replace('.cls', '_cls_contours.txt')):
                self.emit(SIGNAL("update_status(QString)"), 'CLS contours file found. Loading from disk...')
                self.load_contours(self.file_name.replace('.cls', '_cls_contours.txt'))
            else:
                self.parse_cls(self.file_name)

            slice_number = 1

            while True:
                try:
                    self.deconstruct_cls(slice_number)
                    slice_number += 1
                except KeyError:
                    self.slice_parsed['Max Layer'] = slice_number - 1
                    break

            self.emit(SIGNAL("update_progress(QString)"), '100')

            for index in xrange(slice_number - 2):
                self.emit(SIGNAL("update_status(QString)"), 'Parsing layer %s...' % index)
                self.converttocontours(index + 1)
                self.draw_contours2(index + 1)

        elif '.cli' in self.file_name:
            if os.path.isfile(self.file_name.replace('.cli', '_cli_contours.txt')):
                self.emit(SIGNAL("update_status(QString)"), 'CLI contours file found. Loading from disk...')
                self.load_contours(self.file_name.replace('.cli', '_cli_contours.txt'))
            else:
                data_cli = self.read_cli(self.file_name)
                data_cli = self.convert2contours(data_cli)
                self.save_contours(self.file_name.replace('.cli', '_cli_contours.txt'), data_cli)
                self.emit(SIGNAL("update_status(QString)"), 'CLS file converted.')
                if self.contours_flag:
                    self.draw_contours(data_cli)
        else:
            self.emit(SIGNAL("update_status(QString)"), 'Slice file not found.')

    def parse_cls(self, file_name):
        """Parses and converts the .cls file into ASCII"""

        #self.slice_parsed[self.slice_file] = {'Format': self.slice_file[-3:]}

        #Open the slice file and read it as binary
        with open(file_name, 'rb') as slice_file:
            slice_unicode = slice_file.read()

        # slice_unicode = []

        self.emit(SIGNAL("update_status(QString)"), 'STEP 1')

        # # Open the slice file and read it as binary
        # with open(cls_file, 'rb') as slice_file:
        #     for line in slice_file.read():
        #         if 'NEW_LAYER' in line:
        #             slice_unicode.append(line)

        # a = array.array('h')
        # a.fromfile(open(cls_file, 'rb'), os.path.getsize(cls_file)/a.itemsize)

        # Splits the string slice_unicode by the occurrences of the aforelisted patterns into a list
        # Parentheses around each word means to also return that word in the resulting list
        slice_unicode_split = re.split('(NEW_LAYER)|(SUPPORT)*(NEW_BORDER)|(NEW_QUADRANT)'
                             '|(INC_OFFSETS)|(NEW_ISLAND)|(NEW_SKIN)|(NEW_CORE)', slice_unicode)

        self.emit(SIGNAL("update_status(QString)"), 'STEP 2')

        # Remove any parts of the list that return a NoneType
        slice_unicode_split = filter(None, slice_unicode_split)

        self.emit(SIGNAL("update_status(QString)"), 'STEP 3')

        # Remove the first line of the list
        slice_unicode_split = slice_unicode_split[1:]

        self.emit(SIGNAL("update_status(QString)"), 'STEP 4')

        # Create dictionary subclasses that remember the order entries were added
        slice_binary = OrderedDict()
        slice_output = OrderedDict()

        out = []

        # Initialize boolean toggles
        layer_flag = False
        support_flag = False
        border_flag = False
        offset_flag = False
        quadrant_flag = False
        island_flag = False
        skin_flag = False
        core_flag = False

        # Initialize counters
        island_count = 0
        layer_count = 0
        border_count = 0

        # Parsing of the slice file to human-readable format
        for index, string in enumerate(slice_unicode_split):
            # Initialize a temporary list to use
            temporary_list = []

            self.emit(SIGNAL("update_status(QString)"), 'STEP %s' % index)

            # If NEW_LAYER string encountered
            if layer_flag:
                for element in string:
                    # Append adds the argument to the end of the list
                    # Bin converts an integer number to a binary string
                    # Ord returns an integer representing the unicode code point of the character
                    # [2:] removes the 0b that appears at the start of each converted character
                    # zfill(8) adds up to 8 zeros to the left of the string
                    temporary_list.append(bin(ord(element))[2:].zfill(8))

                # Makes a copy of the list and saves it in slice_binary at Layer X
                slice_binary['Layer %s' % str(layer_count).zfill(2)] = temporary_list[:]
                layer_flag = False

            # If NEW_BORDER string encountered
            if border_flag:
                for element in string:
                    temporary_list.append(bin(ord(element))[2:].zfill(8))

                if support_flag:
                    slice_binary['Layer %s Support Border' % str(layer_count).zfill(2)] = temporary_list[:]
                    support_flag = False
                else:
                    slice_binary['Layer %s Border %s' % (str(layer_count).zfill(2), str(border_count).zfill(2))] \
                        = temporary_list[:]

                border_flag = False

            # The following flags currently don't do anything as these features are unnecessary to draw contours
            # Only Layer and Border required it seems
            if offset_flag:
                offset_flag = False
            if quadrant_flag:
                quadrant_flag = False
            if island_flag:
                island_flag = False
            if skin_flag:
                skin_flag = False
            if core_flag:
                core_flag = False

            # If the current string has the following strings in it, flips the flag to parse the next string
            if 'NEW_LAYER' in string:
                layer_flag = True
                layer_count += 1
                island_count = 0
                border_count = 0
            if 'SUPPORT' in string:
                support_flag = True
            if 'NEW_BORDER' in string:
                border_flag = True
                if support_flag:
                    pass
                else:
                    border_count += 1

            # The following flags currently don't do anything as these features are unnecessary to draw contours
            if 'INC_OFFSETS' in string:
                offset_flag = True
            if 'NEW_QUADRANT' in string:
                quadrant_flag = True
            if 'NEW_ISLAND' in string:
                island_flag = True
                island_count += 1
            if 'NEW_SKIN' in string:
                skin_flag = True
            if 'NEW_CORE' in string:
                core_flag = True

        self.emit(SIGNAL("update_status(QString)"), 'STEP BINARY')

        for element in slice_binary:
            # Uses the first border to calculate the number of vectors and the
            if 'Border 01' in element:
                # Joins together the elements with the spacer represented by '',
                # [0:4] Returns the first four elements of the list
                # [::-1] appears to reverse the list
                # Converts the integer from the given base (2) into base 10
                vector_length = int(''.join(slice_binary[element][0:4][::-1]), 2)
                string = slice_binary[element]
                output_string = ['[%s]' % vector_length]
                try:
                    vector_amount = int(''.join(string[5:9][::-1]), 2)
                    index = 9
                    while index < len(string):
                        endx = index + vector_amount * 8
                        output_string.append('<%s>' % vector_amount)
                        while index < endx:
                            next_point = ''.join(string[index:index + 4][::-1])
                            output_string.append(str(int(next_point, 2) if (int(next_point, 2) <= 2147483647)
                                            else (int(next_point, 2) - 4294967295)))
                            index += 4
                        index += 1
                        try:
                            vector_amount = int(''.join(string[index:index + 4][::-1]), 2)
                        except ValueError:
                            break

                        index += 4
                    output_string = output_string[::-1]
                except ValueError:
                    pass

            else:
                string = iter(slice_binary[element][::-1])
                output = iter([c + next(string, '') for c in string])
                output_string = [((int(c + next(output, ''), 2)) - 4294967295 if int(c[0]) == 1
                        else (int(c + next(output, ''), 2))) for c in output]

            slice_output[element] = output_string[::-1]
            self.slice_parsed['Parsed'] = slice_output

        self.emit(SIGNAL("update_status(QString)"), 'STEP SAVING')
        # Save the converted slice file as a text document
        with open(self.file_name_processed, 'w+') as slice_file:
            for element in slice_output:
                if 'Border 01' in element or 'Border' not in element:
                    slice_file.write(element)
                    slice_file.write(':')
                    slice_file_map = slice_output[element]
                    slice_file_map = ','.join(map(str, slice_file_map))
                    slice_file.write(slice_file_map)
                    slice_file.write('\n')

        self.emit(SIGNAL("update_status(QString)"), 'STEP FINISHED')

    def deconstruct_cls(self, slice_number):

        self.slice_parsed[slice_number] = {'Contours': self.slice_parsed['Parsed']['Layer %s Border 01' %
                                            str(slice_number).zfill(2)], 'Polyline-Indices': []}
        polygon_number = int(re.sub('\[+(\d+)\]+', r'\1', self.slice_parsed[slice_number]['Contours'][0]))
        polygon_index = OrderedDict()
        contour_end = None
        for polygon in xrange(polygon_number):
            # First iteration
            if polygon == 0:
                contour_start = 2
                contour_length = 2 * int(re.sub('<+(\d+)>+', r'\1', self.slice_parsed[slice_number]['Contours'][1]))
                contour_end = contour_start + contour_length
            # Subsequent iterations
            else:
                contour_start = contour_end + 1
                contour_length = 2 * int(re.sub('<+(\d+)>+', r'\1', self.slice_parsed[slice_number]['Contours']
                [contour_end]))
                contour_end = contour_start + contour_length

            polygon_index[polygon] = (contour_start, contour_length, contour_end)

        self.slice_parsed[slice_number]['Polyline-Indices'] = polygon_index
        return

    def read_cli(self, file_name):
        """Reads the .cli file and converts the contents into an organised list
        If the file was encoded in binary, this method also converts the contents into ascii format"""

        # Instantiate an ordered dictionary to store all the data
        # data_cli = OrderedDict()
        # data_cli['Layers'] = 0

        # Set up a few flags, counters and lists
        binary_flag = False
        # layer_no = 0
        # contour_no = 0
        data_ascii = list()
        line_ascii = ''

        # Open the .cli file
        with open(file_name, 'r') as cli_file:
            for line in cli_file:
                # Check if the file is actually encoded in binary, if so, break from this loop
                if 'BINARY' in line.strip():
                    binary_flag = True
                    break
                # Extract pertinent information from the header and store them in the dictionary
                elif 'UNITS' in line.strip():
                    data_ascii.append(float(line[8:-2]))
                elif 'GEOMETRYSTART' in line.strip():
                    break
            for line in cli_file:
                if binary_flag:
                    break
                # Check if the line is empty or not (because of the removal of random newline characters
                if line.rstrip('\r\n/n'):
                    data_ascii.append(line.rstrip('\r\n/n'))

        if binary_flag:
            # The file needs to be read as binary if it was encoded in binary
            with open(file_name, 'rb') as cli_file:
                for line in cli_file:
                    if 'UNITS' in line.strip():
                        data_ascii.append(float(line[8:-2]))
                    elif 'HEADEREND' in line.strip():
                        data_binary = line.replace('$$HEADEREND', '')
                        break
                for line in cli_file:
                    data_binary += line

            for one, two in zip(data_binary[0::2], data_binary[1::2]):
                # Convert the character unicode into an integer, then into a binary number
                # Join the second binary number with the first binary number and convert the 16-bit bin number into int
                decimal = int(bin(ord(two))[2:].zfill(8) + bin(ord(one))[2:].zfill(8), 2)
                # Check for command indexes and replace with appropriate ascii words
                if decimal == 128:
                    data_ascii.append(line_ascii.rstrip(','))
                    line_ascii = '$$LAYER/'
                elif decimal == 129:
                    data_ascii.append(line_ascii.rstrip(','))
                    line_ascii = '$$POLYLINE/'
                else:
                    line_ascii += (str(decimal) + ',')

        return data_ascii

    def convert2contours(self, data_ascii):
        """Converts the data from the slice file into organized scaled contour data"""
        
        data = OrderedDict()
        data['Units'] = data_ascii[0]
        data['Layers'] = 0
        
        layer_no = 0
        contour_no = 0
        
        for line in data_ascii[1::]:
            if 'LAYER' in line:
                # Strip the newline character from the end, and split the string where the slash appears
                line = re.split('(/)', line.rstrip('\n'))
                # Store the number of contours the current layer has
                if layer_no is not 0:
                    data['Layer %s Contour No.' % str(layer_no).zfill(4)] = contour_no
                # Create a key for each layer's height
                layer_no += 1
                data['Layer %s Height' % str(layer_no).zfill(4)] = int(line[2])
                contour_no = 0
            elif 'POLYLINE' in line:
                contour_no += 1
                # Split each number into its own entry in a list and remove all the comma elements
                line = re.split('(,)', line.rstrip('\r\n/n'))
                line = [comma for comma in line if comma != ',']
                # Store the contour coordinates as
                line = [round(float(element) * data['Units'] * self.scale_factor) for element in line[3:]]
                data['Layer %s Contour %s' % (str(layer_no).zfill(4), str(contour_no).zfill(2))] = line

        data['Layers'] = layer_no

        return data

    def draw_contours(self, data):
        for index in xrange(data['Layers']):
            index += 1
            if index == data['Layers']:
                break
            image_contours = np.zeros(self.image_resolution).astype(np.uint8)
            image_contours = cv2.cvtColor(image_contours, cv2.COLOR_GRAY2BGR)

            self.emit(SIGNAL("update_status(QString)"), 'Drawing contour %s.' % str(index).zfill(4))

            for contour_no in xrange(data['Layer %s Contour No.' % str(index).zfill(4)]):
                contours = data['Layer %s Contour %s' % (str(index).zfill(4), str(contour_no + 1).zfill(2))]
                contours = np.array(contours).reshape(1, len(contours) / 2, 2).astype(np.int32)
                cv2.drawContours(image_contours, contours, -1, (128, 128, 0), int(self.scale_factor))
                if self.polygons_flag:
                    image_polygons = np.zeros(self.image_resolution).astype(np.uint8)
                    image_polygons = cv2.cvtColor(image_polygons, cv2.COLOR_GRAY2BGR)
                    image_polygons_next = image_polygons.copy()
                    if contour_no == 0:
                        cv2.fillPoly(image_polygons, contours, (128, 128, 0))
                    else:
                        cv2.fillPoly(image_polygons_next, contours, (128, 128, 0))
                        image_polygons = cv2.bitwise_xor(image_polygons, image_polygons_next)

            image_contours = cv2.flip(image_contours, 0)
            cv2.imwrite('contours/image_contours_%s.png' % str(index).zfill(4), image_contours)

            if self.polygons_flag:
                image_polygons = cv2.flip(image_polygons, 0)
                cv2.imwrite('polygons/image_polygons_%s.png' % str(index).zfill(4), image_polygons)

    def load_contours(self, file_name):
        """Loads the converted slice file instead"""

        slice_dictionary = dict()

        with open(file_name, 'r') as slice_parsed:
            for string in slice_parsed:
                data = re.split(':|,', string.strip())
                slice_dictionary[data[0]] = data[1:]
            self.slice_parsed['Parsed'] = slice_dictionary

    def save_contours(self, file_name, contours):
        with open(file_name, 'w+') as slice_file:
            slice_file.write(json.dumps(contours))

    def converttocontours(self, layer):
        """Convert the vectors from the parsed slice file into contours which can then be drawn"""

        # Initialize some variables
        min_x = None
        min_y = None
        # part_contours = None
        # hierarchy = None

        # Save the contours and polyline-indices of the received layer
        contours = self.slice_parsed[layer]['Contours']
        polyline = self.slice_parsed[layer]['Polyline-Indices']

        # if negative values exist (part is set up in quadrant other than top-right and buildplate centre is (0,0))
        # translate part to positive

        # Finds minimum x and y values over all contours in given part
        for element in xrange(len(polyline)):
            if min_x is None:
                min_x = np.array(contours[polyline[element][0]:polyline[element][2]:2]).astype(np.int32).min()
            else:
                min_x_temp = np.array(contours[polyline[element][0]:polyline[element][2]:2]).astype(np.int32).min()
                if min_x_temp < min_x:
                    min_x = min_x_temp
            if min_y is None:
                min_y = np.array(contours[polyline[element][0] + 1:polyline[element][2]:2]).astype(np.int32).min()
            else:
                min_y_temp = np.array(contours[polyline[element][0] + 1:polyline[element][2]:2]).astype(np.int32).min()
                if min_y_temp < min_y:
                    min_y = min_y_temp

        slice_parsed = self.slice_parsed

        # Image resizing scale factor relating image pixels and part mm
        # Found by dividing the cropped image height by the known platform height
        scale_factor = 2410.0 / 400.0

        # Create a blank image the same size and type as the cropped image
        image_blank = np.zeros(self.image_resolution).astype(np.uint8)
        image_contours = image_blank.copy()

        # For each vector in the set of vectors, find the area enclosed by the resultant contours
        # Find the hierarchy of each contour, subtract area if it is an internal contour (i.e. a hole)
        for element in xrange(len(polyline)):

            # Get contours in scaled coordinates (scale_factor * part mm)
            slice_parsed[layer]['Contours'][polyline[element][0]:polyline[element][2]:2] = [
                np.float32(scale_factor * (int(x) / 10000. + self.platform_dimensions[0] / 2) + self.boundary_offset[0])
                for x in slice_parsed[layer]['Contours'][polyline[element][0]:polyline[element][2]:2]]

            slice_parsed[layer]['Contours'][(polyline[element][0] + 1):polyline[element][2]:2] = [
                np.float32(scale_factor * (-int(y) / 10000. + self.platform_dimensions[1] / 2) + self.boundary_offset[1])
                for y in slice_parsed[layer]['Contours'][polyline[element][0] + 1:polyline[element][2]:2]]

            current_contours = np.array(slice_parsed[layer]['Contours'][polyline[element][0]:polyline[element][2]])\
                .reshape(1, (polyline[element][1]) / 2, 2)

            # Convert the array to int32
            current_contours = current_contours.astype(np.int32)

            # Draw filled polygons on a blank image
            cv2.fillPoly(image_blank, current_contours, (255, 255, 255))

            # If contour overlaps other poly, it is a hole and is subtracted
            image_contours = cv2.bitwise_xor(image_contours, image_blank)
            image_contours = cv2.cvtColor(image_contours, cv2.COLOR_BGR2GRAY)

            # Find and output vectorized contours and their respective hierarchies
            _, part_contours, hierarchy = cv2.findContours(image_contours.copy(), cv2.RETR_CCOMP,
                                                           cv2.CHAIN_APPROX_SIMPLE)

        # Save contours to the dictionary

        self.part_contours[layer] = {'PartTopleft': (min_x, min_y), 'PartData': {'Contours': part_contours, 'Hierarchy': hierarchy}}

    def draw_contours2(self, layer):

        # Draws the contours
        image_overlay = np.zeros(self.image_resolution).astype(np.uint8)
        image_overlay = cv2.cvtColor(image_overlay, cv2.COLOR_BGR2RGB)

        cv2.drawContours(image_overlay, self.part_contours[layer]['PartData']['Contours'],
                         -1, (255, 0, 0), int(math.ceil(2410.0 / 400.0)))
        self.emit(SIGNAL("update_status(QString)"), 'Saving contour %s...' % layer)
        cv2.imwrite('contours/contour_layer_%s.png' % str(layer).zfill(4), image_overlay)