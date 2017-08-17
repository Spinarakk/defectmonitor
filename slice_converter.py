# Import external libraries
import os
import re
import json
import cv2
import numpy as np
from PyQt4.QtCore import QThread, SIGNAL

import image_processing

class SliceConverter(QThread):
    """Module used to convert any slice files from .cls or .cli format into ASCII format
    Output can then be used to draw contours using OpenCV
    Currently only supports converting .cls files
    Future implementation will look to either shifting or adding .cli slice conversion

    Currently takes in a .cls or .cli file and parses it, saving it as a .txt file after conversion
    """

    def __init__(self, file_names, contours_flag, fill_flag, combine_flag):

        # Defines the class as a thread
        QThread.__init__(self)

        # Load configuration settings from config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Save respective values to be used to draw contours and polygons
        # Get the resolution of the cropped images using the crop boundaries
        self.image_resolution = ((self.config['CropBoundary'][1] - self.config['CropBoundary'][0]),
                                 (self.config['CropBoundary'][3] - self.config['CropBoundary'][2]))
        self.offset = (self.config['Offset'][0], self.config['Offset'][1])
        self.scale_factor = self.config['ScaleFactor']
        self.transform = self.config['TransformationParameters']

        # Store the received arguments as local instance variables
        self.file_names = file_names
        self.contours_flag = contours_flag
        self.fill_flag = fill_flag
        self.combine_flag = combine_flag

    def run(self):

        max_layers = 0

        for file_name in self.file_names:

            self.emit(SIGNAL("update_status_slice(QString)"), os.path.basename(file_name))

            # Executes if the sent file is a .cls file
            if '.cls' in file_name:
                # Look for an already converted contours file
                if os.path.isfile(file_name.replace('.cls', '_cls_contours.txt')):
                    self.emit(SIGNAL("update_status(QString)"), 'CLS contours file found. Loading from disk...')
                    data_cls = self.load_contours(file_name.replace('.cls', '_cls_contours.txt'))
                    data_cls[1] = int(data_cli[1].strip('\n'))
                else:
                    data_cls = self.read_cls(file_name)
                    data_cls = self.convert2contours(data_cls)
                    self.emit(SIGNAL("update_status(QString)"), 'Saving to .txt file...')
                    self.save_contours(file_name.replace('.cls', '_cls_contours.txt'), data_cls)

                if data_cls['Layers'] > max_layers:
                    max_layers = data_cls['Layers']

                if self.contours_flag:
                    self.emit(SIGNAL("update_status(QString)"), 'Drawing Contours.')
                    self.draw_contours(data_cls, file_name)

            # Executes if the sent file is a .cli file
            elif '.cli' in file_name:
                # Look for an already converted contours file
                if os.path.isfile(file_name.replace('.cli', '_cli_contours.txt')):
                    self.emit(SIGNAL("update_status(QString)"), 'CLI contours file found. Loading from disk...')
                    data_cli = self.load_contours(file_name.replace('.cli', '_cli_contours.txt'))
                    data_cli[1] = int(data_cli[1].strip('\n'))
                else:
                    data_cli = self.read_cli(file_name)
                    data_cli = self.convert2contours(data_cli)
                    self.emit(SIGNAL("update_status(QString)"), 'Saving to .txt file...')
                    self.save_contours(file_name.replace('.cli', '_cli_contours.txt'), data_cli)

                if data_cli[1] > max_layers:
                    max_layers = data_cli[1]

                if self.contours_flag:
                    self.emit(SIGNAL("update_status(QString)"), 'Drawing Contours.')
                    self.draw_contours(data_cli, file_name)
            else:
                self.emit(SIGNAL("update_status(QString)"), 'Slice file not found.')

        if self.combine_flag:

            blue = 20
            green = 40
            red = 60

            contour_colours = dict()
            for file_name in self.file_names:
                contour_colours['%s' % os.path.basename(file_name)] = (blue, green, red)
                blue = (blue + 20) % 255
                green = (green + 40) % 255
                red = (red + 60) % 150

            self.emit(SIGNAL("update_status_slice(QString)"), 'All.')
            self.emit(SIGNAL("update_progress(QString)"), '0')

            progress = 0.0
            progress_previous = None

            for index in xrange(1, max_layers):
                # UI Progress and Status Messages


                self.emit(SIGNAL("update_status(QString)"), 'Combining contour %s of %s.' %
                          (str(index).zfill(4), str(max_layers).zfill(4)))

                image_contours = np.zeros(self.image_resolution).astype(np.uint8)
                image_contours = cv2.cvtColor(image_contours, cv2.COLOR_GRAY2BGR)

                contour_flag = False
                contours = list()

                for file_name in self.file_names:
                    with open(file_name.replace('.cli', '_cli_contours.txt').replace('.cls', 'cls_contours.txt')) as contour_file:
                        for line in contour_file:
                            if 'ENDLAYER' in line:
                                contour_flag = False
                            if contour_flag:
                                line = line.strip('[]\n').split(', ')
                                contours.append(np.array(line).reshape(1, len(line)/2, 2).astype(np.int32))
                            if 'STARTLAYER%s' % str(index).zfill(4) in line:
                                contour_flag = True

                    # If the Fill Contours checkbox is checked, fill the contours, otherwise just draw the contours itself
                    if self.fill_flag:
                        cv2.drawContours(image_contours, contours, -1, contour_colours['%s' % os.path.basename(file_name)], offset=self.offset,
                                         thickness=cv2.FILLED)
                        #fill = '_fill'
                    else:
                        cv2.drawContours(image_contours, contours, -1, contour_colours['%s' % os.path.basename(file_name)], offset=self.offset,
                                         thickness=int(self.scale_factor))
                        #fill = ''

                    contours = list()

                image_contours = cv2.flip(image_contours, 0)
                image_contours = image_processing.ImageCorrection(None).transform(image_contours, self.transform)

                cv2.imwrite('%s/contours/image_contours_%s.png' %
                            (self.config['ImageFolder'], str(index).zfill(4)), image_contours)

                # Put into a conditional to only trigger if the whole number changes so as to not overload the emit
                if int(round(progress)) is not progress_previous:
                    self.emit(SIGNAL("update_progress(QString)"), str(int(round(progress))))
                    progress_previous = int(round(progress))
                progress += 100.0 / max_layers

    def read_cls(self, file_name):
        """Parses and converts the .cls file into ASCII"""

        self.emit(SIGNAL("update_status(QString)"), 'Reading CLS file...')

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
            self.emit(SIGNAL("update_progress(QString)"), '8')
            # Remove any NoneType data in the list
            data_binary = filter(None, data_binary)
            increment = 90.0 / len(data_binary)
            self.emit(SIGNAL("update_progress(QString)"), str(int(round(progress))))

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
                    self.emit(SIGNAL("update_progress(QString)"), str(int(round(progress))))
                    progress_previous = int(round(progress))
                progress += increment

        return data_ascii

    def read_cli(self, file_name):
        """Reads the .cli file and converts the contents into an organised list
        If the file was encoded in binary, this method also converts the contents into ascii format"""

        self.emit(SIGNAL("update_status(QString)"), 'Reading CLI file...')

        # Set up a few flags, counters and lists
        binary_flag = False
        data_ascii = list()
        line_ascii = ''

        # UI Progress and Status Messages
        progress = 0.0
        progress_previous = None

        # Open the .cli file
        with open(file_name, 'r') as cli_file:
            increment = 100.0 / sum(1 for _ in cli_file)
            # Go back to the start of the file as getting the length of the file put the seek head to the EOF
            cli_file.seek(0)
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
                progress += increment

            for line in cli_file:
                if binary_flag:
                    break
                # Check if the line is empty or not (because of the removal of random newline characters
                if line.rstrip('\r\n/n'):
                    data_ascii.append(line.rstrip('\r\n/n'))
                # Put into a conditional to only trigger if the whole number changes so as to not overload the emit
                if int(round(progress)) is not progress_previous:
                    self.emit(SIGNAL("update_progress(QString)"), str(int(round(progress))))
                    progress_previous = int(round(progress))
                progress += increment

        if binary_flag:
            self.emit(SIGNAL("update_status(QString)"), 'Reading CLI file... Binary encoding detected.')
            progress = 0.0
            progress_previous = None

            # The file needs to be read as binary if it was encoded in binary
            with open(file_name, 'rb') as cli_file:
                increment = 100.0 / sum(1 for _ in cli_file)
                # Go back to the start of the file as getting the length of the file put the seek head to the EOF
                cli_file.seek(0)
                for line in cli_file:
                    if 'UNITS' in line.strip():
                        data_ascii.append(float(line[8:-2]))
                    elif 'HEADEREND' in line.strip():
                        data_binary = line.replace('$$HEADEREND', '')
                        break
                for line in cli_file:
                    data_binary += line
                    # Put into a conditional to only trigger if the whole number changes so as to not overload the emit
                    if int(round(progress)) is not progress_previous:
                        self.emit(SIGNAL("update_progress(QString)"), str(int(round(progress))))
                        progress_previous = int(round(progress))
                    progress += increment

            layer_flag = True
            polyline_count = 10

            # UI Progress and Status Messages
            progress = 0.0
            progress_previous = None
            increment = 100.0 / (len(data_binary) / 2.0)
            self.emit(SIGNAL("update_status(QString)"), 'Converting Binary into ASCII...')

            for one, two in zip(data_binary[0::2], data_binary[1::2]):
                # Convert the character unicode into an integer, then into a binary number
                # Join the second binary number with the first binary number and convert the 16-bit bin number into int
                decimal = int(bin(ord(two))[2:].zfill(8) + bin(ord(one))[2:].zfill(8), 2)
                # Check for command indexes and replace with appropriate ascii words
                if not layer_flag:
                    line_ascii += (str(decimal) + ',')
                    layer_flag = True
                elif decimal == 128 and layer_flag:
                    data_ascii.append(line_ascii.rstrip(','))
                    line_ascii = '$$LAYER/'
                    layer_flag = False
                elif decimal == 129 and polyline_count >= 5:
                    data_ascii.append(line_ascii.rstrip(','))
                    line_ascii = '$$POLYLINE/'
                    polyline_count = 0
                else:
                    line_ascii += (str(decimal) + ',')
                    polyline_count += 1

                # Put into a conditional to only trigger if the whole number changes so as to not overload the emit
                if int(round(progress)) is not progress_previous:
                    self.emit(SIGNAL("update_progress(QString)"), str(int(round(progress))))
                    progress_previous = int(round(progress))
                progress += increment

        return data_ascii

    def convert2contours(self, data_ascii):
        """Converts the data from the slice file into an organized scaled list of contours
        First element is the units the contours are in
        Second element is the number of units
        Every layer starts with a LAYER/XX/YY string followed with the strings of contours, followed with a LAYER/END
        XX refers to the layer height, YY refers to the number of contours
        """

        # UI Progress and Status Messages
        progress = 0.0
        progress_previous = None
        increment = 100.0 / (len(data_ascii))
        self.emit(SIGNAL("update_status(QString)"), 'Converting data into organized list of contours...')

        #data = OrderedDict()
        #data['Units'] = data_ascii[0]
        #data['Layers'] = 0
        data = [data_ascii[0], 0]

        layer_no = 0
        contour_no = 0
        index = 1

        for line in data_ascii[1::]:
            if 'LAYER' in line:
                # Strip the newline character from the end, and split the string where the slash appears
                line = re.split('(/)', line.rstrip('\n'))
                # Store the number of contours the current layer has
                if layer_no is not 0:
                    data[index - contour_no][2] = contour_no
                    data.append('ENDLAYER')
                    index += 1
                # Create a key for each layer's height
                layer_no += 1
                data.append(['STARTLAYER%s' % str(layer_no).zfill(4), int(line[2]), 0])
                index += 1
                #data['Layer %s Height' % str(layer_no).zfill(4)] = int(line[2])
                contour_no = 0
            elif 'POLYLINE' in line:
                contour_no += 1
                # Split each number into its own entry in a list, remove all the comma elements and the first 3 numbers
                line = re.split('(,)', line.rstrip('\r\n/n'))
                line = [comma for comma in line if comma != ',']
                # Store the contour coordinates as pixel units after taking scale factor into account
                line = [int(round(float(element) * data[0] * self.scale_factor)) for element in line[3:]]
                data.append(line)
                #data['Layer %s Contour %s' % (str(layer_no).zfill(4), str(contour_no).zfill(2))] = line
                index += 1

            # Put into a conditional to only trigger if the whole number changes so as to not overload the emit
            if int(round(progress)) is not progress_previous:
                self.emit(SIGNAL("update_progress(QString)"), str(int(round(progress))))
                progress_previous = int(round(progress))
            progress += increment

        # Set the layer contour number for the last layer
        #data['Layer %s Contour No.' % str(layer_no).zfill(4)] = contour_no
        #data['Layers'] = layer_no
        data[index - contour_no][2] = contour_no
        data.append('ENDLAYER')
        data[1] = layer_no

        self.emit(SIGNAL("update_status(QString)"), 'Conversion complete. Returning array to main function...')

        return data

    def draw_contours(self, data, file_name):
        # Create a folder in the working directory to store the contours
        # Folder name created by taking the input slice file's name and getting rid of the .cls or .cli
        folder_name = '%s/contours/%s' % (self.config['WorkingDirectory'],
                                          os.path.basename(str(file_name)).replace('.cls', '').replace('.cli', ''))
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # UI Progress and Status Messages
        progress = 0.0
        progress_previous = None

        for index in xrange(1, data[1] + 1):
            image_contours = np.zeros(self.image_resolution).astype(np.uint8)
            image_contours = cv2.cvtColor(image_contours, cv2.COLOR_GRAY2BGR)

            self.emit(SIGNAL("update_status(QString)"), 'Drawing contour %s of %s.' %
                      (str(index).zfill(4), str(data[1]).zfill(4)))

            # Put into a conditional to only trigger if the whole number changes so as to not overload the emit
            if int(round(progress)) is not progress_previous:
                self.emit(SIGNAL("update_progress(QString)"), str(int(round(progress))))
                progress_previous = int(round(progress))
            progress += 100.0 / data['Layers']

            contours = list()
            for contour_no in xrange(data['Layer %s Contour No.' % str(index).zfill(4)]):
                contours.append(data['Layer %s Contour %s' % (str(index).zfill(4), str(contour_no + 1).zfill(2))])
                contours[contour_no] = np.array(contours[contour_no]).reshape(1, len(contours[contour_no]) / 2,
                                                                              2).astype(np.int32)

            # If the Fill Contours checkbox is checked, fill the contours, otherwise just draw the contours itself
            if self.fill_flag:
                cv2.drawContours(image_contours, contours, -1, (128, 128, 0), offset=self.offset, thickness=cv2.FILLED)
                fill = '_fill'
            else:
                cv2.drawContours(image_contours, contours, -1, (128, 128, 0), offset=self.offset,
                                 thickness=int(self.scale_factor))
                fill = ''

            image_contours = cv2.flip(image_contours, 0)
            cv2.imwrite('%s/contours%s_%s.png' % (folder_name, fill, str(index).zfill(4)), image_contours)

    def transform_contours(self, image):
        """Applies image transformations that help the contour image match the scan image"""

    def load_contours(self, file_name):
        """Load the converted slice contours file from disk"""
        with open(file_name) as slice_file:
            return [next(slice_file) for line in xrange(2)]

    def save_contours(self, file_name, contours):
        """Save the converted slice contours file to disk"""
        with open(file_name, 'w+') as slice_file:
            for line in contours:
                slice_file.write('%s\n' % line)
