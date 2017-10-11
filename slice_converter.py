# Import external libraries
import os
import re
import time
import cv2
import numpy as np
import ujson as json

# Import related modules
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

        # Load from the config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Save respective values to be used to draw contours and polygons
        # Get the resolution of the cropped images using the crop boundaries, 3 at the end indicates an RGB image
        crop_boundary = self.config['ImageCorrection']['CropBoundary']
        self.image_resolution = ((crop_boundary[1] - crop_boundary[0]),
                                 (crop_boundary[3] - crop_boundary[2]), 3)
        self.offset = (self.config['ImageCorrection']['Offset'][0], self.config['ImageCorrection']['Offset'][1])
        self.scale_factor = self.config['ImageCorrection']['ScaleFactor']

        # Part names are taken from the build.json file, depending if this method was run from the Slice Converter
        # Or as part of a new build, different files will be read and used
        if self.build['SliceConverter']['Build']:
            self.part_colours = self.build['BuildInfo']['Colours']
            self.filenames = self.build['BuildInfo']['SliceFiles']
            self.draw_flag = self.build['BuildInfo']['Draw']
            self.contours_folder = '%s/contours' % self.build['ImageCapture']['Folder']
        else:
            self.part_colours = self.build['SliceConverter']['Colours']
            self.filenames = self.build['SliceConverter']['Files']
            self.draw_flag = self.build['SliceConverter']['Draw']
            self.contours_folder = self.build['SliceConverter']['Folder']

    def run_converter(self, status, progress):

        # Assign the status and progress signals as instance variables so other methods can use them
        self.status = status
        self.progress = progress

        for filename in self.filenames:
            # Executes if the sent file is a .cls file
            if '.cls' in filename:
                # Look for an already converted contours file, otherwise convert the cls file
                if not os.path.isfile(filename.replace('.cls', '.txt')):
                    self.convert_cls(filename)
            # Executes if the sent file is a .cli file
            elif '.cli' in filename:
                # Look for an already converted contours file, otherwise convert the cli file
                if not os.path.isfile(filename.replace('.cli', '.txt')):
                    self.convert_cli(filename)

        if self.draw_flag:
            # Draw and save the contours to an image file
            self.draw_contours(self.filenames, self.part_colours, self.contours_folder)

            if not self.run_flag:
                return

        self.status.emit('Current Part: None | Conversion completed successfully.')

    def convert_cls(self, filename):
        """Reads the .cli file and converts the contents from binary into an organised ASCII list"""

        self.status.emit('Current Part: %s | Reading CLS file...' % os.path.splitext(os.path.basename(filename))[0])

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

        with open(filename, 'rb') as cls_file:
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

    def convert_cli(self, filename):
        """Reads the .cli file and converts the contents from binary into an organised ASCII list"""

        # TODO remove timers if not needed
        t0 = time.time()

        # UI Progress and Status Messages
        progress_previous = None
        part_name = os.path.splitext(os.path.basename(filename))[0]
        self.status.emit('Current Part: %s | Reading CLI file...' % part_name)
        self.progress.emit(0)

        # Set up counters
        layer_flag = False
        polyline_count = 0
        vector_count = 0
        header_length = 0
        layer_count = 0
        # File needs to be opened and read as binary as it is encoded in binary
        with open(filename, 'rb') as cli_file:

            # Get unit information from the header by reading the first few lines and storing it to be used later
            for line in cli_file.readlines():
                if b'UNITS' in line:
                    units = float(line[8:-2])
                elif b'HEADEREND' in line:
                    # Break out of the header loop and add the $$HEADEREND length
                    header_length += 11
                    break

                # Measure the length of the header (in bytes) to calculate the increment for the rest of the file
                header_length += len(line)

            # Return to the end of the header
            cli_file.seek(header_length)

            # Calculate the increment to use to display progress for the rest of the file data
            increment = 100 / (os.path.getsize(filename) - header_length)
            progress_count = header_length * increment

            # Read the rest of the data
            data = cli_file.read()

        with open(filename.replace('.cli', '.txt'), 'w+') as contours_file:
            # Iterate through every character in the file two at a time
            for one, two in zip(data[0::2], data[1::2]):

                # Convert into binary and join two elements, then convert to decimal
                decimal = int(bin(two)[2:].zfill(8) + bin(one)[2:].zfill(8), 2)

                if layer_flag:
                    # Because the number directly after a 128 represents the layer height, this flag skips the number
                    layer_flag = False
                elif polyline_count > 0:
                    polyline_count -= 1
                    if polyline_count == 0:
                        vector_count = decimal * 2
                elif vector_count > 0:
                    # Convert the vectors after taking unit conversion and scale factor into account
                    decimal = int(decimal * units * self.scale_factor)
                    # Write the converted value to the text file
                    contours_file.write('%s,' % decimal)
                    vector_count -= 1
                elif decimal == 128:
                    # 128 indicates a new layer
                    layer_flag = True
                    contours_file.write('\n')
                elif decimal == 129:
                    # 129 indicates a polyline, or a new contour, which will be indicated by a C,
                    contours_file.write('C,')
                    polyline_count = 3

                # Put into a conditional to only trigger at every interval of 5 so as to not overload the emit
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
                        self.status.emit('Current Part: %s | Conversion paused.' % part_name)
                        time.sleep(1)
                        self.check_flags()
                    if not self.run_flag:
                        self.status.emit('Current Part: %s | Conversion stopped.' % part_name)
                        self.draw_flag = False
                        return None

                    self.status.emit('Current Part: %s | Reading CLI file...' % part_name)

        self.progress.emit(100)

        print('Read CLI %s + READ Time\n%s\n' % (part_name, time.time() - t0))

    def draw_contours(self, filenames, part_colours, folder):
        """Draw all the contours of the selected parts on the same image"""

        # Make sure the received contours folder exists
        if not os.path.exists(folder):
            os.makedirs(folder)

        # UI Progress and Status Messages
        progress = 0.0
        progress_previous = None
        self.progress.emit(0)

        # Set up values and a dictionary
        layer_max = 1
        contour_dict = dict()

        self.status.emit('Current Part: All | Loading contours into memory...')

        # Read all the contour files into memory and save them to a dictionary
        for filename in filenames:
            with open(filename.replace('.cli', '.txt')) as contours_file:
                contour_dict[os.path.basename(filename)] = contours_file.readlines()

                # Get the maximum number of layers from the number of lines in the contour list
                # Subtract 1 because of the empty first element (used to correlate layer with index)
                size = len(contour_dict[os.path.basename(filename)]) - 1
                if size > layer_max:
                    layer_max = size

        # Iterate through all the layers
        for layer in range(1, layer_max):

            # TODO remove timers if not needed
            t0 = time.time()

            self.status.emit('Current Part: All | Drawing contours %s of %s.' %
                             (str(layer).zfill(4), str(layer_max).zfill(4)))

            # Check if the process has been paused or stopped
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
            if layer == 1:
                image_names = np.zeros(self.image_resolution, np.uint8)

            # Iterate through all the parts
            for filename in filenames:

                # Clear the contours list
                contours = list()

                # Try accessing the current layer index of the corresponding part contours list
                try:
                    contour_string = contour_dict[os.path.basename(filename)][layer]
                except IndexError:
                    # If the layer doesn't exist (because the part has ended), continue to the next iteration
                    continue

                # Split up the string into a list based on the C, delimiter (and throw away the first element)
                contour_string = contour_string.split('C,')[1::]

                # Since there might be multiple contours in the one layer
                for string in contour_string:
                    # Convert the string of numbers into a list of vectors using the comma delimiter
                    vectors = string.split(',')[:-1]
                    # Convert the above list of vectors into a numpy array of vectors
                    contours.append(np.array(vectors).reshape(1, len(vectors) // 2, 2).astype(np.int32))

                # Draw the contours onto the image_contours canvas
                cv2.drawContours(image_contours, contours, -1,
                                 part_colours[os.path.splitext(os.path.basename(filename))[0]],
                                 offset=self.offset, thickness=cv2.FILLED)


                # For the first layer, find the centre of the contours and put the part names on a blank image
                if layer == 1:
                    # The first contour is generally the largest one, regardless the exact position isn't important
                    moments = cv2.moments(contours[0])
                    centre_x = int(moments['m10'] / moments['m00'])
                    centre_y = abs(self.image_resolution[0] - int(moments['m01'] / moments['m00']))
                    cv2.putText(image_names, os.path.splitext(os.path.basename(filename))[0], (centre_x, centre_y),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5, cv2.LINE_AA)

            # Flip the image vertically to account for the fact that OpenCV's origin is the top left corner
            image_contours = cv2.flip(image_contours, 0)

            # Correct the image using calculated transformation parameters to account for the perspective warp
            # image_contours = image_processing.ImageTransform().apply_transformation(image_contours, False)

            # Save the image to the selected image folder
            cv2.imwrite('%s/contours_%s.png' % (folder, str(layer).zfill(4)), image_contours)

            # Save the part names image to the contours up one folder after transforming it just like the contours image
            if layer == 1:
                image_names = image_processing.ImageTransform().apply_transformation(image_names, False)
                cv2.imwrite('%s/part_names.png' % os.path.dirname(folder), image_names)

            progress += 100.0 / layer_max
            if int(round(progress)) is not progress_previous:
                self.progress.emit(int(round(progress)))
                progress_previous = int(round(progress))

            print('Contour %s Time\n%s\n' % (layer, time.time() - t0))

    def check_flags(self):
        """Checks the respective Run and Pause keys from the config.json file"""

        # Load from the build.json file
        with open('build.json') as build:
            self.build = json.load(build)

        # Check if the current method was executed by a New Build or the Slice Converter
        if self.build['SliceConverter']['Build']:
            self.run_flag = self.build['BuildInfo']['Run']
            self.pause_flag = self.build['BuildInfo']['Pause']
        else:
            self.run_flag = self.build['SliceConverter']['Run']
            self.pause_flag = self.build['SliceConverter']['Pause']
