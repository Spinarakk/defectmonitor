import os
import re

from collections import OrderedDict

from PyQt4.QtCore import QThread, SIGNAL

class SliceConverter(QThread):
    """
    Module to convert any slice files from the weird format they're in into ASCII characters
    Output can then be used to draw contours
    Currently only converts .cls files
    Future implementation will look to either shifting or adding .cli slice conversion
    """

    def __init__(self, slice_raw_folder, slice_parsed_folder):

        # Defines the class as a thread
        QThread.__init__(self)

        # Sets up lists to store the raw and parsed data
        #self.slice_file = slice_file
        self.slice_raw_folder = slice_raw_folder
        self.slice_parsed_folder = slice_parsed_folder
        self.slice_raw_list = os.listdir(self.slice_raw_folder)
        self.slice_parsed_list = os.listdir(self.slice_parsed_folder)

        # Create a dictionary to store the list of slice files (found in the slice raw folder) to be converted
        self.slice_file_dictionary = dict()

    def run(self):
        self.emit(SIGNAL("update_progress(QString)"), '0')
        self._parse_slice(self.slice_raw_list, self.slice_parsed_list)
        self.emit(SIGNAL("update_progress(QString)"), '100')

    def _parse_slice(self, input_list, output_list):
        for idx, item in enumerate(input_list):
            self.emit(SIGNAL("update_status(QString)"), 'Processing slice files...')
            self.slice_file_dictionary[item] = {'Format': item[-3:]}

            # Checks if a parsed slice is already available in the output directory, if not, parse the slice file
            if not item[:-3] + 'txt' in output_list:
                if self.slice_file_dictionary[item]['Format'] == 'cls':

                    with open(self.input_folder + r'\%s' % item, 'rb') as input:
                        bin_slice = input.read()

                    bin_split = re.split('(NEW_LAYER)|(SUPPORT)*(NEW_BORDER)|(NEW_QUADRANT)'
                                         '|(INC_OFFSETS)|(NEW_ISLAND)|(NEW_SKIN)|(NEW_CORE)', bin_slice)
                    bin_split = filter(None, bin_split)
                    bin_split = bin_split[1:]

                    # Initialise dictionaries
                    presort = OrderedDict()
                    output = OrderedDict()

                    out = []

                    # Initialise boolean toggles
                    layer_switch = False
                    support_switch = False
                    border_switch = False
                    offset_switch = False
                    quadrant_switch = False
                    island_switch = False
                    skin_switch = False
                    core_switch = False

                    # Initialise counters
                    island_count = 0
                    layer_count = 0
                    border_count = 0

                    # Main parsing of cls to human-readable format
                    for idx, s in enumerate(bin_split):

                        # Progress bar percentage calculation
                        progress_percentage = int(float(idx) / float(len(bin_split)) * 100.0)
                        if idx == len(bin_split):
                            progress_percentage = 100
                        self.emit(SIGNAL("update_progress(QString)"), str(progress_percentage))

                        e = []
                        if layer_switch:
                            for c in s:
                                e.append(bin(ord(c))[2:].zfill(8))
                            presort['Layer %s.' % layer_count] = e[:]
                            layer_switch = False
                        if border_switch:
                            for c in s:
                                e.append(bin(ord(c))[2:].zfill(8))
                            if support_switch:
                                support_switch = False
                                presort['Layer %s. Support. Border.' % layer_count] = e[:]
                            else:
                                presort['Layer %s. Border %s.' % (layer_count, border_count)] = e[:]
                            border_switch = False
                        if offset_switch:
                            ## UNCOMMENT IF THIS IS NEEDED, otherwise it skips storing the data
                            ## but either way, leave in these if statements

                            # for c in s:
                            #     e.append(bin(ord(c))[2:].zfill(8))
                            # presort['Layer %s, Offsets' % layer_count] = e[:]
                            offset_switch = False
                        if core_switch:
                            # for c in s:
                            #     e.append(bin(ord(c))[2:].zfill(8))
                            # presort['Layer %s, Core' % layer_count] = e[:]
                            core_switch = False
                        if island_switch:
                            # for c in s:
                            #     e.append(bin(ord(c))[2:].zfill(8))
                            # presort['Layer %s, Island %s' % (layer_count, island_count)] = e[:]
                            island_switch = False
                        if quadrant_switch:
                            # for c in s:
                            #     e.append(bin(ord(c))[2:].zfill(8))
                            # presort['Layer %s, Quadrant' % layer_count] = e[:]
                            quadrant_switch = False
                        if skin_switch:
                            # for c in s:
                            #     e.append(bin(ord(c))[2:].zfill(8))
                            skin_switch = False
                        if 'NEW_LAYER' in s:
                            layer_switch = True
                            layer_count += 1
                            island_count = 0
                            border_count = 0
                            presort['Layer %s.' % layer_count] = []
                        if 'INC_OFFSETS' in s:
                            offset_switch = True
                        if 'NEW_QUADRANT' in s:
                            quadrant_switch = True
                        if 'NEW_SKIN' in s:
                            skin_switch = True
                        if 'NEW_ISLAND' in s:
                            island_switch = True
                            island_count += 1
                        if 'NEW_CORE' in s:
                            core_switch = True
                        if 'SUPPORT' in s:
                            support_switch = True
                        if 'NEW_BORDER' in s:
                            border_switch = True
                            if support_switch:
                                pass
                            else:
                                border_count += 1
                                presort['Layer %s. Border %s.' % (layer_count, border_count)] = []

                    for element in presort:
                        if 'Border 1.' in element:
                            testval = int(''.join(presort[element][0:4][::-1]), 2)
                            string = presort[element]
                            test = ['[%s]' % testval]
                            try:
                                num_pt = int(''.join(string[5:9][::-1]), 2)
                                np_idx = 9
                                while np_idx < len(string):
                                    endx = np_idx + num_pt * 8
                                    test.append('<%s>' % num_pt)
                                    while np_idx < endx:
                                        nextpt = ''.join(string[np_idx:np_idx + 4][::-1])
                                        test.append(str(int(nextpt, 2) if (int(nextpt, 2) <= 2147483647)
                                                        else (int(nextpt, 2) - 4294967295)))  # Convert uint to int
                                        np_idx += 4
                                    np_idx += 1
                                    try:
                                        num_pt = int(''.join(string[np_idx:np_idx + 4][::-1]), 2)
                                    except ValueError:
                                        break
                                    np_idx += 4
                                out = test[::-1]
                            except ValueError:
                                pass
                        else:
                            string = iter(presort[element][::-1])
                            out1 = iter([c + next(string, '') for c in string])
                            out = [((int(c + next(out1, ''), 2)) - 4294967295 if int(c[0]) == 1
                                    else (int(c + next(out1, ''), 2))) for c in out1]

                        output[element] = out[::-1]

                    output_write = open(self.slice_parsed_folder + r'\\' + item[:-3] + 'txt', 'w+')
                    for element in output:
                        if 'Border 1.' in element or 'Border' not in element:
                            output_write.write(element)
                            output_write.write(':')
                            output_list = output[element]
                            output_list = ','.join(map(str, output_list))
                            output_write.write(output_list)
                            output_write.write('\n')

                    output_write.close()
                    self.slice_file_dictionary[item]['Parsed'] = output

            else:
                parsed_file = open(self.slice_parsed_folder + r'\\' + item[:-3] + 'txt', 'r')
                parsed_dict = dict()
                for line in parsed_file:
                    raw_dat = re.split(':|,', line.strip())
                    parsed_dict[raw_dat[0]] = raw_dat[1:]
                self.slice_file_dictionary[item]['Parsed'] = parsed_dict

            slice_number = 1

            while True:
                try:
                    self._deconstruct_cls(item, slice_number)
                    slice_number += 1

                except KeyError:
                    self.slice_file_dictionary[item]['Max.Layer'] = slice_number - 1
                    break
        return

    def _deconstruct_cls(self, item, slice_number):
        self.slice_file_dictionary[item][slice_number] = {
            'Contours': self.slice_file_dictionary[item]['Parsed']['Layer %s. Border 1.' % slice_number], 'Polyline-Indices': []}
        poly_no = int(re.sub('\[+(\d+)\]+', r'\1', self.slice_file_dictionary[item][slice_number]['Contours'][0]))
        poly_idx = OrderedDict()
        i_end = None
        for poly_gon in xrange(poly_no):
            if poly_gon == 0:
                i_length = 2 * int(re.sub('<+(\d+)>+', r'\1', self.slice_file_dictionary[item][slice_number]['Contours'][1]))
                i_start = 2
                i_end = i_start + i_length
            else:
                i_start = i_end + 1
                i_length = 2 * int(re.sub('<+(\d+)>+', r'\1', self.slice_file_dictionary[item][slice_number]['Contours'][i_end]))
                i_end = i_start + i_length
            poly_idx[poly_gon] = (i_start, i_length, i_end)
        self.slice_file_dictionary[item][slice_number]['Polyline-Indices'] = poly_idx
        return

    def _parser(self):
        self.slice_file_dictionary[self.slice_file] = {'Format': self.slice_file[-3:]}

        with open(self.slice_file, 'rb') as slice_file:
            self.bin_slice = slice_file.read()

        self.bin_split = re.split('(NEW_LAYER)|(SUPPORT)*(NEW_BORDER)|(NEW_QUADRANT)'
                             '|(INC_OFFSETS)|(NEW_ISLAND)|(NEW_SKIN)|(NEW_CORE)', self.bin_slice)
        self.bin_split = filter(None, self.bin_split)
        self.bin_split = self.bin_split[1:]

        self.pre_sorting = OrderedDict()
        self.slice_output = OrderedDict()

        out = []

        # Initialize boolean toggles
        self.layer_flag = False
        self.support_flag = False
        self.border_flag = False
        self.offset_flag = False
        self.quadrant_flag = False
        self.island_flag = False
        self.skin_flag = False
        self.core_flag = False

        # Initialize counters
        self.island_count = 0
        self.layer_count = 0
        self.border_count = 0

        # Parsing of the slice file to human-readable format
        pass

