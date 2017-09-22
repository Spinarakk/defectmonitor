# Import external libraries
import os
import re
import json
import time
import cv2
import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import image_processing


class SliceConverter:
    """Module used to convert any slice files from .cls or .cli format into ASCII format
    Output can then be used to draw contours using OpenCV
    Currently takes in a .cls or .cli file and parses it, saving it as a .txt file after conversion
    """

    def __init__(self):

        # Flags that will be dictated from the config.json file that control whether to run/stop or pause/resume
        self.run_flag = True
        self.pause_flag = False

        # Method that loads the config.json file and checks the run and pause keys
        self.check_flags()

        # Save respective values to be used to draw contours and polygons
        # Get the resolution of the cropped images using the crop boundaries, 3 at the end indicates an RGB image
        crop_boundary = self.config['ImageCorrection']['CropBoundary']
        self.image_resolution = ((crop_boundary[1] - crop_boundary[0]),
                                 (crop_boundary[3] - crop_boundary[2]), 3)
        self.offset = (self.config['ImageCorrection']['Offset'][0], self.config['ImageCorrection']['Offset'][1])
        self.scale_factor = self.config['ImageCorrection']['ScaleFactor']
        self.transform = self.config['ImageCorrection']['TransformParameters']

        # Part names are taken from the config.json file, depending if this method was run from the Slice Converter
        # Or as part of a new build, different files will be read and used

        if self.config['SliceConverter']['Build']:
            self.part_colours = self.config['BuildInfo']['Colours']
            self.part_names = self.config['BuildInfo']['SliceFiles']
            self.draw_flag = self.config['BuildInfo']['Draw']
            self.contours_folder = '%s/contours' % self.config['ImageCapture']['Folder']
        else:
            self.part_colours = self.config['SliceConverter']['Colours']
            self.part_names = self.config['SliceConverter']['Files']
            self.draw_flag = self.config['SliceConverter']['Draw']
            self.contours_folder = self.config['SliceConverter']['Folder']

    def convert(self, status, progress):

        # Assign the status and progress signals as instance variables so other methods can use them
        self.status = status
        self.progress = progress

        for part_name in self.part_names:
            # Executes if the sent file is a .cls file
            if '.cls' in part_name:
                # Look for an already converted contours file, otherwise convert the cls file
                if not os.path.isfile(part_name.replace('.cls', '_contours.txt')):
                    # The conditionals for the run flags are to check if the user has cancelled the operation
                    if self.run_flag:
                        data = self.read_cls(part_name)
                    else:
                        # Break out of the entire for loop, set draw flag to false and finish the entire thread
                        return
                    if self.run_flag:
                        self.format_contours(part_name.replace('.cli', '_contours.txt'), data)
                    else:
                        return
            # Executes if the sent file is a .cli file
            elif '.cli' in part_name:
                # Look for an already converted contours file, otherwise convert the cli file
                if not os.path.isfile(part_name.replace('.cli', '_contours.txt')):
                    if self.run_flag:
                        data = self.read_cli(part_name)
                    else:
                        return
                    if self.run_flag:
                        self.format_contours(part_name.replace('.cli', '_contours.txt'), data)
                    else:
                        return

        if self.draw_flag:
            # Draw and save the contours to an image file
            self.draw_contours(self.part_names, self.part_colours, self.contours_folder)

            if not self.run_flag:
                return

        self.status.emit('Current Part: None | Conversion completed successfully.')

    def read_cls(self, file_name):
        """Reads the .cli file and converts the contents from binary into an organised ASCII list"""

        self.status.emit('Current Part: %s | Reading CLS file...' % os.path.basename(file_name).replace('.cls', ''))

        # Set up a few flags, counters and lists
        layer_flag = False
        border_flag = False
        next_border_flag = False
        index = 2
        vector_no = 0

        # Initialize the converted data list with some important information
        data_ascii = [float(0.001), '']

        # UI Progress and Status Messages
        progress = 10.0
        progress_previous = None

        with open(file_name, 'rb') as cls_file:
            # Split the entire file into a massive list if the following strings are found
            data_binary = re.split('(NEW_LAYER)|(SUPPORT)*(NEW_BORDER)|(NEW_QUADRANT)'
                                   '|(INC_OFFSETS)|(NEW_ISLAND)|(NEW_SKIN)|(NEW_CORE)', cls_file.read())
            self.progress.emit(8)
            # Remove any NoneType data in the list
            data_binary = filter(None, data_binary)
            increment = 90.0 / len(data_binary)
            self.progress.emit(int(round(progress)))

            for line in data_binary:
                if layer_flag or border_flag:
                    data_line = list()
                    data = list()
                    for character in line:
                        data_line.append(bin(ord(character))[2:].zfill(8))
                    data_line = data_line[::-1]
                    for one, two, three, four in zip(data_line[0::4], data_line[1::4], data_line[2::4],
                                                     data_line[3::4]):
                        decimal = int(one + two + three + four, 2)
                        data.append(decimal)
                    if layer_flag:
                        data_ascii[index] += str(data[-1] / 100)
                        layer_flag = False
                    elif border_flag:
                        data = data[::-1]
                        data_ascii[index] += '%s,%s,' % (data[0], data[1])
                        for one, two in zip(data[2::4], data[3::4]):
                            data_ascii[index] += (str(one / 100) + ',' + str(two / 100) + ',')
                            vector_no += 1
                        data_ascii[index] = data_ascii[index].replace('1,%s,%s,' % (data[0], data[1]),
                                                                      '1,%s,%s,' % (data[0], vector_no)).rstrip(',')
                        border_flag = False
                        next_border_flag = False
                    # Reset vector numbers
                    vector_no = 0
                    index += 1
                if 'NEW_LAYER' in line:
                    data_ascii.append('$$LAYER/')
                    layer_flag = True
                    next_border_flag = True
                if 'NEW_BORDER' in line and next_border_flag:
                    data_ascii.append('$$POLYLINE/1,')
                    border_flag = True
                    layer_flag = False
                # Put into a conditional to only trigger if the whole number changes so as to not overload the emit
                if int(round(progress)) is not progress_previous:
                    self.progress(int(round(progress)))
                    progress_previous = int(round(progress))
                progress += increment

        return data_ascii

    def read_cli(self, file_name):
        """Reads the .cli file and converts the contents from binary into an organised ASCII list"""

        # UI Progress and Status Messages
        progress_count = 0.0
        progress_previous = None
        self.status.emit('Current Part: %s | Reading CLI (BINARY) file...' %
                         os.path.basename(file_name).replace('.cli', ''))
        self.progress.emit(0)

        # Set up a few lists, flags, counters
        data_ascii = list()
        line_ascii = str()
        layer_flag = False
        polyline_count = 0
        vector_count = 0
        header_length = 0

        # Grab the file size of the cli file in bytes
        file_size = os.path.getsize(file_name)

        # File needs to be opened and read as binary as it is encoded in binary
        with open(file_name, 'rb') as cli_file:

            # Get pertinent information from the header by reading the lines and storing them in the final data list
            for line in cli_file.readlines():
                if 'UNITS' in str(line):
                    data_ascii.append(float(line[8:-2]))
                elif 'LAYERS' in str(line):
                    data_ascii.append(int(line[9:-1]))
                elif 'HEADEREND' in str(line):
                    # Break out of the header loop and add the $$HEADEREND length
                    header_length += 11
                    break

                # Measure the length of the header (in bytes) to calculate the increment for the rest of the file
                header_length += len(line)

            # Return to the end of the header
            cli_file.seek(header_length)

            # Calculate the increment to use to display progress for the rest of the file data
            increment = 100 / (file_size - header_length)
            progress_count = header_length * increment

            # Read the rest of the data
            data = cli_file.read()

            # Iterate through every character in the file two at a time
            for i, k in zip(data[0::2], data[1::2]):
                decimal = int(bin(k)[2:].zfill(8) + bin(i)[2:].zfill(8), 2)
                if layer_flag:
                    line_ascii += (str(decimal) + ',')
                    layer_flag = False
                elif polyline_count > 0:
                    line_ascii += (str(decimal) + ',')
                    polyline_count -= 1
                    if polyline_count == 0:
                        vector_count = decimal * 2
                elif vector_count > 0:
                    line_ascii += (str(decimal) + ',')
                    vector_count -= 1
                elif decimal == 128:
                    data_ascii.append(line_ascii.rstrip(','))
                    line_ascii = '$$LAYER/'
                    layer_flag = True
                elif decimal == 129:
                    data_ascii.append(line_ascii.rstrip(','))
                    line_ascii = '$$POLYLINE/'
                    polyline_count = 3

                # Put into a conditional to only trigger if the whole number changes so as to not overload the emit
                progress_count += increment * 2
                progress = int(5 * round(progress_count / 5))
                if not progress == progress_previous:
                    self.progress.emit(progress)
                    progress_previous = progress

                    # Check if the user has paused/resumed the conversion
                    # Put in the progress conditional so as to not slow down the conversion process
                    # If paused, sleep here indefinitely while constantly checking if the user has resumed operation
                    self.check_flags()
                    while self.pause_flag:
                        self.status.emit('Current Part: %s | Conversion paused.' %
                                         os.path.basename(file_name).replace('.cli', ''))
                        time.sleep(1)
                        self.check_flags()
                    if not self.run_flag:
                        self.status.emit('Current Part: %s | Conversion stopped.' %
                                         os.path.basename(file_name).replace('.cli', ''))
                        self.draw_flag = False
                        return None

                    self.status.emit('Current Part: %s | Reading CLI (BINARY) file...' %
                                     os.path.basename(file_name).replace('.cli', ''))

        return data_ascii

    def read_cli_ascii(self, file_name):
        # Open the .cli file
        with open(file_name, 'r') as cli_file:
            # print(len(cli_file.read()))
            increment = 0.001
            # increment = 100.0 / sum(1 for _ in cli_file.read())
            # # Go back to the start of the file as getting the length of the file put the seek head to the EOF
            # cli_file.seek(0)
            for line in cli_file.read():
                # Check if the file is actually encoded in binary, if so, break from this loop
                if 'BINARY' in line.strip():
                    binary_flag = True
                    break
                # Extract pertinent information from the header and store them in the dictionary
                elif 'UNITS' in line.strip():
                    data_ascii.append(float(line[8:-2]))
                elif 'GEOMETRYSTART' in line.strip():
                    break
                progress += increment

            for line in cli_file:
                if binary_flag:
                    break
                # Check if the line is empty or not (because of the removal of random newline characters)
                if line.rstrip('\r\n/n'):
                    data_ascii.append(line.rstrip('\r\n/n'))

                if int(round(progress)) is not progress_previous:
                    self.progress.emit(int(round(progress)))
                    progress_previous = int(round(progress))
                progress += increment

    def format_contours(self, file_name, data_ascii):
        """Formats the data from the slice file into an organized scaled list of contours
        First element is the number of layers
        Every layer starts with a STARTLAYERXX, YY list, followed by the list of contours, followed by a ENDLAYER
        XX is the layer number, YY is the scaled layer height
        Method also saves the contours to a text file in real-time
        """

        # UI Progress and Status Messages
        progress_count = 0.0
        progress_previous = None
        increment = 100.0 / (len(data_ascii))
        self.status.emit('Current Part: %s | Formatting contour data...' %
                         os.path.basename(file_name).replace('_contours.txt', ''))
        self.progress.emit(0)

        # Initialize some variables to be used later
        units = data_ascii[0]
        layer_count = 0

        with open(file_name, 'w+') as contours_file:
            # Write the first line, the number of layers, to the text file
            contours_file.write('%s\n' % ['LAYERS', data_ascii[1]])

            for line in data_ascii[2::]:
                if 'LAYER' in line:
                    # Strip the newline character from the end, and split the string where the slash appears
                    line = re.split('(/)', line.rstrip('\n'))
                    if layer_count is not 0:
                        contours_file.write('%s\n' % ['ENDLAYER'])
                    layer_count += 1
                    contours_file.write('%s\n' % ['STARTLAYER%s' % str(layer_count).zfill(4), float(line[2]) * units])
                elif 'POLYLINE' in line:
                    # Split each number into its own entry in a list
                    # Remove all the comma elements and the first 3 numbers
                    line = re.split('(,)', line.rstrip('\r\n/n'))
                    line = [comma for comma in line if comma != ',']
                    # Store the contour coordinates as pixel units after taking scale factor into account
                    line = [int(round(float(element) * units * self.scale_factor)) for element in line[3:]]
                    contours_file.write('%s\n' % line)

                # Put into a conditional to only trigger if the whole number changes so as to not overload the emit
                progress_count += increment
                progress = int(5 * round(progress_count / 5))
                if not progress == progress_previous:
                    self.progress.emit(progress)
                    progress_previous = progress

                    self.check_flags()
                    while self.pause_flag:
                        self.status.emit('Current Part: %s | Conversion paused.' %
                                         os.path.basename(file_name).replace('_contours.txt', ''))
                        time.sleep(1)
                        self.check_flags()
                    if not self.run_flag:
                        self.status.emit('Current Part: %s | Conversion stopped.' %
                                         os.path.basename(file_name).replace('_contours.txt', ''))
                        self.draw_flag = False
                        return None

                    self.status.emit('Current Part: %s | Formatting contour data...' %
                                     os.path.basename(file_name).replace('_contours.txt', ''))

            # Write the final ENDLAYER to the contours file
            contours_file.write('%s\n' % ['ENDLAYER'])

    def draw_contours(self, file_names, part_colours, folder_name):
        """Draw all the contours of the selected parts on the same image"""

        # Make sure the received contours folder exists
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # UI Progress and Status Messages
        progress = 0.0
        progress_previous = None
        self.progress.emit(0)

        # Initial while loop conditions
        layer = 1
        layer_max = 10

        while layer <= layer_max:

            self.check_flags()
            while self.pause_flag:
                self.status.emit('Current Part: All | Drawing contours %s of %s paused.' %
                                 (str(layer).zfill(4), str(layer_max).zfill(4)))
                time.sleep(1)
                self.check_flags()
            if not self.run_flag:
                self.status.emit('Current Part: All | Conversion stopped.')
                return None

            # Create a black RGB image to draw contours on and one to write the part names on
            image_contours = np.zeros(self.image_resolution, np.uint8)
            image_names = np.zeros(self.image_resolution, np.uint8)

            for file_name in file_names:
                # Create an empty contours list to store all the contours of the current layer
                contours = list()
                contours_flag = False

                with open(file_name.replace('.cli', '_contours.txt').replace('.cls', '_contours.txt')) as contours_file:
                    for line in contours_file:
                        # Grab the contours and format them as a numpy array that drawContours accepts
                        if 'ENDLAYER' in line and contours_flag:
                            # Break to save a tiny bit of processing time once the current layer's contours are grabbed
                            break
                        elif contours_flag:
                            line = line.strip('[]\n').split(', ')
                            contours.append(np.array(line).reshape(1, len(line) // 2, 2).astype(np.int32))
                        elif 'STARTLAYER%s' % str(layer).zfill(4) in line:
                            contours_flag = True
                        elif 'LAYERS' in line:
                            line = line.strip('[]\n').split(', ')
                            if int(line[1]) > layer_max:
                                layer_max = int(line[1])

                # Draw the contours onto the image_contours canvas
                cv2.drawContours(image_contours, contours, -1,
                                 part_colours[os.path.splitext(os.path.basename(file_name))[0]],
                                 offset=self.offset, thickness=cv2.FILLED)

                # For the first layer, find the centre of the contours and put the part names on the image
                if layer == 1:
                    moments = cv2.moments(contours[0])
                    centre_x = int(moments['m10'] / moments['m00'])
                    centre_y = abs(self.image_resolution[0] - int(moments['m01'] / moments['m00']))
                    cv2.putText(image_names, os.path.splitext(os.path.basename(file_name))[0], (centre_x, centre_y),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5, cv2.LINE_AA)

            self.status.emit('Current Part: All | Drawing contours %s of %s.' %
                             (str(layer).zfill(4), str(layer_max).zfill(4)))

            # Flip the image vertically to account for the fact that OpenCV's origin is the top left corner
            image_contours = cv2.flip(image_contours, 0)

            # Correct the image using calculated transformation parameters to account for the perspective warp
            image_contours = image_processing.ImageTransform(None).transform(image_contours, self.transform)

            # Save the image to the selected image folder
            cv2.imwrite('%s/contours_%s.png' % (folder_name, str(layer).zfill(4)), image_contours)

            # Save the part names image after transforming it just like the contours image
            if layer == 1:
                image_names = image_processing.ImageTransform(None).transform(image_names, self.transform)
                cv2.imwrite('%s/part_names.png' % self.config['ImageCapture']['Folder'], image_names)

            # Increment to the next layer
            layer += 1

            progress += 100.0 / layer_max
            if int(round(progress)) is not progress_previous:
                self.progress.emit(int(round(progress)))
                progress_previous = int(round(progress))

    def check_flags(self):
        """Checks the respective Run and Pause keys from the config.json file"""

        with open('config.json') as config:
            self.config = json.load(config)

        if self.config['SliceConverter']['Build']:
            self.run_flag = self.config['BuildInfo']['Run']
            self.pause_flag = self.config['BuildInfo']['Pause']
        else:
            self.run_flag = self.config['SliceConverter']['Run']
            self.pause_flag = self.config['SliceConverter']['Pause']
