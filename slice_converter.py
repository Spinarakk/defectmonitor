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

        # Load from the config.json file
        with open('config.json') as config:
            self.config = json.load(config)

    def convert_cli(self, filename, status, progress):
        """Reads the .cli file and converts the contents from binary into an organised ASCII contour list"""

        # TODO remove timers if not needed
        t0 = time.time()

        # UI Progress and Status Messages
        progress_previous = None
        part_name = os.path.splitext(os.path.basename(filename))[0]
        status.emit('%s | Converting CLI file...' % part_name)
        progress.emit(0)

        # Set up values
        layer_flag = False
        polyline_count = 0
        vector_count = 0
        header_length = 0
        start_flag = True

        # File needs to be opened and read as binary as it is encoded in binary
        with open(filename, 'rb') as cli_file:
            # Get unit information from the header by reading the first few lines and storing it to be used later
            for line in cli_file.readlines():
                if b'UNITS' in line:
                    units = float(line[8:-2])
                elif b'LAYERS' in line:
                    layers = int(line[9:-1])
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
                    # The number directly after a 128 represents the layer height, which is written as the first value
                    contours_file.write('%s' % round((decimal * units), 3))
                    layer_flag = False
                elif polyline_count > 0:
                    polyline_count -= 1
                    if polyline_count == 0:
                        vector_count = decimal * 2
                elif vector_count > 0:
                    # Write the converted value to the text file
                    contours_file.write('%s,' % round(decimal * units * self.config['ImageCorrection']['ScaleFactor']))
                    vector_count -= 1
                elif decimal == 128:
                    # 128 indicates a new layer
                    if start_flag:
                        # Write the number of layers as the very first line
                        contours_file.write('%s\n' % layers)
                        start_flag = False
                    else:
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

    def draw_contour(self, contour_dict, layer, part_colours, part_transform, folder, names_flag):
        """Draw all the contours of the selected parts on the same image"""

        # TODO remove timers if not needed
        t0 = time.time()

        # Grab a few values to be used to draw contours and polygons
        # 3 at the end of the resolution indicates an RGB image
        image_resolution = tuple(self.config['ImageCorrection']['ImageResolution'] + [3])
        offset = tuple(self.config['ImageCorrection']['Offset'])

        if names_flag:
            # Create a blank black RGB image to write the part names on
            image_names = np.zeros(image_resolution, np.uint8)

        # Create a blank black RGB image to draw contours on
        image_contours = np.zeros(image_resolution, np.uint8)

        # Iterate through all the parts
        for part_name, contour_list in contour_dict.items():
            # Try accessing the current layer index of the corresponding part contours list
            try:
                # Split up the string into a list based on the C, delimiter which represents one contour
                # First element is the layer height which is unneeded to draw the contours
                contour_string = contour_list[layer].split('C,')[1::]
            except IndexError:
                # If the layer doesn't exist (because the part is finished), continue to the next iteration
                continue

            # Clear the contours list
            contours = list()

            # Since there might be multiple contours in the one layer
            for string in contour_string:
                # Convert the string of numbers into a list of vectors using the comma delimiter
                vectors = string.split(',')[:-1]
                # Convert the above list of vectors into a numpy array of vectors and append it to the contours list
                contours.append(np.array(vectors).reshape(1, len(vectors) // 2, 2).astype(np.int32))

            cv2.drawContours(image_contours, contours, -1, part_colours[part_name], offset=offset, thickness=cv2.FILLED)

            # For the first layer, find the centre of the contours and put the part names on a blank image
            if names_flag:
                # The first contour is generally the largest one, regardless the exact position isn't important
                moments = cv2.moments(contours[0])
                centre_x = int(moments['m10'] / moments['m00'])
                centre_y = abs(image_resolution[0] - int(moments['m01'] / moments['m00']))
                cv2.putText(image_names, part_name, (centre_x, centre_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5, cv2.LINE_AA)

        # Flip the whole image vertically to account for the fact that OpenCV's origin is the top left corner
        image_contours = cv2.flip(image_contours, 0)

        # Correct the image using calculated transformation parameters to account for the perspective warp
        #image_contours = image_processing.ImageTransform().apply_transformation(image_contours, False)

        # Save the image to the selected image folder
        cv2.imwrite('%s/contours_%s.png' % (folder, str(layer).zfill(4)), image_contours)

        # Save the part names image to the contours up one folder after transforming it just like the contours image
        if names_flag:
            image_names = image_processing.ImageTransform().apply_transformation(image_names, False)
            cv2.imwrite('%s/part_names.png' % os.path.dirname(folder), image_names)

        print('Contour %s Time\n%s\n' % (layer, time.time() - t0))
