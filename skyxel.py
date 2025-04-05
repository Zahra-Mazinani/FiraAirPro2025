# from numba import jit
from config import *
import threading
import cv2
from djitellopy import Tello
from PIL import Image
import time
import numpy as np
import os 

# def preprocess(frame):
#     frame = cv2.resize(frame,(0,0),fy=0.5,fx=0.5)
#     return frame

reference_frame = None  # برای ذخیره اولین فریم مرجع
reference_brightness = None
reference_contrast = None


def calculate_brightness_contrast(img):
    """
    Calculates the brightness and contrast of an image.

    Args:
        img (numpy.ndarray): The input image.

    Returns:
        tuple: Brightness (mean) and contrast (standard deviation).
    """
    """محاسبه روشنایی (میانگین) و کنتراست (انحراف معیار)"""  
    brightness = np.mean(img)
    contrast = np.std(img)
    return brightness, contrast


def adjust_image(img, brightness_factor, contrast_factor):
    """
    Adjusts the brightness and contrast of an image.

    Args:
        img (numpy.ndarray): The input image.
        brightness_factor (float): The brightness adjustment factor.
        contrast_factor (float): The contrast adjustment factor.

    Returns:
        numpy.ndarray: The adjusted image.
    """
    """تنظیم روشنایی و کنتراست تصویر با استفاده از فاکتورهای محاسبه شده"""
    img = cv2.convertScaleAbs(img, alpha=contrast_factor, beta=brightness_factor)
    return img


def filter_color(img, lower_bound, upper_bound):
    """
    Filters colors in the YCrCb color space.

    Args:
        ycrcb_img (numpy.ndarray): The input image in YCrCb color space.
        lower_bound_ycrcb (tuple): The lower bound for color filtering.
        upper_bound_ycrcb (tuple): The upper bound for color filtering.

    Returns:
        numpy.ndarray: The binary mask after color filtering.
    """
    """فیلتر رنگ در فضای YCrCb و خروجی به صورت ماسک باینری"""
    mask = cv2.inRange(img, lower_bound, upper_bound)
    return mask


def preprocess(frame):
    """
    Preprocesses the input frame by resizing, adjusting brightness/contrast, and filtering colors.

    Args:
        frame (numpy.ndarray): The input image frame.

    Returns:
        tuple: The preprocessed frame and the binary mask.
    """
    global reference_frame, reference_brightness, reference_contrast

    frame = cv2.resize(frame, (0, 0), fy=0.5, fx=0.5)

    ycrcb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
    ycrcb_img = cv2.GaussianBlur(ycrcb_img, (7, 7), 1)

    if reference_frame is None:
        # ذخیره اولین فریم به‌عنوان مرجع
        reference_frame = ycrcb_img
        reference_brightness, reference_contrast = calculate_brightness_contrast(reference_frame)

    current_brightness, current_contrast = calculate_brightness_contrast(ycrcb_img)
    brightness_factor = reference_brightness - current_brightness
    contrast_factor = reference_contrast / current_contrast if current_contrast > 0 else 1.0

    # تنظیم تصویر به حالت مشابه فریم مرجع
    adjusted_img = adjust_image(frame, brightness_factor, contrast_factor)
    adjusted_ycrcb = cv2.cvtColor(adjusted_img, cv2.COLOR_BGR2YCrCb)

    # فیلتر کردن رنگ و خروجی ماسک باینری
    gate_lower_val = np.array(gate_lower)
    gate_upper_val = np.array(gate_upper)
    mask = filter_color(adjusted_ycrcb, gate_lower_val, gate_upper_val)

    return frame,mask


# @jit(nopython=True,cache=True)
# returns error between gate and the center of frame
def gate_center(frame , mask):
    """
    Finds the center of the gate in the frame and calculates the error relative to the frame center.

    Args:
        frame (numpy.ndarray): The input image frame.
        mask (numpy.ndarray): The binary mask of the gate.

    Returns:
        tuple: The error (x, y) and the updated frame with visualizations.
    """
    mask_ = Image.fromarray(mask)
    bbax = mask_.getbbox()
    
    if bbax is not None:
        x1,y1,x2,y2 = bbax
        cv2.rectangle(frame,[x1,y1],[x2,y2],(0,0,255),5)
        cv2.circle(frame, ((x1+x2)//2,(y1+y2)//2), 10, (0,0,255), -1)
        h,w,_ = frame.shape

        error = ((w//2)-((x1+x2)//2),(h//2)-((y1+y2)//2))
        cv2.line(frame, ((x1+x2)//2,(y1+y2)//2), ((w//2),(h//2)), (255,0,0), 2)
        # print(error)
    else:
        error = (0,0)
    return error , frame

def gate_center_overlab(frame,mask):
    """
    Finds the center of the gate using connected components and calculates the error.

    Args:
        frame (numpy.ndarray): The input image frame.
        mask (numpy.ndarray): The binary mask of the gate.

    Returns:
        tuple: The error (x, y) and the updated frame with visualizations.
    """
    height , width, _ =frame.shape
    label, lbl_img, stats, centroids = cv2.connectedComponentsWithStats(mask)
    if len(stats) > 1:  # چک کردن اینکه آیا حداقل یک جسم پیدا شده
        # پیدا کردن بزرگترین مساحت به جز پس‌زمینه (index 0)
        largest_index = np.argmax(stats[1:, cv2.CC_STAT_AREA]) + 1

        # گرفتن اطلاعات بزرگترین جسم
        x, y, w, h, area = stats[largest_index]
        # cx, cy = centroids[largest_index]
        cx = x+w//2
        cy = y+h//2
        # رسم مستطیل و مرکز
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
        cv2.circle(frame, (int(cx), int(cy)), 5, (0, 0, 255), -1)
        error = ((width//2)-(cx),(height//2)-(cy))
        print(f"center: ({int(cx)}, {int(cy)})")
    else:
        error = (0,0)
        print("no gate")
    return error, frame


# line following functions
def thresholding(img):
    """
    Thresholding the image to create a binary mask.

    Args:
        img (numpy.ndarray): The input image.
    
    Returns:
        mask (numpy.ndarray): The binary mask after thresholding.
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    line_lower_val = np.array(line_lower)
    line_upper_val = np.array(line_upper)
    mask = cv2.inRange(hsv, line_lower_val, line_upper_val)
    return mask

def getContours(imgThres, img):
    """
    Finds the contours in the thresholded image and draws them on the original image.
    
    Args:
        imgThres (numpy.ndarray): The thresholded image.
        img (numpy.ndarray): The original image.   
    
    Returns:
        cx (int): The x-coordinate of the center of the largest contour.
    """
    cx = 0
    contours, hieracrhy = cv2.findContours(imgThres, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if len(contours) != 0:
        biggest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(biggest)
        cx = x + w // 2
        cy = y + h // 2
        cv2.drawContours(img, biggest, -1, (255, 0, 255), 7)
        cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
    return cx

def getSensorOutput(frame,imgThres, sensors):
    """
    Splits the thresholded image into sections and counts the number of white pixels in each section.
    
    Args:
        frame (numpy.ndarray): The input image frame.
        imgThres (numpy.ndarray): The thresholded image.
        sensors (int): The number of sensors.
    
    Returns:
        senOut (list): A list containing the sensor outputs (1 or 0).
    """
    imgs = np.hsplit(imgThres, sensors)
    totalPixels = (frame.shape[1] // sensors) * frame.shape[0]
    senOut = []
    for x, im in enumerate(imgs):
        pixelCount = cv2.countNonZero(im)
        if pixelCount > threshold * totalPixels:
            senOut.append(1)
        else:
            senOut.append(0)
        # cv2.imshow(str(x), im)
    # print(senOut)
    return senOut


class PID_Controller:
    """
    A simple PID controller class.
    
    Arguments:
        kp (float): Proportional gain.
        ki (float): Integral gain.
        kd (float): Derivative gain.    
    Returns:
        change (float): The control output.
    """
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0
    def controller(self,error):
        p = error * self.kp
        d = (error - self.prev_error) * self.kd
        self.integral += error
        self.prev_error = error
        return p + d + self.integral * self.ki
    
# @jit(nopython=True,cache=True)
def H_detection(frame):
    """
    Detects the letter 'H' in the given frame.

    Args:
        frame (numpy.ndarray): The input image frame.

    Returns:
        tuple: A boolean indicating if 'H' was found and the bounding box (x, y, w, h).
    """
    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to get a binary image
    _, binary = cv2.threshold(gray, 100, 200, cv2.THRESH_BINARY_INV)

    # Find contours in the binary image
    contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    found_H = False
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 10 and h > 10:  # Filter small contours
            roi = gray[y:y+h, x:x+w]
            roi = cv2.resize(roi, (50, 50))  # Resize ROI to match template size
            roi= np.bitwise_not(roi)
            res = cv2.matchTemplate(roi, H_template, cv2.TM_CCOEFF_NORMED)
            if res >= 0.46:  # Adjust the threshold as needed
                found_H = True
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, "Found 'H'!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                break
    if not found_H:
        cv2.putText(frame, "'H' not found", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        x,y,w,h = 0,0,0,0
    return found_H , (x,y,w,h)

def keyboard_control(drone,key):
    """
    Controls the drone using keyboard input.

    Args:
        drone (object): The drone object to control.
        key (int): The ASCII value of the pressed key.

    Returns:
        None
    """
    if key == ord('w'):
        print("forward")
        drone.move_forward(30)
    
    elif key == ord('s'):
        print("back")
        drone.move_back(30)
        
    elif key == ord('a'):
        print("left")
        drone.move_left(30)
        
    elif key == ord('d'):
        print("right")
        drone.move_right(30)
        
    elif key == ord('e'):
        print("up")
        drone.move_up(30)

    elif key == ord('q'):
        print("down")
        drone.move_down(30)
        
    elif key == ord('t'):
        print("takeoff")
        drone.takeoff()
        
    elif key == ord('l'):
        drone.land()
        print("land")
        
    # elif key == ord('x'):
    #     stop_flag.set()
