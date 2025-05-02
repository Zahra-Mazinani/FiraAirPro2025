# from numba import jit
import threading
import cv2
from djitellopy import Tello
from PIL import Image
import time
import numpy as np
import os 

global error
previos_error_x = 0
integral_x=0
previos_error_y = 0
integral_y=0
error = None

Kp=0.077
kp_resize = 0.1546

# HSV
# gate_lower_val = np.array([110,170,87])
# gate_upper_val = np.array([163,255,255])

# line_lower_val = np.array([82,62,66])
# line_upper_val = np.array([180,255,255])

# orange_lower_val = np.array([0,120,149])
# orange_upper_val = np.array([114,255,255])

# purple_lower_val = np.array([168,56,62])
# purple_upper_val = np.array([180,111,219])

# LAB
gate_lower_val = np.array([49,85,135])
gate_upper_val = np.array([139,141,165])

line_lower_val = np.array([])
line_upper_val = np.array([])

orange_lower_val = np.array([71,94,61])
orange_upper_val = np.array([106,161,88])

purple_lower_val = np.array([141,146,109])
purple_upper_val = np.array([205,196,255])

H_template = cv2.imread('H.png',0)
# H_template = cv2.resize(H_template, (50, 50))  # Resize ROI to match template size

threshold_x = 8 # 8 #cm
threshold_y = 8 # 8 #cm
