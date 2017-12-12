# Import external libraries
import os
import time
import cv2
import numpy as np
import json

# Import related modules
import image_processing


class SliceConverter:
    """Module used to convert any slice files from .cli format into ASCII format
    Output can then be used to draw contours using OpenCV
    Currently takes in a .cli file and parses it, saving it as a .txt file after conversion
    """

    def __init__(self):

        # Flags that will be dictated from the config.json file that control whether to run/stop or pause/resume
        self.run_flag = True
        self.pause_flag = False

        # Load from the config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        # Save respective values to be used to draw contours and polygons
        # Get the resolution of the cropped images using the crop boundaries, 3 at the end indicates an RGB image
        self.image_resolution = tuple(self.config['ImageCorrection']['ImageResolution'] + [3])
        self.offset = tuple(self.config['ImageCorrection']['Offset'])
        self.scale_factor = self.config['ImageCorrection']['ScaleFactor']

        # Part names are taken from the build.json file, depending if this method was run from the Slice Converter
        # Or as part of a new build, different files will be read and used
        # if self.build['SliceConverter']['Build']:
        #     self.part_colours = self.build['BuildInfo']['Colours']
        #     self.filenames = self.build['BuildInfo']['SliceFiles']
        #     self.range_flag = False
        #     self.contours_folder = '%s/contours' % self.build['ImageCapture']['Folder']
        # else:
        #     self.part_colours = self.build['SliceConverter']['Colours']
        #     self.filenames = self.build['SliceConverter']['Files']
        #     self.range_flag = self.build['SliceConverter']['Range']
        #     self.contours_folder = self.build['SliceConverter']['Folder']

    def run_converter(self, status, progress):

        # Assign the status and progress signals as instance variables so other methods can use them
        self.status = status
        self.progress = progress

        for filename in self.filenames:
            # Look for an already converted contours file, otherwise convert the cli file
            if not os.path.isfile(filename.replace('.cli', '_contours.txt')):
                self.convert_cli(filename)

        # Draw and save the contours to an image file
        if self.draw_contours(self.filenames, self.part_colours, self.contours_folder):
            self.status.emit('Current Part: None | Conversion completed successfully.')

    def convert_cli(self, filename, status, progress):
        """Reads the .cli file and converts the contents from binary into an organised ASCII contour list"""

        # TODO remove timers if not needed
        t0 = time.time()

        # UI Progress and Status Messages
        progress_previous = None
        part_name = os.path.splitext(os.path.basename(filename))[0]
        status.emit('%s | Converting CLI file...' % part_name)
        progress.emit(0)

        # Set up counters
        layer_flag = False
        polyline_count = 0
        vector_count = 0
        header_length = 0
        max_layers = 0

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
            increment = 100 / (os.path.getsize(filename) - header_length) * 2
            progress_count = header_length * increment

            # Read the rest of the data
            data = cli_file.read()

        with open(filename.replace('.cli', '_contours.txt'), 'w+') as contours_file:
            # Iterate through every character in the file two at a time
            for one, two in zip(data[0::2], data[1::2]):
                # Convert into binary and join two elements, then convert to decimal
                decimal = int(bin(two)[2:].zfill(8) + bin(one)[2:].zfill(8), 2)

                if layer_flag:
                    # Because the number directly after a 128 represents the layer height, this flag skips the number
                    layer_flag = False
                    max_layers += 1
                elif polyline_count > 0:
                    polyline_count -= 1
                    if polyline_count == 0:
                        vector_count = decimal * 2
                elif vector_count > 0:
                    # Write the converted value to the text file
                    contours_file.write('%s,' % round(decimal * units * self.scale_factor))
                    vector_count -= 1
                elif decimal == 128:
                    # 128 indicates a new layer
                    contours_file.write('\n')
                    layer_flag = True
                elif decimal == 129:
                    # 129 indicates a polyline, or a new contour, which will be indicated by a C,
                    contours_file.write('C,')
                    polyline_count = 3

                # Put into a conditional to only trigger at every interval of 5 so as to not overload the emit
                progress_count += increment
                progress_current = 5 * round(progress_count / 5)
                if not progress_current == progress_previous:
                    progress.emit(progress_current)
                    progress_previous = progress_current

        progress.emit(100)

        print('Read CLI %s + READ Time\n%s\n' % (part_name, time.time() - t0))

        return max_layers

    def draw_contours(self, filenames, part_colours, range, folder, status, progress):
        """Draw all the contours of the selected parts on the same image"""

        # Make sure the received contours folder exists
        if not os.path.exists(folder):
            os.makedirs(folder)

        # UI Progress and Status Messages
        progress_current = 0.0
        progress_previous = None
        progress.emit(0)

        # Set up values and a dictionary
        layer_low = 1
        layer_high = 1
        contour_dict = dict()

        status.emit('Current Part: All | Loading contours into memory...')

        # Read all the contour files into memory and save them to a dictionary
        for filename in filenames:
            with open(filename.replace('.cli', '_contours.txt')) as contours_file:
                contour_dict[os.path.basename(filename)] = contours_file.readlines()

                # Get the maximum number of layers from the number of lines in the contour list
                # Subtract 1 because of the empty first element (used to correlate layer with index)
                size = len(contour_dict[os.path.basename(filename)]) - 1
                if size > layer_high:
                    layer_high = size

        # Change the layer low and high range if the user has specified a range of layers to draw
        if self.range_flag:
            # Check if the set range values are within the parts' layer range
            if self.build['SliceConverter']['RangeLow'] > layer_high or \
                            self.build['SliceConverter']['RangeHigh'] > layer_high:
                self.status.emit('Current Part: All | Set range outside of part contour layer range.')
                return False
            else:
                layer_low = self.build['SliceConverter']['RangeLow']
                layer_high = self.build['SliceConverter']['RangeHigh']

        # Calculate the correct progress increment value to use
        increment = 100 / (layer_high + 1 - layer_low)

        # Create a blank black RGB image to write the part names on
        image_names = np.zeros(self.image_resolution, np.uint8)

        # Iterate through all the layers, the maximum value is raised by 1 so that the last contour is drawn
        for layer in range(layer_low, layer_high + 1):

            # TODO remove timers if not needed
            t0 = time.time()

            status.emit('Current Part: All | Drawing contours %s of %s.' %
                             (str(layer).zfill(4), str(layer_high).zfill(4)))

            # Create a blank black RGB image to draw contours on
            image_contours = np.zeros(self.image_resolution, np.uint8)

            # Clear the contours list
            contours = list()

            # Iterate through all the parts
            for filename in filenames:
                # Try accessing the current layer index of the corresponding part contours list
                try:
                    contour_string = contour_dict[os.path.basename(filename)][layer]
                except IndexError:
                    # If the layer doesn't exist (because the part is finished), continue to the next iteration
                    continue

                # Split up the string into a list based on the C, delimiter (and throw away the first element)
                contour_string = contour_string.split('C,')[1::]

                # Since there might be multiple contours in the one layer
                for string in contour_string:
                    # Convert the string of numbers into a list of vectors using the comma delimiter
                    vectors = string.split(',')[:-1]
                    # Convert the above list of vectors into a numpy array of vectors and append it to the contours list
                    contours.append(np.array(vectors).reshape(1, len(vectors) // 2, 2).astype(np.int32))

                # For the first layer, find the centre of the contours and put the part names on a blank image
                if layer == 1:
                    # The first contour is generally the largest one, regardless the exact position isn't important
                    moments = cv2.moments(contours[0])
                    centre_x = int(moments['m10'] / moments['m00'])
                    centre_y = abs(self.image_resolution[0] - int(moments['m01'] / moments['m00']))
                    cv2.putText(image_names, os.path.splitext(os.path.basename(filename))[0], (centre_x, centre_y),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5, cv2.LINE_AA)

            # Draw all the contours onto the image_contours canvas at once
            cv2.drawContours(image_contours, contours, -1,
                             part_colours[os.path.splitext(os.path.basename(filename))[0]],
                             offset=self.offset, thickness=cv2.FILLED)

            # Flip the image vertically to account for the fact that OpenCV's origin is the top left corner
            image_contours = cv2.flip(image_contours, 0)

            # Correct the image using calculated transformation parameters to account for the perspective warp
            image_contours = image_processing.ImageTransform().apply_transformation(image_contours, False)

            # Save the image to the selected image folder
            cv2.imwrite('%s/contours_%s.png' % (folder, str(layer).zfill(4)), image_contours)

            # Save the part names image to the contours up one folder after transforming it just like the contours image
            if layer == 1:
                image_names = image_processing.ImageTransform().apply_transformation(image_names, False)
                cv2.imwrite('%s/part_names.png' % os.path.dirname(folder), image_names)

            progress_current += increment
            if round(progress_current) is not progress_previous:
                self.progress.emit(round(progress_current))
                progress_previous = round(progress_current)

            print('Contour %s Time\n%s\n' % (layer, time.time() - t0))

        return True
