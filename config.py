# from numba import jit
import threading
import cv2
from djitellopy import Tello
from PIL import Image
import time
import numpy as np
import os 
from skimage.exposure import match_histograms


global error
previos_error_x = 0
integral_x=0
previos_error_y = 0
integral_y=0
error = None

# gate_lower_val = np.array([110,170,87])
# gate_upper_val = np.array([163,255,255])
gate_lower_val = np.array([0,0,180])
gate_upper_val = np.array([109,167,255])

line_lower_val = np.array([82,62,66])
line_upper_val = np.array([180,255,255])

drone = Tello()

H_template = cv2.imread('H.png',0)
H_template = cv2.resize(H_template, (50, 50))  # Resize ROI to match template size

sample_pixels_coords = [(20,20), (180,130), (180, 20), (130,20)] # می توانید این مختصات را تغییر دهید


threshold_x = 8 #cm
threshold_y = 8 #cm

