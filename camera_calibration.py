"""
camera_calibration.py
Module used to calibrate the camera.
If no camera found, uses predefined camera intrinsics for later OpenCV functions.
"""

# Import built-ins
import os

# Import external modules
import cv2
import numpy as np

class Calibration:
    def __init__(self):
        pass