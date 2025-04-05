# from numba import jit
import threading
import cv2
from djitellopy import Tello
from PIL import Image
import time
import numpy as np
import os 

# gate variables
gate_lower_val = np.array([0,0,180])
gate_upper_val = np.array([109,167,255])
threshold_x = 8 #cm
threshold_y = 8 #cm

# H_detection variables
H_template = cv2.imread('D:\\fira_air_2025\\codes\\H.png',0)
H_template = cv2.resize(H_template, (50, 50))  # Resize ROI to match template size


# automate color filtering 
sample_pixels_coords = [(20,20), (180,130), (180, 20), (130,20)] # می توانید این مختصات را تغییر دهید

# line_follower variables
sensors = 3
threshold = 0.2
width, height = 480, 360
senstivity = 3  # if number is high less sensitive
weights = [-25, -15, 0, 15, 25]
fSpeed = 15
curve = 0
line_lower_val = np.array([82,62,66])
line_upper_val = np.array([180,255,255])
