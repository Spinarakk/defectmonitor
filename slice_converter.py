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

    Currently checks if 'sample_converted.txt' exists in the slice folder
    Otherwise it looks for and converts 'sample.cls'
    """

    def __init__(self, cls_file=None, cli_file=None):

        # Defines the class as a thread
        QThread.__init__(self)


        self.cls_file = cls_file
        self.cli_file = cli_file
        # Create a dictionary to store the list of slice files (found in the slice raw folder) to be converted
        self.slice_file_dictionary = dict()

    def run(self):
        self.emit(SIGNAL("update_progress(QString)"), '0')
        #self._parse_slice(self.slice_raw_list, self.slice_parsed_list)
        if bool(self.cls_file) or bool(self.cli_file):
            self.parse_cls(self.cls_file)

        self.emit(SIGNAL("update_progress(QString)"), '100')

    def parse_cls(self, cls_file):
        """Parses and converts the .cls file into ASCII"""

        #self.slice_file_dictionary[self.slice_file] = {'Format': self.slice_file[-3:]}

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
                pre_sorting['Layer %s.' % layer_count] = temporary_list[:]
                layer_flag = False

            # If NEW_BORDER string encountered
            if border_flag:
                for element in string:
                    temporary_list.append(bin(ord(element))[2:].zfill(8))

                if support_flag:
                    pre_sorting['Layer %s. Support. Border.' % layer_count] = temporary_list[:]
                    support_flag = False
                else:
                    pre_sorting['Layer %s. Border %s.' % (layer_count, border_count)] = temporary_list[:]

                border_flag = False

            if offset_flag:
                # Currently doesn't do anything as unneeded to draw contours
                # Only Layer and Border required it seems
                offset_flag = False
            if core_flag:
                core_flag = False
            if island_flag:
                island_flag = False
            if quadrant_flag:
                quadrant_flag = False
            if skin_flag:
                skin_flag = False
            if 'NEW_LAYER' in string:
                layer_flag = True
                layer_count += 1
                island_count = 0
                border_count = 0
                pre_sorting['Layer %s.' % layer_count] = []
            if 'INC_OFFSETS' in string:
                offset_flag = True
            if 'NEW_QUADRANT' in string:
                quadrant_flag = True
            if 'NEW_SKIN' in string:
                skin_flag = True
            if 'NEW_ISLAND' in string:
                island_flag = True
                island_count += 1
            if 'NEW_CORE' in string:
                core_flag = True
            if 'SUPPORT' in string:
                support_flag = True
            if 'NEW_BORDER' in string:
                border_flag = True
                if support_flag:
                    pass
                else:
                    border_count += 1
                    pre_sorting['Layer %s. Border %s.' % (layer_count, border_count)] = []

        for element in pre_sorting:
            if 'Border 1.' in element:
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

        with open('slice/sample_processed.txt', 'w+') as output_write:
            for element in slice_output:
                if 'Border 1.' in element or 'Border' not in element:
                    output_write.write(element)
                    output_write.write(':')
                    output_list = slice_output[element]
                    output_list = ','.join(map(str, output_list))
                    output_write.write(output_list)
                    output_write.write('\n')
