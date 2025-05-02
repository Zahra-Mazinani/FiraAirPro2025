from config import *
from skyxel import *
import threading

# Initialize the Tello drone
drone = Tello()
drone.connect()
print("Battery : ",drone.get_battery())

drone.takeoff()
time.sleep(1)
drone.move_up(50)

# Shared flag to terminate threads
stop_flag = threading.Event()

# متغیر اشتراکی برای ذخیره آخرین مقدار ارور
latest_error = None
error_lock = threading.Lock()

def stream_camera():
    """این تابع فریم را دریافت کرده و آخرین ارور را به‌روز می‌کند."""
    global latest_error

    drone.streamon()
    time.sleep(2)
    n = 0
    while not stop_flag.is_set():
        n+=1
        if n%5==1:
            # get frame
            frame = drone.get_frame_read().frame

            # H detection
            # found_H, (x, y, w, h) = H_detection(frame)
            
            # frame preproccesing
            frame = preprocess(frame)

            # find center of gate
            error, mask, frame = gate_center(frame)
            # print(x, y, w, h)

            cv2.imshow("mask", mask)
            cv2.imshow("frame", frame)

            # ذخیره آخرین مقدار ارور
            with error_lock:
                latest_error = error

            if  cv2.waitKey(1) & 0xFF == 27:  # If ESC key is pressed
                stop_flag.set()
                drone.land()
                break

def control(error):
    # os.system('cls')
    global counter_gates
    
    error_x = error[0]*kp_resize
    error_y = error[1]*- kp_resize
    error_x = int(np.clip(error_x,-100,100))
    error_y = int(np.clip(error_y,-100,100))
    print("=====================================================")
    print("=====================================================")
    print("=====================================================")

    '''
    left_right_velocity: -100~100 (left/right)
    forward_backward_velocity: -100~100 (backward/forward)
    up_down_velocity: -100~100 (down/up)
    yaw_velocity: -100~100 (yaw)
    '''
 
    if abs(error_x) < threshold_x and abs(error_y)<threshold_y :
        print("jellllllllllllllooooooooooooooooooooooooooooooo")
        # input()
        prev_time = time.time()
        while time.time() - prev_time < 0.5:
            drone.send_rc_control(0,45,0,0)
        drone.send_rc_control(0,0,0,0)

        prev_time = time.time()
        while time.time() - prev_time < 0.2:
            drone.send_rc_control(0, 0, 20, 0)
            
        # prev_time = time.time()
        # while time.time() - prev_time < 0.2:
        #     drone.send_rc_control(0, 0, 0, 20)


        # drone.send_rc_control(0,40,0,0)
        # time.sleep(0.5)
        # drone.send_rc_control(0,0,0,0)

        # drone.send_rc_control(0, 0, 20, 0)
        # time.sleep(0.2)
        # drone.send_rc_control(0,0,0,0)

        # drone.send_rc_control(0, 0, 0, 20)
        # time.sleep(0.2)
        # drone.send_rc_control(0,0,0,0)

    else:
        print(error_x,error_y)
        drone.send_rc_control(error_x,10,error_y,0)

    print("=====================================================")
    print("=====================================================")
    print("=====================================================")

def control_loop():
    """این تابع ارور را خوانده و تابع کنترلر را اجرا می‌کند."""
    global latest_error

    while not stop_flag.is_set():
        with error_lock:
            if latest_error is not None:
                control(latest_error)

        time.sleep(0.05)  # تأخیر کوتاه برای جلوگیری از پردازش بی‌وقفه

# Start the camera and controller threads
camera_thread = threading.Thread(target=stream_camera, daemon=True)
control_thread = threading.Thread(target=control_loop, daemon=True)

camera_thread.start()
control_thread.start()

# Main loop to keep the program running
try:

    print(f"Battery: {drone.get_battery()}%")

    while True: 
        if cv2.waitKey(1) & 0xFF == 27:  # ESC key pressed
            print("Landing and stopping the program...")
            stop_flag.set()
            drone.land()
            break
except KeyboardInterrupt:
    print("Interrupted! Landing the drone...")
    stop_flag.set()
    drone.land()
    
# Wait for threads to finish
camera_thread.join()
control_thread.join()

drone.land()

# Safely disconnect the drone
drone.end()