Defect Monitor
MCAM CLS Printer Software

Run main_window.py.

List of Functionality
- Take a picture of the coat and the layer (2 images)
	- Set up camera parameters
	- Done already
- Correct the image for distortions, perspective, crop, move, realign the origin
	- OpenCV


- Make sure the slice is aligned


- Check if defects overlap the part area
	- If not ignore?
	- If so error report


List of defects
Scanned Image
- Inclusions, blobs of spatter within the part contours
- Scan failures, misses
Coating Image
- Blade streaks
- Blade chatter (vertical)
- Blade damage (dark sections near the start of the blade)
- Part warping bulging into the next coat or not enough powder on the coat
- Powder holes

Ultimate goals
- Defect propagation 
- Notifications for major defects
- Report generated based off defects found 


Camera Used
Basler Ace
acA3800-10gm GigE
CMOS Sensor
10 FPS at 10 megapixels
3856 x 2764 resolution