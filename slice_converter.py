# Import external libraries
import os
import re
from collections import OrderedDict
from PyQt4.QtCore import QThread, SIGNAL

class SliceConverter(QThread):
    """Module used to convert any slice files from .cls or .cli format into ASCII format
    Output can then be used to draw contours using OpenCV
    Currently only supports converting .cls files
    Future implementation will look to either shifting or adding .cli slice conversion

    Currently takes in a .cls or .cli file and parses it, saving it as a .txt file after conversion
    """

    def __init__(self, file_name=None):

        # Defines the class as a thread
        QThread.__init__(self)

        # Save the files as local instance variables
        self.slice_file_name = str(file_name)

        self.slice_parsed = dict()

    def run(self):

        self.emit(SIGNAL("update_progress(QString)"), '0')

        # Change the name of the slice file for checking if it already exists
        self.slice_file_name = self.slice_file_name.replace('.cls', '_cls_processed.txt')
        self.slice_file_name = self.slice_file_name.replace('.cli', '_cli_processed.txt')

        # Checks if a converted slice file already exists in the form of XXX_processed.txt in the sent folder
        # If so, load from it instead of converting again
        if os.path.isfile(self.slice_file_name):
            print 'FILE FOUND'
            self.load_slice(self.slice_file_name)
        else:
            # Change the name of the slice file back to the original
            self.slice_file_name.replace('_cls_processed.txt', '.cls')
            self.slice_file_name.replace('_cli_processed.txt', '.cli')

            # Checks if the sent file is of cls or cli format
            if '.cls' in self.slice_file_name:
                self.parse_cls(self.slice_file_name)
            else:
                self.parse_cli(self.slice_file_name)

        self.emit(SIGNAL("update_progress(QString)"), '50')

        slice_number = 1

        while True:
            try:
                self.deconstruct_cls(slice_number)
                slice_number += 1
            except KeyError:
                self.slice_parsed['Max Layer'] = slice_number - 1
                break

        self.emit(SIGNAL("update_progress(QString)"), '100')

    def parse_cls(self, cls_file):
        """Parses and converts the .cls file into ASCII"""

        #self.slice_parsed[self.slice_file] = {'Format': self.slice_file[-3:]}

        # Open the slice file and read it as binary
        with open(cls_file, 'rb') as slice_file:
            bin_slice = slice_file.read()

        # Splits the string bin_slice by the occurrences of the aforelisted patterns into a list
        # Parentheses around each word means to also return that word in the resulting list
        bin_split = re.split('(NEW_LAYER)|(SUPPORT)*(NEW_BORDER)|(NEW_QUADRANT)'
                             '|(INC_OFFSETS)|(NEW_ISLAND)|(NEW_SKIN)|(NEW_CORE)', bin_slice)

        # Remove any parts of the list that return a NoneType
        bin_split = filter(None, bin_split)

        # Remove the first line of the list
        bin_split = bin_split[1:]

        # Create dictionary subclasses that remember the order entries were added
        pre_sorting = OrderedDict()
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
        for index, string in enumerate(bin_split):
            # Initialize a temporary list to use
            temporary_list = []

            # If NEW_LAYER string encountered
            if layer_flag:
                for element in string:
                    # Append adds the argument to the end of the list
                    # Bin converts an integer number to a binary string
                    # Ord returns an integer representing the unicode code point of the character
                    # [2:] removes the 0b that appears at the start of each converted character
                    # zfill(8) adds up to 8 zeros to the left of the string
                    temporary_list.append(bin(ord(element))[2:].zfill(8))

                # Makes a copy of the list and saves it in pre_sorting at Layer X
                pre_sorting['Layer %s' % str(layer_count).zfill(2)] = temporary_list[:]
                layer_flag = False

            # If NEW_BORDER string encountered
            if border_flag:
                for element in string:
                    temporary_list.append(bin(ord(element))[2:].zfill(8))

                if support_flag:
                    pre_sorting['Layer %s Support Border' % str(layer_count).zfill(2)] = temporary_list[:]
                    support_flag = False
                else:
                    pre_sorting['Layer %s Border %s' % (str(layer_count).zfill(2), str(border_count).zfill(2))] \
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

        for element in pre_sorting:
            # Uses the first border to calculate the number of vectors and the
            if 'Border 01' in element:
                # Joins together the elements with the spacer represented by '',
                # [0:4] Returns the first four elements of the list
                # [::-1] appears to reverse the list
                # Converts the integer from the given base (2) into base 10
                test_value = int(''.join(pre_sorting[element][0:4][::-1]), 2)
                string = pre_sorting[element]
                test = ['[%s]' % test_value]
                try:
                    number_points = int(''.join(string[5:9][::-1]), 2)
                    index = 9
                    while index < len(string):
                        endx = index + number_points * 8
                        test.append('<%s>' % number_points)
                        while index < endx:
                            next_point = ''.join(string[index:index + 4][::-1])
                            test.append(str(int(next_point, 2) if (int(next_point, 2) <= 2147483647)
                                            else (int(next_point, 2) - 4294967295)))
                            index += 4
                        index += 1
                        try:
                            number_points = int(''.join(string[index:index + 4][::-1]), 2)
                        except ValueError:
                            break

                        index += 4
                    out = test[::-1]
                except ValueError:
                    pass

            else:
                string = iter(pre_sorting[element][::-1])
                out1 = iter([c + next(string, '') for c in string])
                out = [((int(c + next(out1, ''), 2)) - 4294967295 if int(c[0]) == 1
                        else (int(c + next(out1, ''), 2))) for c in out1]

            slice_output[element] = out[::-1]
            self.slice_parsed['Parsed'] = slice_output

        # Change the name of the slice file for export
        self.slice_file_name.replace('.cls', '_cls_processed.txt')

        # Save the converted slice file as a text document
        with open(self.slice_file_name, 'w+') as output_write:
            for element in slice_output:
                if 'Border 01' in element or 'Border' not in element:
                    output_write.write(element)
                    output_write.write(':')
                    output_list = slice_output[element]
                    output_list = ','.join(map(str, output_list))
                    output_write.write(output_list)
                    output_write.write('\n')

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

    def parse_cli(self):
        """Parses and converts the .cli file into ASCII"""
        pass

    def load_slice(self, file_name):
        """Loads the converted slice file instead"""

        slice_dictionary = dict()

        with open(file_name, 'r') as slice_parsed:
            for string in slice_parsed:
                data = re.split(':|,', string.strip())
                slice_dictionary[data[0]] = data[1:]
            self.slice_parsed['Parsed'] = slice_dictionary
