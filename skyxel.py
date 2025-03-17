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
    h,w,_ = frame.shape
    print(h,w)
    frame= frame[50:h-50,50:w-50]
    return frame

# @jit(nopython=True,cache=True)
def gate_center(frame):
    # returns error between gate and the center of frame
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(frame, gate_lower_val, gate_upper_val)
    mask_ = Image.fromarray(mask)
    bbax = mask_.getbbox()
    
    if bbax is not None:
        x1,y1,x2,y2 = bbax
        cv2.rectangle(frame,[x1,y1],[x2,y2],(0,0,255),5)
        cv2.circle(frame, ((x1+x2)//2,(y1+y2)//2), 10, (0,0,255), -1)
        h,w,_ = frame.shape

        error=( (w//2)-((x1+x2)//2),(h//2)-((y1+y2)//2))
        cv2.line(frame, ((x1+x2)//2,(y1+y2)//2), ((w//2),(h//2)), (255,0,0), 2)
        # print(error)
    else:
        error = (0,0)
    return error , mask, frame

def line_lenght():
    return
def line_following():
    return 
def line_detection():
    return
def line_following():
    return