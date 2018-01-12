Defect Monitor
MCAM 3D Printer Software

Installation
- Python 3.6.3
    - Camera only works on versions predating 3.6.3
    - Add python.exe to PATH
    - https://www.python.org/downloads/
- Basler Pylon
    - Latest Version
    - Need to install in Developer Mode
    - https://www.baslerweb.com/en/support/downloads/software-downloads/#type=pylonsoftware;language=all;version=all;os=windows;series=baslerace;model=all
- Execute package_installation.bat as administrator

- (Optional) PyCharm Professional
- (Optional) If a pypylon folder isn't in the root directory
    - pip3 install Cython
    - Visual C++ 14.0 will need to be installed (Google)
    - Open an admistrator command prompt
    - cd "random directory"
    - git clone https://github.com/mabl/PyPylon
    - cd PyPylon
    - python setup.py install
    - Pypylon should be installed in the site-packages folder of Python
    - Otherwise, copy the pypylon folder from the build/lib.win-(windowsver)-(pythonver) to Defect Monitor root directory
    - To the Defect Monitor root directory

Operation
- Execute run_program.bat

Hardware
- Basler Ace acA3800-10gm GigE
    - CMOS Sensor
    - 10 FPS at 10 megapixels
    - 3840 x 2748 resolution
    - Grayscale
- Windows 10 64-bit System

Core Functionality
- Start/Load a build and change settings as appropriate
- Take an image after the machine does both the scan and coat operations (2 images)
    - Serial trigger using hall sensors in the machine
- Correct the image for distortions, perspective, crop, move, realign the origin
- Convert the .cls or .cli files into contours that OpenCV can draw
- Camera calibration using pre-taken checkboard images 
- Process the scan and coat images for defects
    - See below for defects
- Check if defects overlap the part countours
    - No
	- Ignore
	- Check if the defects may propogate into the part
    - Yes
	- Stop the operation
	- Send notification to user
	- Error report
- Generate final report after part is completed
- Notification (instantaneous) for major defects
- Possible real-time interaction with the machine software
    - Correcting minor errors
    - Re-coating
    - Re-scanning (missed areas)
    - Halt for major errors (dosing error)
- Simple to use User Interface

Defect Detection
- Completed
    - Coat
	- Blade Streak (Horizontal divets caused by chips in blade)
	- Blade Chatter (Vertical slits caused by blade hitting parts)
	- Shiny Patch (Caused by insufficient dosing during coat or part warping)
	- Contrast Outlier (Areas that are too bright/dark compared to the average contrast)
	- Histogram Comparison (Compares the current layer to the previous layer)
    - Scan
	- Blade Streak
	- Blade Chatter
	- Scan Detection (Tries to detect the scanned area)
	- Overlay Comparison (Compares the scanned area to the part contours)
	- Histogram Comparison
- To Do
    - Coat
	- Clearly define powder holes or dosing errors
    - Scan
	- Vastly improve scan pattern detection
	- Inclusions
	- Spatter

Defect Reporting
- Currently only the following are reported and designated as a defect based on testing-based thresholds
    - Defect pixel size of Shiny Patches and Contrast Outliers
    - Number of occurences of detected blade streaks and blade chatter
    - Histogram comparison of subsequent layers (coat and scan have different thresholds)
    - Overlay template matching of scan pattern
- Possible future implementations
    - Defect propagation
    - Severity of blade streaks
- Notes
    - Combined report will report different defect coordinates from the individual part reports
    - This is because individual parts may potentially split up defects that are only partially overlapping

Slice Conversion
- Works by looking for the corresponding JSON file in the same folder as the selected part's CLS or CLI files
- If not found, the CLS or CLI files will be read, parsed and serialized as a JSON dictionary file
- If contours are to be drawn, these JSON files are read and contours for every layer are drawn

Modules
- main_window.py
- dialog_windows.py
- image_capture.py
- camera_calibration.py
- slice_converter.py
- image_processing.py
- extra_functions.py
- qt_multithreading.py
- ui_elements

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
    - filename / XXX_folder (strings that contain a file/folder name)
    - XXX_name (Strings that contain a file/folder name)
    - XXX_file (The actual open file used within with blocks, exception: config)
    - XXX_flag (Flags)
    - XXX_dialog (For dialog windows)
    - XXX_instance (For Qthread instances)
    - image_XXX (Image arrays)
- Comments will only be provided for the first time the function or block of code appears in the module, starting from the main_window module
- The entire functioning of the program requires the presence of config.json and build.json
- Almost every called function saves and loads settings and values to these files
- Do not delete these files ever, lest the program stop working entirely

How to Interpret Converted .cls Slice Files
- Layer X: Layer Height, 
- Layer X Border X: [Number of Vectors], <Length of Vectors>, Vectors (Twice as length)