# Import external libraries
import os
import cv2
import numpy as np


class SliceConverter:
    """Module used to convert any slice files from .cli format into ASCII format
    The .cli file is parsed, converting from binary to decimal, and outputted as a .txt file of contours
    These contours can then be subsequently drawn using OpenCV while taking scaling and the ROI into account
    """

    @staticmethod
    def convert_cli(filename, scale, status, progress):
        """Reads the .cli file and converts the contents from binary into an organised ASCII contour list"""

        # UI Progress and Status Messages
        progress_previous = None
        part_name = os.path.splitext(os.path.basename(filename))[0]
        status.emit('%s | Converting CLI file...' % part_name)
        progress.emit(0)

        # Initialize a few values and flags
        polyline_count = 0
        vector_count = 0
        header_length = 0
        layer_flag = False
        beginning_flag = True

        # File needs to be opened and read as binary as it is encoded in binary
        with open(filename, 'rb') as cli_file:
            # Get unit information from the header by reading the first few lines and storing it to be used later
            for line in cli_file.readlines():
                if b'UNITS' in line:
                    units = float(line[8:-2])
                elif b'LAYERS' in line:
                    layers = int(line[9:-1])
                elif b'HEADEREND' in line:
                    # Break out of the header loop and add the $$HEADEREND length of 11 characters
                    header_length += 11
                    break

                # Accumulate the length of the header (in bytes) to calculate the increment for the rest of the file
                header_length += len(line)

            # Return to the end of the header
            cli_file.seek(header_length)

            # Calculate the increment to use to display progress for the rest of the file data
            increment = 100 / (os.path.getsize(filename) - header_length) * 2
            progress_count = header_length * increment

            # Read the rest of the data
            data = cli_file.read()

        # Create and open the corresponding contours .txt file for the current .cli file
        with open(filename.replace('.cli', '_contours.txt'), 'w+') as contours_file:
            # Iterate through every character in the file two at a time
            for one, two in zip(data[0::2], data[1::2]):
                # Convert (from hexadecimal) into binary and join two elements, then convert to decimal
                decimal = int(bin(two)[2:].zfill(8) + bin(one)[2:].zfill(8), 2)

                # Figure out what to do with the decimal number depending on what the current (or previous) number is
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
                    contours_file.write('%s,' % round(decimal * units * scale))
                    vector_count -= 1
                elif decimal == 128:
                    # 128 indicates a new layer
                    if beginning_flag:
                        # Write the number of layers at the beginning of the file
                        contours_file.write('%s\n' % layers)
                        beginning_flag = False
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

    @staticmethod
    def draw_contours(contour_dict, image, layer, colours, transform, folder, thickness, roi_offset, names_flag,
                      save_flag, roi):
        """Draw all the contours of the received parts and of the received layer on the same image"""

        if names_flag:
            # Copy a blank black RGB image using the received image's size to write the part names on
            image_names = np.zeros(image.shape, np.uint8)

        # Initialize values in order to calculate the ROI of all the part contours
        min_x, min_y = image.shape[1], image.shape[0]
        max_x = max_y = 0

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

            # Since there might be multiple contours for a given part
            for string in contour_string:
                # Convert the string of numbers into a list of vectors using the comma delimiter
                vectors = string.split(',')[:-1]
                # Convert the above list of vectors into a numpy array of vectors and append it to the contours list
                contours.append(np.array(vectors).reshape(1, len(vectors) // 2, 2).astype(np.int32))

            # Offset the offset by the transform parameters for the current part
            offset = tuple(transform[part_name][:2])

            # Block of code responsible for rotation of the current part if an angle has been specified
            if transform[part_name][2]:
                # Calculate the centre of the largest contour using contour moments (also offset by translation)
                moments = cv2.moments(max(contours, key=cv2.contourArea))
                centre = (int(moments['m10'] // moments['m00']), int(moments['m01'] // moments['m00']))

                # Calculate the rotation matrix and rotate the part around it's centre axis
                rotation_matrix = cv2.getRotationMatrix2D(centre, transform[part_name][2], 1)

                # Rotate each of the contours (in place)
                for index, item in enumerate(contours):
                    contours[index] = cv2.transform(item, rotation_matrix)

            # Find the minimum and maximum X and Y values to create a bounding box surrounding all the parts
            if roi_offset:
                for item in contours:
                    x, y, w, h = cv2.boundingRect(item)
                    min_x, max_x = min(x, min_x), max(x + w, max_x)
                    min_y, max_y = min(y, min_y), max(y + h, max_y)

            # Draw all the contours on the received image
            cv2.drawContours(image, contours, -1, colours[part_name], offset=offset, thickness=thickness)

            # If set, find the centre of the largest contours and put the part names on a blank image
            if names_flag:
                moments = cv2.moments(max(contours, key=cv2.contourArea))
                # The Y value is subtracted from the height to 'flip' the coordinates without flipping the text itself
                centre = (int(moments['m10'] // moments['m00']) + offset[0],
                          abs(image.shape[0] - (int(moments['m01'] // moments['m00'] + offset[1]))))
                cv2.putText(image_names, part_name, centre, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Flip the whole image vertically to account for the fact that OpenCV's origin is the top left corner
        image = cv2.flip(image, 0)

        # Apply the offset to the region of interest
        if roi_offset:
            min_x -= roi_offset
            max_x += roi_offset
            min_y = abs(min_y - roi_offset - image.shape[0])
            max_y = abs(max_y + roi_offset - image.shape[0])
            roi.emit([min_x, max_y, max_x - min_x, min_y - max_y], False)

        if names_flag:
            cv2.imwrite('%s/part_names.png' % os.path.dirname(folder), image_names)

        # Save the image to the selected image folder
        if save_flag:
            cv2.imwrite('%s/contours_%s.png' % (folder, str(layer).zfill(4)), image)
        else:
            return image
