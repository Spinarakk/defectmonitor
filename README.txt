Defect Monitor
MCAM 3D Printer Software

Installation
- From the software folder install the following (64-bit Versions)
	- Python 2.7.13 (Remember to select add python.exe to PATH)
	- Basler Pylon 5.0.5.8999
	- PyQt4 4.11.4 GPL Py2.7 Qt4.8.7
	- PyCharm Professional 2017.1.2
- Extract OpenCV 3.2.0
	- Navigate to build/python/2.7/x86
	- Copy cv2.pyd into Python/Lib/site-packages
- Install the required Python packages as listed under Required Software
	- Open a command prompt
	- Navigate to the python/scripts folder (cd "Folder Name")
	- Run: pip install name_of_package

Important Note
- DO NOT MOVE, RENAME OR DELETE CONFIG_DEFAULT.JSON 

Operation
- Run main_window.py

Required Software
- Python 2.7.13
- OpenCV 3.2.0
- PyQt 4.11.4
- Basler Pylon 5.0.5.8999
	- Install in Developer Mode
	- Required to create New Build
- Python Packages:
	- numpy
	- pyserial
	- validate_email
Optional Software
- Pycharm 2017.1.2

Hardware
- Basler Ace acA3800-10gm GigE
	- CMOS Sensor
	- 10 FPS at 10 megapixels
	- 3856 x 2764 resolution
	- Grayscale
- Laptop running Windows 10

Core Functionality
- Start/Load a build and change settings as appropriate
- Take an image after the machine does both the scan and coat operations (2 images)
	- Setup camera parameters
	- Serial trigger using hall sensors in the machine
- Correct the image for distortions, perspective, crop, move, realign the origin
- Convert the .cls or .cli files into a format OpenCV can use
- Camera calibration using pre-taken checkboard images 
- Process the scan and coat images for defects
	- See below for defects
- Check if defects overlap the part countours
	- No
		- Ignore
		- Check if the defects may propogate into the part
	- Yes
		- Stop the operation
		- Send (push) notification to user
		- Error report
- Generate final report after part is completed
- Notification (instantaneous) for major defects
- Possible real-time interaction with the machine software to correct minor errors
	- Re-coating
	- Re-scanning (missed areas)
- Simple to use User Interface

List of Defects
Scan
- Inclusions
- Blobs of spatter within the part contours
- Scan failures, misses
Coat
- Blade streaks (horizontal divets)
- Blade chatter (vertical)
- Blade damage (dark sections near the start of the blade)
- Part warping bulging into the next coat
- Not enough powder for the coat
- Powder holes

Modules
main_window.py
- Contains code to setup the main window when you open the application
dialog_windows.py
- Contains code for all the dialog sub-windows that open when you click on various elements on the main window
image_capture.py
- Contains code for capturing images
- If simulation is checked, images are loaded from a sample folder
camera_calibration.py
- Contains code for calibrating the camera and generating the camera parameters and intrinsic values
slice_converter.py
- Contains code for converting the .cls or .cli file into a format OpenCV can use to draw contours
image_processing.py
- Contains code for processing the images
- Image correction
- Defect analysis and identification
extra_functions.py
- Contains miscellaneous functions that provide various bits of visual or minor QOL functionality

- Image Processing for Defects
- Slice Overlay & Comparison
- Report Generation
- Notification

Camera
- Has lots of features and changeable settings
- Most of these can be ignored as we are only using the camera to take one image every few seconds
- Software trigger through the Python program

Nomenclature Notes
- All CLASS names use CamelCaps
- All METHOD & VARIABLE names use full words in all lower caps with underscore spacing
- All INSTANCE (QThread) names use capital abbreviation of the called method + _instance
- All DICTIONARY keys use CamelCaps
- All PyQt GUI Object names use camelCaps with the first word being what the object is
- Similar code grouped in boxes with comment describing what that block does
- Variable naming schemes
	- XXX_name (Strings that contain a file/folder name)
	- XXX_file (The actual open file used within with blocks)
	- XXX_flag (Flags)
	- XXX_dialog (For dialog windows)
	- XXX_instance (For Qthread instances)
	- image_XXX (Image arrays)
- Comments will only be provided for the first time the function or block of code appears in the module, starting from the main_window module

GUI Standard Sizes
- Button Height -> 28
- Space between Vertical Buttons -> 6

How to Interpret Converted .cls Slice Files
- Layer X: Layer Height, 
- Layer X Border X: [Number of Vectors], <Length of Vectors>, Vectors (Twice as length)