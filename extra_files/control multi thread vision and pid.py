from config import *
from skyxel import *

# Initialize the Tello drone
drone.connect()
print(f"Battery: {drone.get_battery()}%")

# Shared flag to terminate threads
stop_flag = threading.Event()
def control(error):
    x = error[0]
    y = error[1]
    error_x = pid_controller_x(x,0.5,0,0)
    error_y = pid_controller_y(y,0.5,0,0)
    if error_x >0 :
        right = int(np.clip(abs(error_x), 20, 100))
        # drone.move_right(right)
        print("x : ",x, "pid :",error_x , "right",end =" ")
        
    else:
        left = int(np.clip(abs(error_x), 20, 100))
        # drone.move_left(left)
        print("x : ",x, "pid :",error_x, "left",end=" ")
        
    if error_y >0 :
        up = int(np.clip(abs(error_y), 20, 100))
        # drone.move_up(up)    
        print("y : ",y, "pid :",error_y, "up")
        
    else:
        down = int(np.clip(abs(error_y), 20, 100))
        # drone.move_down(down)
        print("y : ",y, "pid :",error_y, "down")
        # keyboard(key)

def stream_camera():
    drone.streamon()
    time.sleep(2)
    while not stop_flag.is_set():
        frame = drone.get_frame_read().frame
        found_H , (x,y,w,h) = H_detection(frame)

        error,mask,frame = gate_center(frame)
        print(x,y,w,h)
        cv2.imshow("mask",mask)
        cv2.imshow("frame", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # If a key is pressed
            drone.land()
            break
        control(error)
# Start the camera thread
camera_thread = threading.Thread(target=stream_camera)
camera_thread.start()

# Wait for the thread to finish
camera_thread.join()

# Safely disconnect the drone
drone.end()