from config import *

def pid_controller_x(error, kp, kd,ki ):
    global previos_error_x , integral_x
    p = error* kp
    d = (error-previos_error_x)*kd
    integral_x += error 
    previos_error_x = error
    return p + d + integral_x*ki


def pid_controller_y(error, kp, kd,ki):
    global previos_error_y , integral_y
    p = error* kp
    d = (error-previos_error_y)*kd
    integral_y += error 
    previos_error_y = error
    return p + d + integral_y*ki

# @jit(nopython=True,cache=True)
def H_detection(frame):
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

def preprocess(frame):
    frame = cv2.resize(frame,(0,0),fy=0.5,fx=0.5)
    return frame

# @jit(nopython=True,cache=True)
def gate_center(frame):
    # returns error between gate and the center of frame
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    mask = cv2.inRange(frame, gate_lower_val, gate_upper_val)
    # عملیات مورفولوژیکی برای حذف نویزها
    kernel = np.ones((7, 7), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    label, lbl_img, stats, centroids = cv2.connectedComponentsWithStats(mask)
    error = None
    if len(stats) > 1:  # چک کردن اینکه آیا حداقل یک جسم پیدا شده
        # پیدا کردن بزرگترین مساحت به جز پس‌زمینه (index 0)
        largest_index = np.argmax(stats[1:, cv2.CC_STAT_AREA]) + 1

        # گرفتن اطلاعات بزرگترین جسم
        x, y, w, h, area = stats[largest_index]
        # cx, cy = centroids[largest_index]
        cx = x+w//2
        cy = y+h//2
        frame_center = (frame.shape[1] // 2, frame.shape[0] // 2)
        error = (cx - frame_center[0], cy - frame_center[1])
        # رسم مستطیل و مرکز
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
        cv2.circle(frame, (int(cx), int(cy)), 5, (0, 0, 255), -1)
        print(f"center: ({int(cx)}, {int(cy)})")
    else:
        print("no gate")
        
    return error , mask, frame

# def Command(left_right=0,forward_backward=0,updown=0,yaw=0,duration=0.5):
#     prev_time = time.time()
#     while time.time() - prev_time < duration:
#         drone.send_rc_control(left_right,forward_backward,updown,yaw)
#         drone.send_rc_control(0,0,0,0)
         
# def horizontal_gates(frame):
#     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#     mask = cv2.inRange(frame, gate_lower_val, gate_upper_val)



# line_follower

def thresholding_line(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    mask = cv2.inRange(hsv, line_lower_val, line_upper_val)
    return mask

def getContours_line(imgThres, img):
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
    imgs = np.hsplit(imgThres, sensors)
    totalPixels = (frame.shape[1] // sensors) * frame.shape[0]
    senOut = []
    for x, im in enumerate(imgs):
        pixelCount = cv2.countNonZero(im)
        if pixelCount > threshold_line * totalPixels:
            senOut.append(1)
        else:
            senOut.append(0)
        # cv2.imshow(str(x), im)
    # print(senOut)
    return senOut



