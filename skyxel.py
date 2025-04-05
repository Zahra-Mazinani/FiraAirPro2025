from config import *

def pid_controller_x(error, kp, kd,ki ):
    """
    PID controller for the X-axis.

    Args:
        error (float): The error value for the X-axis.
        kp (float): Proportional gain.
        kd (float): Derivative gain.
        ki (float): Integral gain.

    Returns:
        float: The control output for the X-axis.
    """
  
    global previos_error_x , integral_x
    p = error* kp
    d = (error-previos_error_x)*kd
    integral_x += error 
    previos_error_x = error
    return p + d + integral_x*ki


def pid_controller_y(error, kp, kd,ki):
    """
    PID controller for the Y-axis.

    Args:
        error (float): The error value for the Y-axis.
        kp (float): Proportional gain.
        kd (float): Derivative gain.
        ki (float): Integral gain.

    Returns:
        float: The control output for the Y-axis.
    """
    
    global previos_error_y , integral_y
    p = error* kp
    d = (error-previos_error_y)*kd
    integral_y += error 
    previos_error_y = error
    return p + d + integral_y*ki

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

def keyboard_control(key):
    """
    Controls the drone using keyboard input.

    Args:
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


def filter_color_ycrcb(ycrcb_img, lower_bound_ycrcb, upper_bound_ycrcb):
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
    mask = cv2.inRange(ycrcb_img, lower_bound_ycrcb, upper_bound_ycrcb)
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
    mask = filter_color_ycrcb(adjusted_ycrcb, gate_lower_val, gate_upper_val)

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
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",len(stats))
        print(f"center: ({int(cx)}, {int(cy)})")
    else:
        error = (0,0)
        print("no gate")
    return error, frame

